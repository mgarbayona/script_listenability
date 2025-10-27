#!/usr/bin/env bash

TRANSCRIPTS_DIR="$1"

grep -r [0-9] "${TRANSCRIPTS_DIR}" \
  | cut -d ":" -f 2- \
  | tr " " "\n" \
  | sed -e :a -e '$!N;s/\n\([bm]illion\)/ \1/;ta' -e 'P;D' \
  | grep [0-9] \
  | sed -e 's#[.,]$##g' \
  | sed -e "s#[“”()]##g" \
  | sort | uniq > "${TRANSCRIPTS_DIR}/num_tokens.list"

echo "Numerical tokens stored in ${TRANSCRIPTS_DIR}/num_tokens.list."
