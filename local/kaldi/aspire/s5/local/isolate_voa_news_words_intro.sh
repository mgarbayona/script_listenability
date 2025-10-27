#!/usr/bin/env bash

# ctm file: time-marked conversation file
IN_CTM_FILE="$1"
CTM_DIR=`dirname "${IN_CTM_FILE}"`
OUT_CTM_FILE=`echo "${CTM_DIR}/isolated_intro.ctm"`

# intro message: Welcome to the Voice of America's News Words
INTRO_WORD_CNT=8
BODY_WORD_START=$((INTRO_WORD_CNT + 1))

rm -f "${OUT_CTM_FILE}"

cat "${IN_CTM_FILE}" \
  | cut -d " " -f 1 \
  | sort | uniq | while read utt_id; do
    word_cnt=0

    intro_start="0.000"

    intro_last_times=`grep "^${utt_id}" "${IN_CTM_FILE}" \
      | head -n "${INTRO_WORD_CNT}" \
      | tail -n 1 \
      | cut -d " " -f 3-4`
    intro_last_start=`echo "${intro_last_times}" | cut -d " " -f 1`
    intro_last_dur=`echo "${intro_last_times}" | cut -d " " -f 2`
    intro_dur=`echo "${intro_last_start} + ${intro_last_dur}" | bc`

    intro_text=`grep "^${utt_id}" "${IN_CTM_FILE}" \
      | head -n "${INTRO_WORD_CNT}" \
      | cut -d " " -f 5 \
      | tr "\n" " "`

    body_last_times=`grep "^${utt_id}" "${IN_CTM_FILE}" \
      | tail -n 1 \
      | cut -d " " -f 3-4`
    body_last_start=`echo "${body_last_times}" | cut -d " " -f 1`
    body_last_dur=`echo "${body_last_times}" | cut -d " " -f 2`
    body_dur=`echo "${body_last_start} + ${body_last_dur}" | bc`
    body_dur=`echo "${body_dur} - ${intro_dur}" | bc`

    body_text=`grep "^${utt_id}" "${IN_CTM_FILE}" \
      | tail -n +"${BODY_WORD_START}" \
      | cut -d " " -f 5 \
      | tr "\n" " "`

    echo "${utt_id} 1 ${intro_start} ${intro_dur} ${intro_text}" \
      >> "${OUT_CTM_FILE}"
    echo "${utt_id} 1 ${intro_dur} ${body_dur} ${body_text}" \
      >> "${OUT_CTM_FILE}"
  done
