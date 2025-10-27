import csv
import matplotlib.pyplot as plt
import os
import pandas as pd

from os.path import isfile,join,splitext

rttm_header = [
    'Type', 'file', 'chnl', 'tbeg', 'tdur', 'ortho', 'stype', 'name', 'conf',
    'Slat'
]

def create_interval_header(intr_name, intr_xmax, intr_size):
    interval_header = [
        'class = "IntervalTier" \n',
        'xmin = 0\n',
    ]

    name_header = \
        'name = "{intr_name:s}"\n'.format(intr_name = intr_name)
    interval_header.insert(1, name_header)

    xmax_header = \
        "xmax = {intr_xmax:f}\n".format(intr_xmax = intr_xmax)
    interval_header.insert(3, xmax_header)

    size_header = \
        "intervals: size = {intr_size:d}\n".format(intr_size = intr_size)
    interval_header.append(size_header)

    interval_header = ["\t\t" + info for info in interval_header]

    return interval_header

def create_segment_record(seg_num, seg_xmin, seg_xmax, seg_text):
    segment_record = []

    seg_num_info = \
        "\t\tintervals [{seg_num:d}]:\n".format(seg_num = seg_num + 1)
    segment_record.append(seg_num_info)

    if float(seg_xmin) == 0:
        seg_xmin_info = "\t\t\txmin = 0\n"
    else:
        seg_xmin_info = "\t\t\txmin = {seg_xmin:f}\n".format(seg_xmin = seg_xmin)
    segment_record.append(seg_xmin_info)

    seg_xmax_info = "\t\t\txmax = {seg_xmax:f}\n".format(seg_xmax = seg_xmax)
    segment_record.append(seg_xmax_info)

    seg_text_info = '\t\t\ttext = "{seg_text}"\n'.format(seg_text = seg_text)
    segment_record.append(seg_text_info)

    return segment_record

def create_textgrid_header(tg_xmax, tg_size):
    textgrid_header = [
        'File type = "ooTextFile"\n',
        'Object class = "TextGrid"\n\n',
        "xmin = 0\n",
        "tiers? <exists> \n",
        "item []:\n"
    ]

    xmax_header = \
        "xmax = {tg_xmax:f}\n".format(tg_xmax = tg_xmax)
    textgrid_header.insert(3, xmax_header)

    size_header = \
        "size = {tg_size:d}\n".format(tg_size = tg_size)
    textgrid_header.insert(-1, size_header)

    return textgrid_header

def get_all_speaker_counts(rttm_dir):
    summary_df = pd.DataFrame()

    for rttm_file in sorted(os.listdir(rttm_dir)):
        rttm_path = join(rttm_dir, rttm_file)

        if isfile(rttm_path) and rttm_file.startswith("rttm"):
            rttm_id = rttm_file.replace("rttm", "").strip("_")
            rttm_df = load_rttm_file(rttm_path)

            counts_df = get_speaker_counts(rttm_df)
            counts_df = counts_df.rename({'spkrcnts':rttm_id}, axis='columns')

            if summary_df.empty:
                summary_df = counts_df
            else:
                summary_df = pd.merge(summary_df, counts_df, on='file')

    fig,ax = plt.subplots(1,1)
    # summary_df.boxplot(notch=True)
    summary_df.boxplot()
    ax.set_xticklabels(
        ax.get_xticklabels(),
        rotation=90
    )
    plt.xlabel('diarisation type and threshold factor')
    plt.ylabel('number of speakers')

    plt.ylim((0,120))
    fig.tight_layout()

    plt.show()

    return summary_df

def get_speaker_counts(rttm_df):
    counts = []

    for utt_id in rttm_df.file.unique():
        count = rttm_df.loc[rttm_df['file']==utt_id, 'name'].nunique()
        counts.append([utt_id, count])

    return pd.DataFrame(counts, columns=['file', 'spkrcnts'])

def load_rttm_file(rttm_path):
    rttm_df = pd.read_table(
        rttm_path,
        delim_whitespace=True,
        header=None,
        names=rttm_header
    )

    return rttm_df

def rttm_to_textgrid(utt_id, utt_records, textgrid_dir, cols_to_write):
    utt_records.reset_index(drop=True, inplace=True)
    print(utt_records)
    cols_to_write = list(set(rttm_header).intersection(cols_to_write))

    textgrid_file = utt_id + ".TextGrid"
    textgrid_path = join(textgrid_dir, textgrid_file)

    xmax_val = utt_records['tend'].iloc[-1]
    textgrid_header = create_textgrid_header(
        tg_xmax=xmax_val,
        tg_size=len(cols_to_write)
    )

    if not os.path.isdir(textgrid_dir):
        os.makedirs(textgrid_dir)

    with open(textgrid_path, mode='w') as tg_f:
        tg_f.writelines(textgrid_header)

        for item_no,col_to_write in enumerate(cols_to_write):
            tg_f.write("\titem [%d]:\n" % (item_no + 1))

            size_val = len(utt_records[col_to_write])

            interval_header = create_interval_header(
                intr_name=col_to_write,
                intr_xmax=xmax_val,
                intr_size=size_val
            )
            tg_f.writelines(interval_header)

            for seg_num in range(size_val):
                segment_record = create_segment_record(
                    seg_num=seg_num,
                    seg_xmin=utt_records['tbeg'][seg_num],
                    seg_xmax=utt_records['tend'][seg_num],
                    seg_text=utt_records[col_to_write][seg_num]
                )
                tg_f.writelines(segment_record)

    print("TextGrid for %s created in %s" % (utt_id, textgrid_dir))

def run_elllo_example():
    elllo_dir = "data/elllo"
    rttm_dir = join(elllo_dir, "results/diarization/kaldi-sre16/no-segmenter/target-energy-1.0")
    rttm_file = "rttm_unsup_0.40"
    rttm_path = join(rttm_dir, rttm_file)

    textgrid_dir = join(rttm_dir, rttm_file + "_tgs")

    speaker_count_file = rttm_file + "_spkcounts.csv"
    speaker_count_path = join(rttm_dir, speaker_count_file)

    # rttm_df = load_rttm_file(rttm_path)
    # rttm_df['tend'] = rttm_df.apply(
    #     lambda row: row.tbeg + row.tdur,
    #     axis=1
    # )
    #
    # cols_to_write = ['name']
    # counts_header = ['utt_id', 'spkrcnt']
    # counts_info = []
    #
    # for utt_id in rttm_df.file.unique():
    #     utt_records = rttm_df.loc[rttm_df['file'] == utt_id]
    #     rttm_to_textgrid(utt_id, utt_records, textgrid_dir, cols_to_write)

    counts_summary_df = get_all_speaker_counts(rttm_dir)


def main():
    run_elllo_example()

if __name__ == "__main__":
    main()
