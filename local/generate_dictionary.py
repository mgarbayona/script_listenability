from g2p_en import G2p
from os.path import join

def get_entry(word):
    g2p = G2p()

    sequence = " ".join(g2p(word))

    # write entry following format in cmudict.0.7a
    entry = word + "  " + sequence

    return entry

def run_voa_example():
    list_dir = "data/voa/info"
    list_file = "voa_processed-transcript_words-not-in-cmu07a.txt"
    list_path = join(list_dir, list_file)

    dict_file = "voa_processed-transcript_words-not-in-cmu07a.dict"
    dict_path = join(list_dir, dict_file)

    with open(list_path, mode='r') as list_f, \
         open(dict_path, mode='w') as dict_f:
        print("Generating phoneme sequences...\n")
        for index, line in enumerate(list_f):
            word = line.strip()
            entry = get_entry(word)

            dict_f.write(entry + "\n")
        print("Done.")

def main():
    run_voa_example()

if __name__ == "__main__":
    main()
