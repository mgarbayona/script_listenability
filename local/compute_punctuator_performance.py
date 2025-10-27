import csv
import numpy as np
import re
import textstat as ts

from os import listdir, makedirs
from os.path import isfile, join, splitext
from punctuator import Punctuator
from sklearn.metrics import f1_score

p = Punctuator('Demo-Europarl-EN.pcl')

punctuation_map = dict({'all': ["period","qmark","comma","average"],
                        '.': ["period"],
                        '?': ["qmark"],
                        ',': ["comma"]})

system_map = dict({'actual': 'actual',
                   'gws': 'google-web-speech',
                   'ka5': 'kaldi-aspire-s5'})

def compute_f1_from_dir(true_dir, f1_scores_file, punctuation = "all"):
    """
    Compute the F1 score of the punctuator based on all the text files in the
    specified directory. Returns a score per file, and the scores are saved in
    CSV format

    Parameters
    ----------
    true_dir       : string
                     Directory where the ground truth text files are stored
    f1_scores_file : string
                     Location of the output CSV file where the scores will be
                     stored
    punctuation    : string
                     Punctuation that will be used for the calculation of the F1
                     score

    Returns
    -------
    f1_score_avg   : float
                     Average of all the F1 scores calculated. If 'punctuation'
                     is "all", then the average score returned is the average
                     of the microaverage F1 score of all punctuations considered
    """
    f1_scores = list()

    out_header = punctuation_map[punctuation]
    out_header.insert(0, "utt_id")

    for entry in sorted(listdir(true_dir)):
        text_path = join(true_dir, entry)
        utt_id = splitext(entry)[0]

        if isfile(text_path):
            with open(text_path, 'r') as true_in_f:
                true_text = true_in_f.read().lower()

            pred_text = ts.remove_punctuation(true_text)
            pred_text = p.punctuate(pred_text)

            text_f1_score = compute_f1_from_text(true_text,
                                                 pred_text,
                                                 punctuation = punctuation)

            text_f1_score.insert(0, utt_id)
            f1_scores.append(text_f1_score)

    with open(f1_scores_file, mode = 'w+') as scores_f:
        score_writer = csv.writer(scores_f)
        score_writer.writerow(out_header)
        score_writer.writerows(f1_scores)
        print("F1 scores stored in %s." % f1_scores_file)

    f1_score_avg = sum(row[-1] for row in f1_scores) / len(f1_scores)

    return f1_score_avg

def compute_f1_from_text(true_text, pred_text, punctuation = "all"):
    """
    Compute the F1 score of the punctuator based from the punctuator's output
    text and its corresponding ground truth text

    Parameters
    ----------
    true_text     : string
                    Text with the true placement of punctuations
    pred_text     : string
                    Text output of the punctuator
    punctuation   : string
                    Punctuation that will be used for the calculation of the F1
                    score

    Returns
    -------
    text_f1_score : list
                    Punctuator's F1 score
                    If punctuation is "all", will contain the F1 scores
                    for all punctuations considered (period, question mark and
                    comma)
    """
    punctuations = [".", "?", ","]

    # Remove isolated punctuations, e.g. " - " or " ... "
    true_tokens = [token for token in true_text.split()
                         if re.search("[a-z0-9]", token)]
    pred_tokens = pred_text.split()

    if punctuation == "all":
        true_y = list()
        pred_y = list()

        for punctuation in punctuations:
            true_y += get_output_labels(true_tokens, punctuation)
            pred_y += get_output_labels(pred_tokens, punctuation)
        true_y = np.reshape(true_y, (len(punctuations), -1)).T
        pred_y = np.reshape(pred_y, (len(punctuations), -1)).T

        text_f1_score = f1_score(true_y,
                                 pred_y,
                                 average=None,
                                 zero_division=1).tolist()
        text_f1_score.append(f1_score(true_y,
                                      pred_y,
                                      average='micro',
                                      zero_division=1))
    else:
        true_y = get_output_labels(true_tokens, punctuation)
        pred_y = get_output_labels(pred_tokens, punctuation)

        text_f1_score = [f1_score(true_y, pred_y, zero_division=1).tolist()]

    return text_f1_score

def get_output_labels(tokens, punctuation):
    """
    Generate binary labels needed for the F1 score calculation

    Parameters
    ----------
    tokens      : list
                  Text split into words and stored in list format
    punctuation : string
                  Punctuation that will be used for the calculation of the F1
                  score

    Returns
    -------
    labels      : list
                  Corresponding binary labels -- '1' if the desired punctuation
                  is present, '0' if not
    """
    labels = [1 if punctuation in token else 0 for token in tokens]

    return labels

def punctuate_text(text):
    text = ts.remove_punctuation(text)
    text = p.punctuate(text)

    return text

def punctuate_texts_in_dir(texts_dir, out_dir):
    makedirs(out_dir, exist_ok = True)

    for entry in sorted(listdir(texts_dir)):
        text_path = join(texts_dir, entry)

        if isfile(text_path) and entry.endswith(".txt"):
            print("Processing %s" % entry)
            out_path = join(out_dir, entry)

            with open(text_path, mode = 'r') as text_f:
                text = text_f.read()

            out_text = punctuate_text(text)
            with open(out_path, mode = 'w') as out_f:
                out_f.write(out_text)

def punctuate_texts_in_list(texts_path, out_dir):
    makedirs(out_dir, exist_ok = True)

    with open(texts_path, 'r') as texts_f:
        for entry in texts_f:
            utt_id,text = entry.strip().split(" ", maxsplit=1)
            print("Processing %s" % utt_id)

            out_text = punctuate_text(text)

            if not utt_id.endswith(".txt"):
                utt_id = utt_id + ".txt"
            out_path = join(out_dir, utt_id)

            with open(out_path, mode = 'w') as out_f:
                out_f.write(out_text)

def run_demo():
    """
    Demo calculating the punctuator's F1 score
    """
    score_type = "ka5"

    # Access to ASR outputs will be needed to run this demo
    # Request permission from VoA to access the original VoA materials which 
    # will be the input to the ASR system
    hyps_dir = join("data", score_type, "hyps")
    puncd_dir = join("data", score_type, "hyps_punctuator")
    makedirs(puncd_dir, exist_ok = True)

    punctuate_texts_in_dir(hyps_dir, puncd_dir)

def main():
    run_demo()

if __name__ == "__main__":
    main()
