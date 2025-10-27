import csv
import textstat

from compute_readability import limit_text_by_word_count
from os import listdir
from os.path import isfile, join, splitext
from punctuator import Punctuator

p = Punctuator('Demo-Europarl-EN.pcl')

def format_text(text):
    formatted_text = textstat.remove_punctuation(text)
    formatted_text = formatted_text.lower().replace('\n', ' ').strip()

    return formatted_text

def limit_texts_from_dir(
    texts_dir,
    out_dir,
    is_punct = False,
    count_limit = 100,
    is_save = True
):
    for entry in sorted(listdir(texts_dir)):
        text_path = join(texts_dir, entry)
        utt_id = splitext(entry)[0]

        if isfile(text_path) and entry.endswith(".txt"):
            with open(text_path, mode = 'r') as text_f:
                text = text_f.read()

            if is_punct:
                text = textstat.remove_punctuation(text)
                text = p.punctuate(text.lower())

            limited_text = \
                limit_text_by_word_count(text,
                                         count_limit = count_limit,
                                         is_save_sentences = is_save)
            output_text = format_text(limited_text)

            out_path = join(out_dir, entry)
            with open(out_path, mode = 'w') as out_f:
                out_f.write(output_text)
            print(f"Word-limited version of {utt_id} was created.")

def limit_texts_from_list(
    texts_list_path,
    out_dir,
    is_punct = False,
    count_limit = 100,
    is_save = True
):
    with open(texts_list_path, 'r') as textlist_f:
        for entry in textlist_f:
            utt_id,text = entry.strip().split(" ", maxsplit=1)

            if is_punct:
                text = textstat.remove_punctuation(text)
                text = p.punctuate(text.lower())

            limited_text = limit_text_by_word_count(
                text,
                count_limit=count_limit,
                is_save=is_save
            )
            output_text = format_text(limited_text)

            out_path = join(out_dir, utt_id + ".txt")
            with open(out_path, mode = 'w') as out_f:
                out_f.write(output_text)
            print(f"Word-limited version of {utt_id} was created.")

def get_counts(text):
    counts = []
    easyw_count = 0
    hardw_count = 0

    text = text.lower().replace('\n', '. ').replace('.. ', '. ').strip()

    # Count easy and hard words as defined in the Linsear Write Formula
    words = text.split()[:100]
    for word in words:
        if textstat.syllable_count(word) < 3:
            easyw_count += 1
        else:
            hardw_count += 1

    # Count miniwords as defined in the McAlpine EFLAW Readability Score
    miniw_count = textstat.miniword_count(text)

    # Count difficult words as defined in the Dale-Chall Formula
    diffw_count = textstat.difficult_words(text, syllable_threshold=0)


    syll_count = textstat.syllable_count(text)
    word_count = textstat.lexicon_count(text)
    sent_count = textstat.sentence_count(text)

    counts = [
        easyw_count, hardw_count, miniw_count, diffw_count, syll_count, 
        word_count, sent_count
    ]

    return counts

def get_counts_from_dir(
    texts_dir,
    is_punct = False,
    is_limit = False,
    count_limit = 100,
    is_save = True
):
    counts_list = []

    for entry in sorted(listdir(texts_dir)):
        text_path = join(texts_dir, entry)
        utt_id = splitext(entry)[0]

        print(f"Processing {utt_id}.")

        if isfile(text_path) and entry.endswith(".txt"):
            with open(text_path, mode = 'r') as text_f:
                text = text_f.read()

            if is_punct:
                text = textstat.remove_punctuation(text)
                text = p.punctuate(text.lower())

            if is_limit:
                text = limit_text_by_word_count(
                    text,
                    count_limit = count_limit,
                    is_save_sentences = is_save
                )

            counts = get_counts(text)
            counts.insert(0, utt_id)

            counts_list.append(counts)

    return counts_list

def get_counts_from_list(
    texts_path,
    is_punct = False,
    is_limit = False,
    count_limit = 100,
    is_save = True
):
    counts_list = []

    with open(texts_path, 'r') as texts_f:
        for entry in texts_f:
            utt_id,text = entry.strip().split(" ", maxsplit=1)

            print(f"Processing {utt_id}.")

            if is_punct:
                text = textstat.remove_punctuation(text)
                text = p.punctuate(text.lower())

            if is_limit:
                text = limit_text_by_word_count(
                    text,
                    count_limit=count_limit,
                    is_save_sentences=is_save
                )

            counts = get_counts(text)
            counts.insert(0, utt_id)

            counts_list.append(counts)

    return counts_list

def run_voa_example():
    """
    Sample run with VOA Learning English materials
    """
    is_punct = False
    count_limit = 100
    is_save = True

    data_name = "voa"
    asr_name = "gws"

    main_dir = join("data", data_name)
    asr_dir = join(main_dir, "processed/asr/google-web-speech")
    texts_dir = join(main_dir, "processed/transcripts")
    results_dir = join(main_dir, "results/2023_nodalida/google-web-speech")
    ref_dir = join(asr_dir, "refs_lim-100")

    # limit_texts_from_dir(texts_dir,
    #                      out_dir = ref_dir,
    #                      is_punct = is_punct,
    #                      count_limit = count_limit,
    #                      is_save = is_save)
    # print("DONE. Files saved in %s." % ref_dir)

    is_limit = False
    counts_file = "actual_text-counts.csv"
    counts_path = join(results_dir, counts_file)

    # counts_list = get_counts_from_dir(texts_dir,
    #                                   is_punct = is_punct,
    #                                   is_limit = is_limit,
    #                                   count_limit = count_limit,
    #                                   is_save = is_save)
    #
    # with open(counts_path, "w", newline = "") as counts_f:
    #     writer = csv.writer(counts_f)
    #     writer.writerow(["id",
    #                      "easy",
    #                      "hard",
    #                      "mini",
    #                      "diff",
    #                      "syll",
    #                      "word",
    #                      "sent"])
    #     writer.writerows(counts_list)

    is_punct = True
    texts_file = "voa-1000_google-web_T-chunks_T-period_hyp.txt"
    texts_path = join(asr_dir, texts_file)
    # hyp_dir = join(asr_dir, "hyps_lim-100")

    # limit_texts_from_list(texts_path,
    #                       out_dir = hyp_dir,
    #                       is_punct = is_punct,
    #                       count_limit = count_limit,
    #                       is_save = is_save)
    # print("DONE. Files saved in %s." % hyp_dir)

    is_limit = False
    counts_file = "voa_gws_text-counts.csv"
    counts_path = join(results_dir, counts_file)

    counts_list = get_counts_from_list(
        texts_path,
        is_punct=is_punct,
        is_limit=is_limit,
        count_limit=count_limit,
        is_save=is_save
    )

    with open(counts_path, "w", newline = "") as counts_f:
        writer = csv.writer(counts_f)
        writer.writerow([
            "id", "easy", "hard", "mini", "diff", "syll", "word", "sent"
        ])
        writer.writerows(counts_list)

def main():
    run_voa_example()

if __name__ == "__main__":
    main()
