import matplotlib.pyplot as plt
import re
import pandas as pd
import seaborn as sns

from compare_scores import get_scores_df
from os import makedirs
from os.path import join

script_map = dict({'actual': 'actual',
                   'gws': 'google-web-speech',
                   'ka5': 'kaldi-aspire-s5'})

label_map = dict({'actual': 'VOA',
                  'gws': 'GWS',
                  'ka5': 'KA'})

def plot_classifier_accuracies():
    results_dir = "data/voa/results"
    issc_dir = join(results_dir, "2023_issc")
    acc_list = []
    acc_df = pd.DataFrame()

    script_names = ["actual", "gws", "ka5"]
    clf_name = "3-way"

    for script in script_names:
        script_file = "_".join(["issc_voa", script, "lr-" + clf_name + ".csv"])
        script_path = join(issc_dir, script_file)

        script_acc_df = pd.read_csv(script_path)
        script_acc_df['script'] = label_map[script]
        acc_list.append(script_acc_df)
    
    acc_df = pd.concat(acc_list, ignore_index=True)
    acc_df['features'].replace(r"[()']", '', regex=True, inplace=True)
    acc_df['features'].replace(r",$", '', regex=True, inplace=True)
    
    fig, ax = plt.subplots()
 
    for key, group in acc_df.groupby('script'):
        plt.errorbar(x=group['features'], y=group['mean'], yerr=group['stdev'], 
                   label=key, fmt="o", elinewidth=1, capsize=2)
    
    if clf_name in ["2-way"]:
        plt.ylim(0.4, 0.9)
    else:
        plt.ylim(0.2, 0.7)
    plt.xlabel("features")
    plt.ylabel("classifier accuracy")
    plt.setp(ax.get_xticklabels(), rotation='vertical', fontsize=7)
    plt.grid(linestyle="dashed")
    
    h,l = ax.get_legend_handles_labels()
    plt.legend(h, l,
               loc='upper left')
    fig.tight_layout()
    
    # plt.show()
    plt.savefig(join(issc_dir, "lr_" + clf_name + ".png"), dpi=600)

def prepare_data():
    data_name = "voa"
    script_names = ["actual", "gws", "ka5"]
    # sys_names = ["readability", "listenability"]
    sys_names = ["readability"]

    results_dir = "data/voa/results"
    readability_dir = join(results_dir, "readability")
    listenability_dir = join(results_dir, "listenability")
    issc_dir = join(results_dir, "2023_issc")
    makedirs(issc_dir, exist_ok = True)

    for script_name in script_names:
        issc_file = "_".join(["issc", data_name, script_name, "scores.csv"])
        issc_path = join(issc_dir, issc_file)
        merged_df = pd.DataFrame()
        new_cols = []

        if script_name in ["actual"]:
            is_split = False
            is_punct = False
            is_sample = True
            is_limit = False
            is_save = True
        elif script_name in ["gws", "ka5"]:
            is_split = True
            is_punct = True
            is_sample = True
            is_limit = False
            is_save = True
        
        for sys_name in sys_names:
            if sys_name in ["readability"]:
                scores_dir = join(readability_dir, script_map[script_name])
                # scores_cols = ['UDCR', 'UFRE']
                scores_cols = ['UDCR', 'UFRE', 'ULW', 'UMER']
            else:
                scores_dir = join(listenability_dir, script_map[script_name])
                scores_cols = ['UELF_C', 'URLF']

            scores_file = sys_name + "_" \
                + data_name + "_" \
                + script_name + "_" \
                + str(is_split)[0] + "-chunks" + "_" \
                + str(is_punct)[0] + "-punct" + "_" \
                + str(is_sample)[0] + "-samp" + "_" \
                + str(is_limit)[0] + "-limit" + "_" \
                + str(is_save)[0] + "-save" \
                + ".csv"
            
            scores_df = get_scores_df(scores_dir, scores_file)
            
            if merged_df.empty:
                merged_df = scores_df[['ID'] + scores_cols]
            else:
                merged_df = pd.merge(merged_df, 
                                     scores_df[['ID'] + scores_cols],
                                     on='ID')
            
        for col in merged_df.columns:
            new_cols.append(re.sub(r'_[A-Z]$', "", re.sub(r'^U', "", col)))
        
        merged_df.columns = new_cols
        merged_df.to_csv(issc_path, index=False)

        print(issc_file)
        print(merged_df.max())

def main():
    # prepare_data()
    plot_classifier_accuracies()

if __name__ == "__main__":
    main()