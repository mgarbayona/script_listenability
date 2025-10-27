#!/usr/bin/env bash

stage=0
DATA_NAME="voa"
DATA_DIR="data/${DATA_NAME}"
SET_NAME="le-begin"

OLD_LOCAL_DIR="data/local"
OLD_LEX_DIR="${OLD_LOCAL_DIR}/dict"
OLD_LM_DIR="${OLD_LOCAL_DIR}/lm"

NEW_LOCAL_DIR="${DATA_DIR}/${SET_NAME}/local"
NEW_LOCAL_LEX_DIR="${NEW_LOCAL_DIR}/dict"
NEW_LOCAL_LM_DIR="${NEW_LOCAL_DIR}/lang"

# Set the paths of our input files into variables
MODEL_DIR="exp/tdnn_7b_chain_online"
PHONES_SRC="exp/tdnn_7b_chain_online/phones.txt"
NEW_LM="${NEW_LOCAL_LM_DIR}/merged-lm"

NEW_LEX_DIR="${DATA_DIR}/${SET_NAME}/dict"
NEW_LANG_DIR="${DATA_DIR}/${SET_NAME}/lang"
NEW_LEX_TMP_DIR="${DATA_DIR}/${SET_NAME}/dict_tmp"
NEW_GRAPH_DIR="${DATA_DIR}/${SET_NAME}/graph"

mkdir -p "${NEW_LOCAL_DIR}"
mkdir -p "${NEW_LOCAL_LEX_DIR}"
mkdir -p "${NEW_LOCAL_LM_DIR}"
mkdir -p "${NEW_LANG_DIR}"
mkdir -p "${NEW_LEX_DIR}"

. ./cmd.sh
. ./path.sh
. utils/parse_options.sh  # e.g. this parses the --stage option if supplied.

##DATA PREPARATION
if [ "${stage}" -le 1 ]; then
  # Create files needed by Kaldi
  "local/prepare_${DATA_NAME}_${SET_NAME}.sh" || exit 1;
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
# if [ "${stage}" -le 2 ]; then
#   # Run the speech recognizer and generate the lattices
#   online2-wav-nnet3-latgen-faster \
#     --online=false \
#     --do-endpointing=false \
#     --frame-subsampling-factor=3 \
#     --config=exp/tdnn_7b_chain_online/conf/online.conf \
#     --max-active=7000 \
#     --beam=15.0 \
#     --lattice-beam=6.0 \
#     --acoustic-scale=1.0 \
#     --word-symbol-table=exp/tdnn_7b_chain_online/graph_pp/words.txt \
#     exp/tdnn_7b_chain_online/final.mdl \
#     exp/tdnn_7b_chain_online/graph_pp/HCLG.fst \
#     "ark:${DATA_DIR}/${SET_NAME}/spk2utt" \
#     "scp:${DATA_DIR}/${SET_NAME}/wav.scp" \
#     "ark,t:exp/${DATA_NAME}/${SET_NAME}/lattices.ark" || exit 1;
# fi

##
if [ "${stage}" -le 3 ]; then
  cp "${OLD_LEX_DIR}/extra_questions.txt" "${NEW_LOCAL_LEX_DIR}"
  cp "${OLD_LEX_DIR}/nonsilence_phones.txt" "${NEW_LOCAL_LEX_DIR}"
  cp "${OLD_LEX_DIR}/optional_silence.txt" "${NEW_LOCAL_LEX_DIR}"
  cp "${OLD_LEX_DIR}/silence_phones.txt" "${NEW_LOCAL_LEX_DIR}"

  # Decompress 3gram-mincount/lm_unpruned from original model
  # New lexicon and language model to be added generated from Sphinx's
  #   Knowledge-Based Tool (http://www.speech.cs.cmu.edu/tools/lmtool-new.html)
  # Tested on python 3.8
  python local/mergedicts.py \
    "${OLD_LEX_DIR}/lexicon4_extra.txt" \
    "${OLD_LM_DIR}/3gram-mincount/lm_unpruned" \
    "${DATA_DIR}/${SET_NAME}/skbt-files/${DATA_NAME}_${SET_NAME}.dic" \
    "${DATA_DIR}/${SET_NAME}/skbt-files/${DATA_NAME}_${SET_NAME}.lm" \
    "${NEW_LOCAL_LEX_DIR}/lexicon.txt" \
    "${NEW_LOCAL_LM_DIR}/merged-lm"
