import csv
import normalize_word as nw
import pandas as pd
import re
import spacy
import string
import textstat as ts

from cainesap_syllabify import syllable3
from nltk import pos_tag
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import sent_tokenize, word_tokenize
from os import listdir, makedirs
from os.path import isfile, join, splitext
from punctuator import Punctuator

# Load knowledge sources
en_compounds_path = "local/resources/wordlists/ogden_compound-words.csv"
with open(en_compounds_path, mode="r") as cw_f:
    cw_reader = csv.reader(cw_f)
    en_cw_dict = {entry[0]:entry[1] for entry in cw_reader}

en_dep_markers_path = "local/resources/wordlists/en_dep_markers.txt"
with open(en_dep_markers_path, mode="r") as dep_f:
    en_dep_markers = dep_f.read().strip().split(",")

en_stopwords_path = "local/resources/wordlists/en_stopwords.txt"
sw_f = open(en_stopwords_path, "r")
try:
    content = sw_f.read()
    en_stopwords = content.split(",")
finally:
    sw_f.close()

wordlists_dir = "local/resources/wordlists"
dale_list_path = join(wordlists_dir, "dale-chall-detailed.csv")
dale_df = pd.read_csv(dale_list_path, header=0)

wordlists_dir = "local/resources/wordlists"
en_headword_path = join(wordlists_dir, "bnc-coca_master-list-detailed.csv")
en_hw_df = pd.read_csv(en_headword_path, header=0)

# Load models
lemmatizer = WordNetLemmatizer()
nlp = spacy.load('en_core_web_trf')
p = Punctuator('Demo-Europarl-EN.pcl')

# Set up mappings
system_map = dict({
    'actual': 'actual',
    'gws': 'google-web-speech',
    'ka5': 'kaldi-aspire-s5'
})

tag_class = dict({
    'contraction-1': ['NN','NNP','NNS','PRP','WP'],
    'contraction-2': ['MD','VB','VBD','VBG','VBN','VBP','VBZ'],
    'linking': ['DT','IN'],
    'reduction': ['DT','IN','MD','PRP','WP'],
    'verb': ['VB','VBD','VBG','VBN','VBP','VBZ']
})

def average_sentence_length(text):
    ave_length = 0.0

    sent_count = ts.sentence_count(text)
    word_count = ts.lexicon_count(text)

    ave_length = word_count / sent_count

    return ave_length

def average_word_length(text):
    ave_length = 0.0

    syll_count = count_syllables_cainesap(text)
    word_count = ts.lexicon_count(text)

    ave_length = syll_count / word_count

    return ave_length

def compute_from_dir(
    texts_dir, 
    score_writer,
    is_punct = False,
    is_limit = False,
    count_limit = 100,
    is_save = True
):
    """
    This function calculates readability scores of all transcripts in a
    directory. It assumes that one file contains one transcript only.

    Parameters
    ----------
    texts_dir : string
        Directory where all the transcripts are stored
    score_writer : class '_csv.writer'
        Tells where to save the readability scores for each transcript
    is_punct : boolean
        Option to use ottokart's punctuator2,
        (https://github.com/ottokart/punctuator2)
        True if the punctuator will be used
    is_limit : boolean
        Option to truncate the text based on word count. True if the truncation
        will be applied
    count_limit : int
        Target word count of the truncated text. Default is 100 words
    is_save : boolean
        Option to keep complete sentences when a word count limit is imposed.
        This means that if the limit cuts the text in the middle of the
        sentence and this option is True, then the entire sentence will still
        be included in the truncated text instead.

    Returns
    -------
    None

    """

    for entry in sorted(listdir(texts_dir)):
        text_path = join(texts_dir, entry)
        utt_id = splitext(entry)[0]

        if isfile(text_path) and entry.endswith(".txt"):
            print("Analyzing %s" % entry)
            text_f = open(text_path, mode = 'r')
            text = text_f.read()
            text_f.close()

            text = text.replace('\n', ' ').strip()

            scores = compute_scores(
                text, 
                is_punct = is_punct,
                is_limit = is_limit,
                count_limit = count_limit,
                is_save = is_save
            )

            scores.insert(0, utt_id)
            score_writer.writerow(scores)

