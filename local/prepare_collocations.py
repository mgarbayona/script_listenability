import pandas as pd
import re

from os.path import join

def load_pte_file(collocations_path):
    collocations = []

    records_df = pd.read_csv(collocations_path, skiprows=1)

    collocations = \
        [re.sub(r'[()]', '', c1) + " " + re.sub(r'[()]', '', c2) 
         for (c1,c2) 
         in zip(records_df['Component I'].values.tolist(), 
                records_df['Component II'].values.tolist())]
    
    return collocations

def load_word_sketch_file(collocations_path):
    collocations = []

    records_df = pd.read_csv(collocations_path, skiprows=2)

    collocations = \
        [hw[:-2] + " " + c[:-2] 
         for (hw,c) 
         in zip(records_df['Headword'].values.tolist(), 
                records_df['Collocation'].values.tolist())]

    return collocations

def main():
    collocations_dir = "local/resources/collocations"
    pte_file = "2021_Teachers_AcademicCollocationList.csv"
    ws_file = "word_sketch_as_list_preloaded_sibol_corpus_20230307225029.csv"
    out_file = "en-collocations.txt"

    pte_path = join(collocations_dir, pte_file)
    pte_colls = load_pte_file(pte_path)

    ws_path = join(collocations_dir, ws_file)
    ws_colls = load_word_sketch_file(ws_path)

    collocations = list(set(pte_colls + ws_colls))
    collocations.sort()
    out_path = join(collocations_dir, out_file)
    with open(out_path, mode='w') as out_f:
        out_f.writelines("\n".join(collocations) + "\n")

if __name__ == "__main__":
    main()