fi

if [ "${stage}" -le 4 ]; then
  #
  # Compile the word lexicon (L.fst)
  utils/prepare_lang.sh \
    --phone-symbol-table "${PHONES_SRC}" \
    "${NEW_LOCAL_LEX_DIR}" "" "${NEW_LEX_TMP_DIR}" "${NEW_LEX_DIR}"

  # Compile the grammar/language model (G.fst)
  gzip "${NEW_LM}"
  utils/format_lm.sh \
    "${NEW_LEX_DIR}" \
    "${NEW_LM}.gz" \
    "${NEW_LOCAL_LEX_DIR}/lexicon.txt" \
    "${NEW_LANG_DIR}"

  # Finally assemble the HCLG graph
  utils/mkgraph.sh \
    --self-loop-scale 1.0 \
    "${NEW_LANG_DIR}" \
    "${MODEL_DIR}" \
    "${NEW_GRAPH_DIR}"
fi

if [ "${stage}" -le 5 ]; then
  # To use our newly created model, we must also build a decoding configuration,
  # the following line will create these for us into the new/conf directory
  steps/online/nnet3/prepare_online_decoding.sh \
    --mfcc-config conf/mfcc_hires.conf \
    "${NEW_LEX_DIR}" \
    "exp/nnet3/extractor" \
    "exp/chain/tdnn_7b" \
    "${DATA_DIR}/${SET_NAME}"

  mkdir -p "exp/${DATA_NAME}/${SET_NAME}-biased"
  # mkdir -p "exp/${DATA_NAME}/${SET_NAME}-biased/recog_logs"

  # Run the speech recognizer and generate the lattices
  online2-wav-nnet3-latgen-faster \
    --online=false \
    --do-endpointing=false \
    --frame-subsampling-factor=3 \
    --config="${DATA_DIR}/${SET_NAME}/conf/online.conf" \
    --max-active=7000 \
    --beam=15.0 \
    --lattice-beam=6.0 \
    --acoustic-scale=1.0 \
    --word-symbol-table="${DATA_DIR}/${SET_NAME}/graph/words.txt" \
    exp/tdnn_7b_chain_online/final.mdl \
    "${DATA_DIR}/${SET_NAME}/graph/HCLG.fst" \
    "ark:${DATA_DIR}/${SET_NAME}/spk2utt" \
    "scp:${DATA_DIR}/${SET_NAME}/wav.scp" \
    "ark:|lattice-scale --acoustic-scale=0.5 ark:- ark:- | gzip -c \
      > exp/${DATA_NAME}/${SET_NAME}-biased/lat.1.gz" \
    > "exp/${DATA_NAME}/${SET_NAME}-biased/recog_logs" 2>&1
fi

if [ "${stage}" -le 6 ]; then
  python local/extract_likelihood_per_frame.py \
    "exp/${DATA_NAME}/${SET_NAME}-biased/recog_logs" \
    "exp/${DATA_NAME}/${SET_NAME}-biased/lpf.txt"

  # create time alignment
  # also acount for frame sub-sampling
  # --frame-shift=0.03
  lattice-align-words-lexicon  \
    "${DATA_DIR}/${SET_NAME}/lang/phones/align_lexicon.int" \
    exp/tdnn_7b_chain_online/final.mdl \
    "ark:gunzip -c exp/${DATA_NAME}/${SET_NAME}-biased/lat.1.gz|" \
    ark:- | lattice-1best ark:- ark:- \
    | nbest-to-ctm --frame-shift=0.03 \
    ark:- "exp/${DATA_NAME}/${SET_NAME}-biased/align.ctm"

  python local/convert_ctm.py \
    -i "exp/${DATA_NAME}/${SET_NAME}-biased/align.ctm" \
    -w "${DATA_DIR}/${SET_NAME}/lang/words.txt" \
    -o "exp/${DATA_NAME}/${SET_NAME}-biased/out.ctm"

fi

if [ "${stage}" -le 7 ]; then
  echo "Isolating body of recording..."
  ./local/remove_voa_news_words_intro.sh \
    "exp/${DATA_NAME}/${SET_NAME}-biased/out.ctm" \
    "${DATA_DIR}/${SET_NAME}/wav.scp"
  echo "Done."
fi
