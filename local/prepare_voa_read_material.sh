#!/usr/bin/env bash

TRANSCRIPT_DIR="$1"

# Go through all VoA files with a *.txt format
find "${TRANSCRIPT_DIR}" -type f -name "*.txt" \
  | grep "voa-" \
  | while read text_file_path; do
    cat "${text_file_path}" \
      | grep "[a-z]" \
      | grep -v " – *[nv]\. " \
      | grep -v " – *ad[jv]\. " > tmp
    mv tmp "${text_file_path}"
done
