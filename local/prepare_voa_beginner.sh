#!/usr/bin/env bash

VIDEO_DIR="$1"

# Save the audio files in the same parent directory
DATA_DIR=`dirname "${VIDEO_DIR}"`
AUDIO_DIR="${DATA_DIR}/wav"

echo "Extracting audio from video..."

# Create the folder if it doesn't exist yet
mkdir -p "${AUDIO_DIR}"

# Go through all video files with an MP4 format, get the audio, and save it
# in WAV format
find "${VIDEO_DIR}" -type f -name "*.mp4" | while read video_path; do
  audio_path=`echo "${video_path}" \
    | sed -e "s#${VIDEO_DIR}#${AUDIO_DIR}#g" \
    | sed -e 's#mp4$#wav#g'`

  echo "PROCESSING ${video_path}..."
  # Add the -nostdin option so as not to mess up with input filenames
  ffmpeg -nostdin -y -i "${video_path}" \
         -ac 1 \
         -acodec pcm_s16le \
         -ar 8000 \
         "${audio_path}"
done

echo "Done."
