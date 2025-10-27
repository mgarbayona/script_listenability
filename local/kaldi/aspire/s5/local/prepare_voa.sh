#!/usr/bin/env bash

SPEECH_DIR=""
TRANSCRIPT_DIR=""

VOA_DIR="data/voa"
LEARN_ENG_DIR="data/voa/learning-english"

mkdir -p "${VOA_DIR}"
mkdir -p "${LEARN_ENG_DIR}"

rm -f "${LEARN_ENG_DIR}/text"

##GENERATE TRANSCRIPTS FILE
echo "Generating transcripts file..."
ls "${TRANSCRIPT_DIR}" \
  | grep ".txt" \
  | grep "^voa-" \
  | while read transcript_file; do
    utt_id=`echo "${transcript_file}" | sed -e 's#.txt$##g'`

    transcript=`cat "${TRANSCRIPT_DIR}/${transcript_file}" \
      | sed -e "s#…# #g" \
      | tr "‘" " " \
      | sed -e "s#’ # #g" \
      | tr "’" "'" \
      | tr "[a-z]" "[A-Z]" \
      | sed -e 's#[-—.,:;!?"“”]# #g' \
      | sed -e "s#[][]##g" \
      | tr "\n" " " \
      | tr -s " "`

    echo "${utt_id} ${transcript}" >> "${LEARN_ENG_DIR}/text"
  done
echo "Done."

##GENERATE WAV.SCP
echo "Generating wav.scp file..."
cat "${LEARN_ENG_DIR}/text" | cut -d " " -f 1 > "${LEARN_ENG_DIR}/utt_ids.tmp"
cat "${LEARN_ENG_DIR}/text" \
  | cut -d " " -f 1 \
  | sed -e 's#$#.wav#g' \
  | sed -e "s#^#${SPEECH_DIR}/#g" > "${LEARN_ENG_DIR}/utt_locs.tmp"
paste -d " " "${LEARN_ENG_DIR}/utt_ids.tmp" "${LEARN_ENG_DIR}/utt_locs.tmp" \
  > "${LEARN_ENG_DIR}/wav.scp"
echo "Done."

##GENERATE UTT2SPK
# For now we are assigning one speaker ID per recording
echo "Generating utt2spk file..."
cat "${LEARN_ENG_DIR}/text" | cut -d "-" -f 1-2 > "${LEARN_ENG_DIR}/spk_ids.tmp"
paste -d " " "${LEARN_ENG_DIR}/utt_ids.tmp" "${LEARN_ENG_DIR}/spk_ids.tmp" \
  > "${LEARN_ENG_DIR}/utt2spk"
echo "Done."

##GENERATE SPK2UTT
utils/fix_data_dir.sh "${LEARN_ENG_DIR}"