def compute_from_list(
    transcript_file, 
    score_writer,
    is_punct = False,
    is_limit = False,
    count_limit = 100,
    is_save = True
):
    """
    Calculate readability scores of all files in a directory

    Parameters
    ----------
    transcript_file : string
        Text file containing all the transcripts. One line contains one
        transcript. Format is <utt_id> <transcript>
    score_writer : class '_csv.writer'
        Tells where to save the readability scores for each transcript
    is_punct : boolean
        Option to use ottokart's punctuator2,
        (https://github.com/ottokart/punctuator2)
        True if the punctuator will be used
    is_limit : boolean
        Option to truncate the text based on word count True if the truncation
        will be applied
    count_limit : int
        Target word count of the truncated text. Default is 100 words
    is_save : boolean
        Option to keep complete sentences when a word count limit is imposed.
        This means that if the limit cuts the text in the middle of the
        sentence and this option is True, then the entire sentence will still
        be included in the truncated text instead.

    Returns
    -------
    None

    """

    with open(transcript_file, 'r') as tr_in_f:
        for entry in tr_in_f:
            utt_id,text = entry.strip().split(" ", maxsplit=1)
            print("Analyzing %s" % utt_id)

            text = re.sub(r'\[NOISE\]', "", text)
            text = re.sub(r' +', " ", text)

            scores = compute_scores(
                text, 
                is_punct = is_punct,
                is_limit = is_limit,
                count_limit = count_limit,
                is_save = is_save
            )

            scores.insert(0, utt_id)
            score_writer.writerow(scores)

def compute_idea_unit_length(text):
    idea_unit_length = 0.0
    ind_clause_count = 0.0

    text = text.replace("-"," ")
    text = text.replace("\n", ". ")
    text = text.replace("..", ".")
    word_count = ts.lexicon_count(text)

    sentences = re.findall(r'\b[^.!?]+[.!?]*', text, re.UNICODE)
    for sentence in sentences:
        ind_clause_count += count_independent_clause(
            sentence, dep_markers=en_dep_markers
        )

    try:
        idea_unit_length = word_count/ind_clause_count
    except ZeroDivisionError:
        idea_unit_length = 0.0

    return idea_unit_length

def compute_scores(
    text, 
    is_punct = False,
    is_limit = False,
    count_limit = 100,
    is_save = True
):
    """
    Calculate readability scores of all files in a directory

    Parameters
    ----------
    text : string
        Transcript to be processed
    is_punct : boolean
        Option to use ottokart's punctuator2,
        (https://github.com/ottokart/punctuator2)
        True if the punctuator will be used
    is_limit : boolean
        Option to truncate the text based on word count True if the truncation
        will be applied
    count_limit : int
        Target word count of the truncated text. Default is 100 words
    is_save : boolean
        Option to keep complete sentences when a word count limit is imposed.
        This means that if the limit cuts the text in the middle of the
        sentence and this option is True, then the entire sentence will still
        be included in the truncated text instead.
    Returns
    -------
    scores : list
        Readability scores
    """

    if is_punct:
        text = remove_punctuation(text)
        text = p.punctuate(text.lower())

    if is_limit:
        text = limit_text_by_word_count(
            text,
            count_limit=count_limit,
            is_save=is_save
        )

    sent_count = ts.sentence_count(text)
    syll_count = count_syllables_cainesap(text)
    word_count = ts.lexicon_count(text)

    miniw_count = ts.miniword_count(text)
    monosyll_count = count_monosyllables(text)
    not_in_dale_count = word_count - count_in_dale_list(text)

    ave_sent_len = average_sentence_length(text)
    ave_word_len = average_word_length(text)

    scores = [
        sent_count, syll_count, word_count, 
        miniw_count, monosyll_count, not_in_dale_count,
        ave_sent_len, ave_word_len
    ]

    return scores

def count_in_dale_list(text):
    count = 0.0

    sentences = sent_tokenize(text)

    for sentence in sentences:
        for word, word_pos in pos_tag(word_tokenize(sentence)):
            if (
                word and 
                (word not in string.punctuation) and 
                is_in_dale_list(word, word_pos)
            ):
                count += 1

    return count

