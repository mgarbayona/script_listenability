#!/usr/bin/env bash

REF_FILE=""
HYP_FILE=""

. ./cmd.sh
. ./path.sh

compute-wer \
  --mode=all \
  "ark:${REF_FILE}" \
  "ark:${HYP_FILE}"

compute-wer \
  --mode=present \
  "ark:${REF_FILE}" \
  "ark:${HYP_FILE}"
