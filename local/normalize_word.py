import csv
import enchant
import re

from nltk import pos_tag
from nltk.corpus import words
from nltk.corpus import wordnet as wn
from nltk.stem import PorterStemmer,WordNetLemmatizer
from os.path import join

prefixes_path = "local/resources/wordlists/en_prefixes.txt"
pre_f = open(prefixes_path, "r")
try:
    content = pre_f.read()
    en_prefixes = dict.fromkeys(content.split(","), "")
finally:
    pre_f.close()

en_dict = enchant.Dict("en_US")
lemmatizer = WordNetLemmatizer()
porter = PorterStemmer()

whitelist = list(wn.words()) + words.words()

def get_lemma(word, raw_pos_tag):
    word_lemma = ""

    word_pos_tag = get_pos_tag_for_lemmatizer(raw_pos_tag)
    word_lemma = lemmatizer.lemmatize(word, pos=word_pos_tag)

    return word_lemma

def get_pos_tag_for_lemmatizer(raw_pos_tag):
    raw_pos_tag = raw_pos_tag.upper()

    if "V" in raw_pos_tag:
        word_pos_tag = "v"
    elif "JJ" in raw_pos_tag:
        word_pos_tag = "a"
    elif "RB" in raw_pos_tag:
        word_pos_tag = "r"
    else:
        word_pos_tag = "n"

    return word_pos_tag

def get_stem(word, prefixes=en_prefixes):

    word_stem = porter.stem(remove_prefix(word, prefixes, whitelist))

    return word_stem

def remove_prefix(word, prefixes, roots):

    original_word = word

    for prefix in sorted(prefixes, key=len, reverse=True):
        # Use subn to track the no. of substitution made.
        # Allow dash in between prefix and root.
        word, nsub = re.subn("^{}[\-]?".format(prefix), "", word)
        if nsub > 0 and word in roots:
            return word

    return original_word

def main():
    list_dir = "local/resources/wordlists"
    # list_file = "bnc-coca_master-list.csv"
    list_file = "dale-chall.txt"
    # new_list_file = "bnc-coca_master-list-detailed.csv"
    new_list_file = "dale-chall-detailed.csv"

    list_path = join(list_dir, list_file)
    new_list_path = join(list_dir, new_list_file)

    with open(list_path, mode = "r") as list_f, \
         open(new_list_path, mode = "w") as new_list_f:
        entry_writer = csv.writer(new_list_f, delimiter=',')

        for entry in list_f:
            # word,headword_class = entry.strip().lower().split(",")
            word = entry.strip().lower()

            if not en_dict.check(word):
                # Use American English spelling rules
                word = en_dict.suggest(word)[0].lower()

            # raw_pos_tag = pos_tag([word])[0][1]
            # word_lemma = get_lemma(word, raw_pos_tag)
            word_lemma_n = get_lemma(word, "n")
            word_lemma_v = get_lemma(word, "v")
            word_lemma_a = get_lemma(word, "a")
            word_lemma_r = get_lemma(word, "r")
            word_stem = get_stem(word)
            # entry = [word, word_stem, word_lemma_n, word_lemma_v, 
            #          word_lemma_a, word_lemma_r, headword_class]
            entry = [word, word_stem, word_lemma_n, word_lemma_v, 
                     word_lemma_a, word_lemma_r]

            entry_writer.writerow(entry)

if __name__ == "__main__":
    main()