def count_independent_clause(sentence, dep_markers=en_dep_markers):
    """
    Return number of independent clauses in a sentence

    Parameters
    ----------
    sentence : string
        Sentence to be processed
    dep_markers : list of strings
        List of dependent clause markers, default uses English language markers

    Returns
    -------
    ind_clause_count : float
        Number of indepndent clauses in the sentence
    """
    ind_clause_count = 0.0

    clauses = get_clauses(sentence)

    dep_clauses = list(filter(
        lambda x: x.startswith(tuple(dep_markers)), clauses
    ))
    ind_clause_count = float(len(clauses) - len(dep_clauses))

    return ind_clause_count

def count_monosyllables(text):
    count = 0.0
    ignore_words = ["the", "is", "are", "was", "were"]
    text = remove_punctuation(text)

    for word in text.split():
        if word.lower() not in ignore_words:
            if count_syllables_cainesap(word) == 1:
                count +=1

    return count

def count_syllables_cainesap(text):
    count = 0
    text = remove_punctuation(text)

    for word in text.split():
        syllables = syllable3.generate(word)
        if syllables:
            try:
                count += len(list(syllables)[0])
            except:
                # print(
                #     f"WARNING: cannot process {word.upper()}. "
                #     f"Defaults to pyphen."
                # )
                count += ts.syllable_count(word)
                pass
    return count

def find_other_verbs(doc, root_token):
    """
    Derived from Packt>
    """
    other_verbs = []
    for token in doc:
        ancestors = list(token.ancestors)
        if (
            token.tag_ in tag_class['verb'] and
            len(ancestors) == 1 and
            ancestors[0] == root_token
        ):
            other_verbs.append(token)
    return other_verbs

def find_root_of_sentence(doc):
    """
    From Packt>
    """
    root_token = None
    for token in doc:
        if (token.dep_ == "ROOT"):
            root_token = token
    return root_token

def get_clause_token_span_for_verb(verb, doc, all_verbs):
    """
    From Packt>
    """
    first_token_index = len(doc)
    last_token_index = 0
    this_verb_children = list(verb.children)
    for child in this_verb_children:
        if (child not in all_verbs):
            if (child.i < first_token_index):
                first_token_index = child.i
            if (child.i > last_token_index):
                last_token_index = child.i
    return(first_token_index, last_token_index)

def get_clauses(sentence):
    """
    From Packt>
    """
    sentence = ' '.join(sentence.split())
    doc = nlp(sentence)

    root_token = find_root_of_sentence(doc)
    other_verbs = find_other_verbs(doc, root_token)

    # Get start and end indices for all clauses
    token_spans = []
    all_verbs = [root_token] + other_verbs
    for other_verb in all_verbs:
        first_token_index, last_token_index = get_clause_token_span_for_verb(
            other_verb, doc, all_verbs
        )
        token_spans.append((first_token_index, last_token_index))

    # Get clauses
    sentence_clauses = []
    for token_span in token_spans:
        start = token_span[0]
        end = token_span[1]
        if (start < end):
            clause = doc[start:end]
            sentence_clauses.append(clause)
    sentence_clauses = sorted(sentence_clauses, key=lambda tup: tup[0])

    clauses_text = [clause.text.lower() for clause in sentence_clauses]

    return clauses_text

def get_compound_class(
    compound, compound_pos, cw_dict=en_cw_dict, hw_df=en_hw_df
):
    """
    Get headword class for a given compound word

    Parameters
    ----------
    compound : string
        Compound word to be analyzed
    compound_pos : string
        POS tag of the given compound word
    hw_df : pandas.DataFrame
        Record of headwords and corresponding classes

    Returns
    -------
    compound_class : float
        Corresponding headword class or rank of the compound word
    """
    # Default: if all components of a compound word are stopwords, assign a
    # level of 1
    compound_class = 1.0

    words = cw_dict[compound].split()

    for word in words:
        # Highest difficulty class assigned to a component is the class of the
        # compound word
        word_class = get_word_class(word, compound_pos, hw_df)
        compound_class = max(compound_class, word_class)

    return compound_class

def get_headword_class(headword, hw_df=en_hw_df):
    """
    Get class for a word's headword

    Parameters
    ----------
    headword : string
        Headword to be searched in the list of headwords
    hw_df : pandas.DataFrame
        Record of headwords and corresponding classes

    Returns
    -------
    word_class : float
        Corresponding headword class or rank of the word
    """
    headword_class = 11.0

    headword_match = hw_df.loc[hw_df["word"] == headword, "hw_class"]

    if not headword_match.empty:
        headword_class = float(headword_match.iloc[0])

    return headword_class

