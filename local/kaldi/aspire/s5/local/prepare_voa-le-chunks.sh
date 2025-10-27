#!/usr/bin/env bash

DATA_DIR=""
SPEECH_DIR="${DATA_DIR}/processed/wav"
TRANSCRIPT_DIR="${DATA_DIR}/processed/transcript"

VOA_DIR="data/voa"
LECHUNKS_DIR="${VOA_DIR}/le-chunks"

mkdir -p "${VOA_DIR}"
mkdir -p "${LECHUNKS_DIR}"

rm -f "${LECHUNKS_DIR}/text"

##GENERATE TRANSCRIPTS FILE
echo "Generating transcripts file..."
ls "${TRANSCRIPT_DIR}" \
  | grep "\.txt" \
  | grep "^voa-" \
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

    echo "${utt_id} ${transcript}" >> "${LECHUNKS_DIR}/text"
  done

# ls "${SPEECH_DIR}" \
#   | grep "\.wav" \
#   | grep "^voa-" \
#   | while read wav_file; do
#     utt_id=`echo "${wav_file}" | sed -e 's#.wav$##g'`
#     transcript="PLACEHOLDER"
#     echo "${utt_id} ${transcript}" >> "${LECHUNKS_DIR}/text"
#   done
#
# echo "Done."

##GENERATE WAV.SCP
echo "Generating wav.scp file..."
cat "${LECHUNKS_DIR}/text" | cut -d " " -f 1 > "${LECHUNKS_DIR}/utt_ids.tmp"
cat "${LECHUNKS_DIR}/text" \
  | cut -d " " -f 1 \
  | sed -e 's#$#.wav#g' \
  | sed -e "s#^#${SPEECH_DIR}/#g" > "${LECHUNKS_DIR}/utt_locs.tmp"
paste -d " " "${LECHUNKS_DIR}/utt_ids.tmp" "${LECHUNKS_DIR}/utt_locs.tmp" \
  > "${LECHUNKS_DIR}/wav.scp"
echo "Done."

##GENERATE SEGMENTS
echo "Generating segments file..."
python local/generate_segments_file.py
echo "Done."

##GENERATE UTT2SPK
# For now we are assigning one speaker ID per recording
echo "Generating utt2spk file..."
cat "${LECHUNKS_DIR}/segments" \
  | cut -d "-" -f 1-2 \
  > "${LECHUNKS_DIR}/spk_ids.tmp"
cat "${LECHUNKS_DIR}/segments" | cut -d " " -f 1 > "${LECHUNKS_DIR}/seg_ids.tmp"
paste -d " " "${LECHUNKS_DIR}/seg_ids.tmp" "${LECHUNKS_DIR}/spk_ids.tmp" \
  > "${LECHUNKS_DIR}/utt2spk"
echo "Done."

##GENERATE DUMMY TRANSCRIPTS FILE
echo "Generating dummy text file..."
mv "${LECHUNKS_DIR}/text" "${LECHUNKS_DIR}/text-whole"
cat "${LECHUNKS_DIR}/seg_ids.tmp" | sed -e 's#$# PLACEHOLDER#g' \
  > "${LECHUNKS_DIR}/text"
echo "Done"

##GENERATE SPK2UTT
utils/fix_data_dir.sh "${LECHUNKS_DIR}"
