from os import listdir, mkdir
from os.path import basename, dirname, isfile, join, splitext

from pydub import AudioSegment
from pydub.silence import detect_nonsilent, split_on_silence

# settings for voa
KEEP_SILENCE=500
MIN_SILENCE_LEN=1000
SEEK_STEP=1

# settings for elllo
# KEEP_SILENCE=500
# MIN_SILENCE_LEN=500
# SEEK_STEP=1

def get_segments(utt_id, utt_loc):
    segments = list()

    utt_dir = dirname(utt_loc)
    utt_ext = splitext(utt_loc)[1]

    speech_data = getattr(AudioSegment, "from_" + utt_ext[1:])(utt_loc)

    # Silence defined based on RMS
    # VoA: minus 30 derived empirically, specifically
    # to accommodate words ending in unvoiced fricatives (e.g., /s/)
    silence_thresh = speech_data.dBFS - 30

    # Get timestamps of speech segments
    segment_times = detect_nonsilent(speech_data, \
                                     min_silence_len=MIN_SILENCE_LEN, \
                                     silence_thresh=silence_thresh, \
                                     seek_step=SEEK_STEP)

    for segment_time in segment_times:
        segment_id = utt_id + "_" + str(round(segment_time[0]/100)).zfill(5) \
                     + "-" + str(round(segment_time[1]/100)).zfill(5)
        segment = segment_id + " " \
                  + utt_id + " " \
                  + "{:.2f}".format(round(segment_time[0]/100)/10) + " " \
                  + "{:.2f}".format(round(segment_time[1]/100)/10)
        segments.append(segment)

    return segments

def main():
    main_dir = ""
    wav_scp_file = main_dir + "/wav.scp"
    segments_file = main_dir + "/segments"

    with open(segments_file, 'w') as seg_out_f:
        with open(wav_scp_file, 'r') as wav_in_f:
            for entry in wav_in_f:
                utt_id,utt_loc = entry.strip().split(" ", maxsplit=1)
                segments = get_segments(utt_id, utt_loc)

                seg_out_f.write("\n".join(segments))
                seg_out_f.write("\n")

if __name__ == "__main__":
    main()