def get_lemma_class(word, raw_pos_tag, hw_df=en_hw_df):
    """
    Get headword class for a word's lemma

    Parameters
    ----------
    word : string
        Word to be lemmatized, lemma to be searched in the list of headwords
    raw_pos_tag : string
        Part-of-speech (POS) tag of the word
    hw_df : pandas.DataFrame
        Record of headwords and corresponding classes

    Returns
    -------
    lemma_class : float
        Corresponding headword class or rank of the word's lemma
    word_lemma : string
        Lemma of the given word
    """
    lemma_class = 11.0
    word_lemma = ""

    word_lemma = nw.get_lemma(word, raw_pos_tag)
    word_lemma_type = "lemma_" + nw.get_pos_tag_for_lemmatizer(raw_pos_tag)

    lemma_match = hw_df.loc[hw_df[word_lemma_type] == word_lemma, "hw_class"]

    if not lemma_match.empty:
        lemma_class = float(lemma_match.iloc[0])

    headword_class = get_headword_class(word_lemma, hw_df)

    lemma_class = min(lemma_class, headword_class)

    return lemma_class,word_lemma

def get_stem_class(word, hw_df=en_hw_df):
    """
    Get headword class for a word's stem

    Parameters
    ----------
    word : string
        Word to be stemmed, stem to be searched in the list of headwords
    hw_df : pandas.DataFrame
        Record of headwords and corresponding classes

    Returns
    -------
    stem_class : float
        Corresponding headword class or rank of the word's stem
    word_stem : string
        Stem of the given word
    """
    stem_class = 11.0
    word_stem = ""

    word_stem = nw.get_stem(word)
    stem_match = hw_df.loc[hw_df["stem"] == word_stem, "hw_class"]

    if not stem_match.empty:
        stem_class = float(stem_match.iloc[0])

    headword_class = get_headword_class(word_stem, hw_df)

    stem_class = min(stem_class, headword_class)

    return stem_class,word_stem

def get_word_class(word, word_pos, hw_df=en_hw_df):
    """
    Get headword class for a given word

    Parameters
    ----------
    word : string
        Word to be analyzed
    word_pos : string
        POS tag of the given word
    hw_df : pandas.DataFrame
        Record of headwords and corresponding classes

    Returns
    -------
    word_class : float
        Corresponding headword class or rank of the word
    """
    word_lemma = ""
    word_stem = ""

    # Default: if word is not found in the headwords list, assign a difficulty
    # level of 11
    word_class = 11.0

    # Extract the word's class
    if word in en_stopwords:
        word_class = 1.0
    else:
        word_class = get_headword_class(word, hw_df)

        if word_class == 11.0:
            # Use the word's stem and lemma to find the word's class
            stem_class,word_stem = get_stem_class(word, hw_df)
            lemma_class,word_lemma = get_lemma_class(word, word_pos, hw_df)

            word_class = float(min(stem_class, lemma_class))

    # print(f"{word} : {word_pos} : {word_stem} : {word_lemma} : {word_class}")

    return word_class

def is_in_dale_list(word, word_pos):
    bool_in_dale = False 

    if (dale_df['word'].eq(word.lower())).any():
        bool_in_dale = True
    elif word.isnumeric():
        # number
        bool_in_dale = True
    elif word.endswith("en"):
        # misc: word ending in "en"
        bool_in_dale = False
    elif word_pos == "NNP":
        # noun
        check_ner = [ent.label_ for ent in nlp(word).ents]
        if check_ner:
            word_ner = check_ner[0]
            if word_ner and word_ner in ["PERSON", "GPE"]:
                bool_in_dale = True
    elif word_pos in ["VB", "VBD", "VBG", "VBN", "VBP", "VBZ"]:
        # verb
        word_lemma = lemmatizer.lemmatize(word.lower(), pos='v')
        if (dale_df['lemma_v'].eq(word_lemma)).any():
            bool_in_dale = True
    elif word_pos in ["JJ", "JJR", "JJS"]:
        # adjective
        if (dale_df['lemma_a'].eq(
            re.sub(r'e[rs]t?$', "", word.lower()))).any():
            # comparative or superlative
            bool_in_dale = True
        elif word.endswith("n"):
            word_lemma = word[:-1]
            word_lemma_pos = pos_tag([word_lemma])[0][1]
            if word_lemma_pos in ["NN", "NNP", "NNS"]:
                # formed from a noun
                bool_in_dale = True
    elif word_pos == "RB":
        # adverb
        if (dale_df['word'].eq(re.sub(r'ly$','',word.lower()))).any():
            bool_in_dale = True
    elif "-" in word:
        # hypenated word
        if all((dale_df['word'].eq(w)).any() 
               for w in re.sub("-", " ", word.lower()).split()):
            bool_in_dale = True
    
    return bool_in_dale

