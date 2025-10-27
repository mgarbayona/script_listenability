#!/usr/bin/env bash

# ctm file: time-marked conversation file
CTM_FILE="$1"
WAV_SCP_FILE="$2"

# intro message: Welcome to the Voice of America's News Words [noise]
INTRO_WORD_CNT=8
BODY_WORD_START=$((INTRO_WORD_CNT + 1))

rm -f "${OUT_CTM_FILE}"

# Create new folders to store the processed recordings
cat "${WAV_SCP_FILE}" \
  | cut -d " " -f 2- \
  | rev \
  | cut -d "/" -f 2- \
  | rev | sort | uniq | while read utt_dir; do
    new_utt_dir=`echo "${utt_dir}-processed" `
    mkdir -p "${new_utt_dir}"
  done

cat "${CTM_FILE}" \
  | cut -d " " -f 1 \
  | sort | uniq | while read utt_id; do
    word_cnt=0

    # Get starting time of the recording's "body"
    intro_last_times=`grep "^${utt_id}" "${CTM_FILE}" \
      | head -n "${INTRO_WORD_CNT}" \
      | grep 'words\|noise' \
      | tail -n 1 \
      | cut -d " " -f 3-4`
    intro_last_start=`echo "${intro_last_times}" | cut -d " " -f 1`
    intro_last_dur=`echo "${intro_last_times}" | cut -d " " -f 2`
    intro_dur=`echo "${intro_last_start} + ${intro_last_dur}" | bc`

    # Define where the processed recording will be stored
    utt_loc=`grep "${utt_id}" "${WAV_SCP_FILE}" | cut -d " " -f 2-`
    new_utt_dir=`dirname "${utt_loc}" | sed -e 's#$#-processed#g'`
    utt_filename=`basename "${utt_loc}"`
    new_utt_loc=`echo "${new_utt_dir}/${utt_filename}"`

    # Cut out the intro
    ffmpeg -nostdin -y -ss "${intro_dur}" -i "${utt_loc}" "${new_utt_loc}"

  done
