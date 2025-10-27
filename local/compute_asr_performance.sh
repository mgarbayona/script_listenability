#!/usr/bin/env bash

MAIN_DIR="data/voa/processed/asr/kaldi-aspire-s5"
REFS_DIR="${MAIN_DIR}/refs"
HYPS_DIR="${MAIN_DIR}/hyps"
OUT_FILE="${MAIN_DIR}/texterrors_kaldi-aspire-s5.csv"

rm -f "${OUT_FILE}"

echo "utt_file,wer,ins,del,sub,words,ser" >> "${OUT_FILE}"

ls "${REFS_DIR}" | grep ".txt" | sort | uniq | while read ref_file; do
  ref_path="${REFS_DIR}/${ref_file}"
  hyp_path="${HYPS_DIR}/${ref_file}"

  utt_stats=`texterrors -s -use-chardiff "${ref_path}" "${hyp_path}" \
    | tr "\n" " " \
    | grep -Eo '[0-9]+\.*[0-9]*' \
    | tr "\n" "," \
    | sed '$s/,$/\n/'`

  echo "${ref_file},${utt_stats}" >> "${OUT_FILE}"
done
