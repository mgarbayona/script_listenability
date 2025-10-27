#!/usr/bin/env bash

stage=0
DATA_NAME="voa"
DATA_DIR="data/${DATA_NAME}"
SET_DIR="le-chunks"

. ./cmd.sh
. ./path.sh
. utils/parse_options.sh  # e.g. this parses the --stage option if supplied.

mkdir -p "exp/${DATA_NAME}"
mkdir -p "exp/${DATA_NAME}/${SET_DIR}"

##DATA PREPARATION
if [ "${stage}" -le 1 ]; then
  # Create files needed by Kaldi
  "local/prepare_${DATA_NAME}-${SET_DIR}.sh" || exit 1;
fi

if [ "${stage}" -le 2 ]; then
  steps/online/nnet3/prepare_online_decoding.sh \
    --mfcc-config conf/mfcc_hires.conf \
    data/lang_chain \
    exp/nnet3/extractor \
    exp/chain/tdnn_7b \
    exp/tdnn_7b_chain_online || exit 1;

  utils/mkgraph.sh \
    --self-loop-scale 1.0 \
    data/lang_pp_test \
    exp/tdnn_7b_chain_online \
    exp/tdnn_7b_chain_online/graph_pp || exit 1;
fi

##SPEECH RECOGNITION - OFFLINE BATCH PROCESSING
if [ "${stage}" -le 3 ]; then
  # Run the speech recognizer and generate the lattices
  online2-wav-nnet3-latgen-faster \
    --online=false \
    --do-endpointing=false \
    --frame-subsampling-factor=3 \
    --config=exp/tdnn_7b_chain_online/conf/online.conf \
    --max-active=7000 \
    --beam=15.0 \
    --lattice-beam=6.0 \
    --acoustic-scale=1.0 \
    --word-symbol-table=exp/tdnn_7b_chain_online/graph_pp/words.txt \
    exp/tdnn_7b_chain_online/final.mdl \
    exp/tdnn_7b_chain_online/graph_pp/HCLG.fst \
    "ark:${DATA_DIR}/${SET_DIR}/spk2utt" \
    "ark,s,cs:extract-segments scp,p:${DATA_DIR}/${SET_DIR}/wav.scp ${DATA_DIR}/${SET_DIR}/segments ark:- |" \
    "ark,t:exp/${DATA_NAME}/${SET_DIR}/lattices.ark";
fi

if [ "${stage}" -le 4 ]; then
  # Get the best hypothesis from each lattice. Note that the word sequence will
  # still be encoded based on the word-symbol table.
  lattice-best-path \
    --word-symbol-table=exp/tdnn_7b_chain_online/graph_pp/words.txt \
    "ark:exp/${DATA_NAME}/${SET_DIR}/lattices.ark" \
    "ark,t:exp/${DATA_NAME}/${SET_DIR}/one-best_symbols.txt" || exit 1;

  utils/int2sym.pl -f 2- \
    "exp/tdnn_7b_chain_online/graph_pp/words.txt" \
    "exp/${DATA_NAME}/${SET_DIR}/one-best_symbols.txt" \
      > "exp/${DATA_NAME}/${SET_DIR}/one-best_words.txt" || exit 1;
fi

##WORD-ERROR RATE CALCULATION
if [ "${stage}" -le 5 ]; then
  # Note that Kaldi's compute-wer function operates in a case-sensitive way
  cut -d " " -f 1 "exp/${DATA_NAME}/${SET_DIR}/one-best_words.txt" \
    > "utt_ids.tmp"
  cut -d " " -f 2- "exp/${DATA_NAME}/${SET_DIR}/one-best_words.txt" \
    | tr "[a-z]" "[A-Z]" > "hyps.tmp"
  paste -d " " "utt_ids.tmp" "hyps.tmp" \
    > "exp/${DATA_NAME}/${SET_DIR}/one-best_words-caps.txt"

  # Delete temporary files created
  rm -f "utt_ids.tmp"
  rm -f "hyps.tmp"

  rm -f "exp/${DATA_NAME}/${SET_DIR}/one-best_words-caps-read.txt"
  rm -f "exp/${DATA_NAME}/${SET_DIR}/one-best_words-caps-asr.txt"

  cat "${DATA_DIR}/${SET_DIR}/segments" \
    | cut -d " " -f 2 \
    | sort | uniq | while read utt_id; do
      transcript=`grep "^${utt_id}" "exp/${DATA_NAME}/${SET_DIR}/one-best_words-caps.txt" \
        | cut -d ' ' -f 2- \
        | tr '\n' '.' \
        | sed -e "s#\.#. #g" \
        | sed -e "s# \.#.#g" \
        | sed -e "s#_##g" \
        | tr -s " "`
      echo "${utt_id} ${transcript}" \
        >> "exp/${DATA_NAME}/${SET_DIR}/one-best_words-caps-read.txt"
    done

  cat "exp/${DATA_NAME}/${SET_DIR}/one-best_words-caps-read.txt" \
    | sed -e "s#\. # #g" \
    > "exp/${DATA_NAME}/${SET_DIR}/one-best_words-caps-asr.txt"

  compute-wer \
    "ark:${DATA_DIR}/${SET_DIR}/text-whole" \
    "ark:exp/${DATA_NAME}/${SET_DIR}/one-best_words-caps-asr.txt" || exit 1;

  unk_count=`cat "exp/${DATA_NAME}/${SET_DIR}/one-best_words-caps-asr.txt" \
    | sed -e "s#<UNK>#\n<UNK>\n#g" | grep "<UNK>" | wc -l`
  echo "<UNK> count: ${unk_count}"
fi