def limit_text_by_word_count(text, count_limit = 100, is_save = True):
    """
    Truncate text based on a word count limit

    Parameters
    ----------
    text : string
        Transcript to be processed
    count_limit : int
        Target word count of the truncated text. Default is 100 words
    is_save : boolean
        Option to keep complete sentences when a word count limit is imposed.
        This means that if the limit cuts the text in the middle of the
        sentence and this option is True, then the entire sentence will still
        be included in the truncated text instead.

    Returns
    -------
    limited_text : string
        Truncated text
    """

    if is_save:
        current_count = 0
        limited_text = ""

        sentences = re.findall(r'\b[^.!?]+[.!?]*', text, re.UNICODE)

        for sentence in sentences:
            limited_text = limited_text + " " + sentence
            current_count = ts.lexicon_count(limited_text)

            if current_count >= count_limit:
                break
    else:
        limited_text = " ".join(text.split()[:count_limit])

    return limited_text

def remove_punctuation(text):
    """
    Remove punctuations from text

    Parameters
    ----------
    text : string
        Transcript to be processed

    Returns
    -------
    text : string
        Cleaned version of the text
    """
    punctuation_regex = r"[^\w\s\']"

    text = re.sub(r"\'(?![tsd]\b|ve\b|ll\b|re\b|m\b)", '"', text)
    text = re.sub(punctuation_regex, " ", text)
    text = " ".join(text.split())

    return text

def run_voa_example():
    data_name = "voa"
    sys_name = "ka5"
    header = [
        "id", "sent_count", "syll_count", "word_count", 
        "miniw_count", "monosyll_count", "not_in_dale_count", 
        "ave_sent_len", "ave_word_len"
    ]

    transcripts_map = {
        'gws': "voa-1000_google-web_T-chunks_T-period_hyp.txt",
        'ka5': "voa-1000_kaldi-aspire_Tr-chunks_hyp.txt"
    }

    main_dir = join("data", data_name)

    if sys_name in ["actual"]:
        is_split = False
        is_punct = False
        is_sample = False
        is_limit = False
        count_limit = 100
        is_save = True

        texts_dir = join(main_dir, "processed/transcripts")
    elif sys_name in ["ka5", "gws"]:
        is_split = True
        is_punct = True
        is_sample = False
        is_limit = False
        count_limit = 100
        is_save = True
        
        transcript_dir = join(
            main_dir, join("processed/asr",system_map[sys_name])
        )
        transcript_file = transcripts_map[sys_name]
        transcript_path = join(transcript_dir, transcript_file)
    
    results_dir = join(
        main_dir, join("results/readability",system_map[sys_name])
    )
    makedirs(results_dir, exist_ok = True)

    scores_file = f"content_feats_{data_name}_{sys_name}_{str(is_split)[:1]}-chunks_{str(is_punct)[:1]}-punct_{str(is_sample)[:1]}-samp_{str(is_limit)[:1]}-limit_{str(is_save)[:1]}-save.csv"
    scores_path = join(results_dir, scores_file)

    with open(scores_path, mode = 'w') as scores_f:
        score_writer = csv.writer(scores_f, delimiter=',')
        score_writer.writerow(header)

        if sys_name in ["actual"]:
            compute_from_dir(
                texts_dir, 
                score_writer, 
                is_punct = is_punct, 
                is_limit = is_limit, 
                count_limit = count_limit, 
                is_save = is_save
            )
        elif sys_name in ["gws", "ka5"]:
            compute_from_list(
                transcript_path, 
                score_writer, 
                is_punct = is_punct, 
                is_limit = is_limit, 
                count_limit = count_limit, 
                is_save = is_save
            )
        else:
            print("Please specify valid system name")

def main():
    run_voa_example()

if __name__ == "__main__":
    main()

