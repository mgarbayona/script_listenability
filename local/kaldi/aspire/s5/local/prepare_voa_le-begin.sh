#!/usr/bin/env bash

SPEECH_DIR=""
TRANSCRIPT_DIR=""

VOA_DIR="data/voa"
BEGIN_DIR="${VOA_DIR}/le-begin"

mkdir -p "${VOA_DIR}"
mkdir -p "${BEGIN_DIR}"

rm -f "${BEGIN_DIR}/text"

##GENERATE TRANSCRIPTS FILE
echo "Generating transcripts file..."
ls "${TRANSCRIPT_DIR}" \
  | grep "^voa-" \
  | grep "1.txt" \
  | while read transcript_file; do
    utt_id=`echo "${transcript_file}" | sed -e 's#.txt$##g'`

    transcript=`cat "${TRANSCRIPT_DIR}/${transcript_file}" \
      | sed -e "s#…# #g" \
      | tr "’" "'" \
      | tr "[a-z]" "[A-Z]" \
      | sed -e 's#[-—.,:;!?"“”]# #g' \
      | sed -e "s#[][]##g" \
      | tr "\n" " " \
      | tr -s " "`

    echo "${utt_id} ${transcript}" >> "${BEGIN_DIR}/text"
  done
echo "Done."

##GENERATE WAV.SCP
echo "Generating wav.scp file..."
cat "${BEGIN_DIR}/text" | cut -d " " -f 1 > "${BEGIN_DIR}/utt_ids.tmp"
cat "${BEGIN_DIR}/text" \
  | cut -d " " -f 1 \
  | sed -e 's#$#.wav#g' \
  | sed -e "s#^#${SPEECH_DIR}/#g" > "${BEGIN_DIR}/utt_locs.tmp"
paste -d " " "${BEGIN_DIR}/utt_ids.tmp" "${BEGIN_DIR}/utt_locs.tmp" \
  > "${BEGIN_DIR}/wav.scp"
echo "Done."

##GENERATE UTT2SPK
# For now we are assigning one speaker ID per recording
echo "Generating utt2spk file..."
cat "${BEGIN_DIR}/text" | cut -d "-" -f 1-2 > "${BEGIN_DIR}/spk_ids.tmp"
paste -d " " "${BEGIN_DIR}/utt_ids.tmp" "${BEGIN_DIR}/spk_ids.tmp" \
  > "${BEGIN_DIR}/utt2spk"
echo "Done."

##GENERATE SPK2UTT
utils/fix_data_dir.sh "${BEGIN_DIR}"
