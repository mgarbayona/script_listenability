import compare_scores
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from os.path import join

levels_bins_map = dict({'DCR': [*range(0,12)],
                        'FRE': [*range(0,12)],
                        'LW': [*range(30,95,5)],
                        'MER': [*range(0,5)]})
levels_probs_map = dict({'DCR': np.linspace(0,0.5,6),
                         'FRE': np.linspace(0,0.4,5),
                         'LW': np.linspace(0,0.5,6),
                         'MER': np.linspace(0,0.7,8)})
boxplot_xtick_map = dict({'DCR': [*range(5,15,2)],
                          'FEL': [*range(0,21)],
                          'ELFC': [*range(0,21)],
                          'ELFP': [*range(0,21)],
                          'FRE': [*range(0,110,10)],
                          'LLD': [*range(0,7)],
                          'LW': [*range(30,95,5)],
                          'MER': [*range(0,45,5)],
                          'RL': [*range(0,15)]})
scores_bins_map = dict({'DCR': [*range(5,14)],
                        'FEL': [*range(0,21)],
                        'ELFC': [*range(0,21)],
                        'ELFP': [*range(0,21)],
                        'FRE': [0, 10, 30, *range(50,110,10)],
                        'LLD': [*range(0,7)],
                        'LW': [*range(30,95,5)],
                        'MER': [0, 21, 26, 30, 40],
                        'RL': [*range(0,15)]})
scores_probs_map = dict({'DCR': np.linspace(0,0.16,5),
                         'FEL': np.linspace(0,0.08,5),
                         'ELFC': np.linspace(0,0.2,5),
                         'ELFP': np.linspace(0,0.25,6),
                         'FRE': np.linspace(0,0.016,5),
                         'LLD': np.linspace(0,0.6,4),
                         'LW': np.linspace(0,0.03,7),
                         'MER': np.linspace(0,0.06,7),
                         'RL': np.linspace(0,0.16,5)})
cat_bins_map = dict({'DCR': [*range(-4,5)],
                     'FRE': [*range(-5,6)],
                     'LW': [*range(-15,16)],
                     'MER': [*range(-4,5)]})
cat_counts_map = dict({'DCR': [*range(0,1000,200)],
                       'FRE': [*range(0,800,200)],
                       'LW': [*range(0,250,50)],
                       'MER': [*range(0,450,50)]})
cat_probs_map = dict({'DCR': np.linspace(0,0.8,5),
                      'FRE': np.linspace(0,0.6,7),
                      'LW': np.linspace(0,0.5,6),
                      'MER': np.linspace(0,0.4,5)})
title_map = dict({'DCR': "Dale–Chall Readability Formula",
                  'FEL': "Fang Easy Listening",
                  'ELFC': "Fang Easy Listening (cainesap)",
                  'ELFP': "Fang Easy Listening (pyphen)",
                  'FRE': "Flesch Reading-Ease",
                  'LLD': "Lin Lexical Difficulty",
                  'LW': "Lensear Write",
                  'MER': "McAlpine EFLAW(TM) Readability",
                  'RL': "Rogers Listenability Formula"})
xtick_map = dict({'DCR': [*range(0,600,100)],
                  'FRE': [*range(0,600,100)],
                  'LW': [*range(0,300,50)],
                  'MER': [*range(0,800,100)]})
voa_levels = ["beginner", "intermediate", "advanced"]

readability_list = ["DCR", "FRE", "LW", "MER"]
listenability_list = ["FEL", "ELFC", "ELFP", "LLD", "RL"]

def generate_boxplots(scores_df, results_dir):
    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(12,6))

    for n, key in enumerate(title_map.keys()):
        i, j = divmod(n, 2)
        subfig = sns.boxplot(x=key,
                             y="LEVEL",
                             data=scores_df,
                             ax=axes[i, j],
                             palette="Greys",
                             hue="LEVEL",
                             notch=True,
                             dodge=False)

        subfig.legend().set_visible(False)
        subfig.set_xlabel("readability score", fontsize = 16)
        subfig.set_xlim(boxplot_xtick_map[key][0],boxplot_xtick_map[key][-1])

        subfig.tick_params(left=False, axis='both', which='major', labelsize=16)
        subfig.set(yticklabels=[])
        subfig.set_ylabel(key, fontsize = 16)


    handles, labels = fig.axes[-1].get_legend_handles_labels()
    subfig.legend(handles[::-1],
                  labels[::-1],
                  loc='lower right',
                  bbox_to_anchor =(1, -0.01),
                  fontsize = 12,
                  ncol = 1)

    fig.tight_layout()

    # plt.show()
    plt.savefig(results_dir + "/merged-box.png", dpi=600)
    plt.clf()

def generate_boxplots_scores_downloaded():
    scores_dir = "data/voa/results/202207_slt/readability/downloaded"
    scores_file = "readability_voa_no-asr_F-chunks_F-punct_T-limit-text_T-save-sntnc.csv"
    results_dir = scores_dir

    scores_path = join(scores_dir, scores_file)

    scores_df = pd.read_csv(scores_path)
    scores_df.columns = scores_df.columns.str.upper()
    scores_df['LEVEL'] = scores_df['ID'].str.strip().str[-1].astype(int)

    scores_df.loc[scores_df['LEVEL'] == 1, 'LEVEL'] = "beginner"
    scores_df.loc[scores_df['LEVEL'] == 2, 'LEVEL'] = "intermediate"
    scores_df.loc[scores_df['LEVEL'] == 3, 'LEVEL'] = "advanced"

    generate_boxplots(scores_df, results_dir)

def generate_histograms_levels():
    orig_scores_df,kaldi_scores_df,google_scores_df = load_voa_data()

    orig_scores_df = compare_scores.map_to_levels(orig_scores_df)
    kaldi_scores_df = compare_scores.map_to_levels(kaldi_scores_df)
    google_scores_df = compare_scores.map_to_levels(google_scores_df)

    orig_scores_df.to_csv("voa_orig.csv")
    kaldi_scores_df.to_csv("voa_kaldi.csv")
    google_scores_df.to_csv("voa_google.csv")

    fig, axes = \
        plt.subplots(ncols=len(title_map.keys()), nrows=3, figsize=(9,9))

    for n, key in enumerate(title_map.keys()):
        i, j = divmod(n, 4)

        metric = key + " cat"
        metric_bins = [x - 0.5 for x in cat_bins_map[key]]

        subfig = sns.histplot(data=orig_scores_df,
                              x=metric,
                              bins=levels_bins_map[key],
                              stat="probability",
                              color="gray",
                              ax=axes[0, j])
        # subfig.set_xlim(cat_bins_map[key][0],cat_bins_map[key][-1])
        subfig.set_ylim(levels_probs_map[key][0],levels_probs_map[key][-1])
        subfig.set_ylabel("")
        subfig.set_xlabel("")
        subfig.set_title(key)
        if j == 0:
            subfig.set_ylabel("VOA")

        heights = [h.get_height() for h in subfig.patches]
        print("VOA: Sum for %s is %4.4f" % (key, sum(heights)))

        subfig = sns.histplot(data=kaldi_scores_df,
                              x=metric,
                              bins=levels_bins_map[key],
                              stat="probability",
                              color="gray",
                              ax=axes[1, j])
        # subfig.set_xlim(cat_bins_map[key][0],cat_bins_map[key][-1])
        subfig.set_ylim(levels_probs_map[key][0],levels_probs_map[key][-1])
        subfig.set_ylabel("")
        subfig.set_xlabel("")
        if j == 0:
            subfig.set_ylabel("KA")

        heights = [h.get_height() for h in subfig.patches]
        print("Kaldi: Sum for %s is %4.4f" % (key, sum(heights)))

        subfig = sns.histplot(data=google_scores_df,
                              x=metric,
                              bins=levels_bins_map[key],
                              stat="probability",
                              color="gray",
                              ax=axes[2, j])
        # subfig.set_xlim(cat_bins_map[key][0],cat_bins_map[key][-1])
        # subfig.set_xlim(cat_counts_map[key][0],cat_counts_map[key][-1])
        subfig.set_ylim(levels_probs_map[key][0],levels_probs_map[key][-1])
        subfig.set_ylabel("")
        subfig.set_xlabel("")
        if j == 0:
            subfig.set_ylabel("GWS")

        heights = [h.get_height() for h in subfig.patches]
        print("Google: Sum for %s is %4.4f" % (key, sum(heights)))
        print(heights)

    fig.supxlabel("readability level", fontsize = 12)
    fig.supylabel("normalised count", fontsize = 12)
    fig.tight_layout()
    # plt.show()

    plt.savefig(join(main_dir, "hist_levels.png"), dpi=600)
    plt.clf()

def generate_histograms_levels_difference():
    orig_scores_df,kaldi_scores_df,google_scores_df = load_voa_data()

    orig_scores_df = compare_scores.map_to_levels(orig_scores_df)
    kaldi_scores_df = compare_scores.map_to_levels(kaldi_scores_df)
    google_scores_df = compare_scores.map_to_levels(google_scores_df)

    # DF2 - DF1
    kaldi_orig_diff_df = \
        compare_scores.compare_levels(orig_scores_df, kaldi_scores_df)
    google_orig_diff_df = \
        compare_scores.compare_levels(orig_scores_df, google_scores_df)
    kaldi_google_diff_df = \
        compare_scores.compare_levels(google_scores_df, kaldi_scores_df)

    fig, axes = \
        plt.subplots(nrows=len(title_map.keys()), ncols=3, figsize=(9,9))

    for n, key in enumerate(title_map.keys()):
        i, j = divmod(n, 4)

        metric = key + " cat"
        metric_bins = [x - 0.5 for x in cat_bins_map[key]]

        subfig = sns.histplot(data=kaldi_orig_diff_df,
                              x=metric,
                              bins=metric_bins,
                              stat="probability",
                              color="gray",
                              ax=axes[j,0])
        subfig.set_xlim(cat_bins_map[key][0],cat_bins_map[key][-1])
        # subfig.set_xlim(cat_counts_map[key][0],cat_counts_map[key][-1])
        subfig.set_ylim(cat_probs_map[key][0],cat_probs_map[key][-1])
        subfig.set_ylabel(key)
        subfig.set_xlabel("")
        # subfig.set_title(key)
        if j == 0:
            subfig.set_title("KA - VOA")

        subfig = sns.histplot(data=google_orig_diff_df,
                              x=metric,
                              bins=metric_bins,
                              stat="probability",
                              color="gray",
                              ax=axes[j,1])
        subfig.set_xlim(cat_bins_map[key][0],cat_bins_map[key][-1])
        # subfig.set_xlim(cat_counts_map[key][0],cat_counts_map[key][-1])
        subfig.set_ylim(cat_probs_map[key][0],cat_probs_map[key][-1])
        subfig.set_ylabel("")
        subfig.set_xlabel("")
        if j == 0:
            subfig.set_title("GWS - VOA")

        subfig = sns.histplot(data=kaldi_google_diff_df,
                              x=metric,
                              bins=metric_bins,
                              stat="probability",
                              color="gray",
                              ax=axes[j, 2])
        subfig.set_xlim(cat_bins_map[key][0],cat_bins_map[key][-1])
        # subfig.set_xlim(cat_counts_map[key][0],cat_counts_map[key][-1])
        subfig.set_ylim(cat_probs_map[key][0],cat_probs_map[key][-1])
        subfig.set_ylabel("")
        subfig.set_xlabel("")
        if j == 0:
            subfig.set_title("KA - GWS")

    fig.supxlabel("level difference", fontsize = 12)
    fig.supylabel("normalised counts", fontsize = 12)
    fig.tight_layout()
    # plt.show()

    plt.savefig(join(main_dir, "hist_level-diff.png"), dpi=600)
    plt.clf()

def generate_histograms_scores():
    orig_scores_df,kaldi_scores_df,google_scores_df = load_voa_data()

    fig, axes = \
        plt.subplots(ncols=len(title_map.keys()), nrows=3, figsize=(9,9))

    for n, key in enumerate(title_map.keys()):
        i, j = divmod(n, 4)

        subfig = sns.histplot(data=orig_scores_df,
                              x=key,
                              bins=scores_bins_map[key],
                              stat="probability",
                              color="gray",
                              ax=axes[0, j])
        # subfig.set_xlim(cat_bins_map[key][0],cat_bins_map[key][-1])
        subfig.set_ylim(scores_probs_map[key][0],scores_probs_map[key][-1])
        subfig.set_ylabel("")
        subfig.set_xlabel("")
        subfig.set_title(key)
        if j == 0:
            subfig.set_ylabel("VOA")

        heights = [h.get_height() for h in subfig.patches]
        print("VOA: Sum for %s is %4.4f" % (key, sum(heights)))
        print(heights)

        subfig = sns.histplot(data=kaldi_scores_df,
                              x=key,
                              bins=scores_bins_map[key],
                              stat="probability",
                              color="gray",
                              ax=axes[1, j])
        # subfig.set_xlim(cat_bins_map[key][0],cat_bins_map[key][-1])
        subfig.set_ylim(scores_probs_map[key][0],scores_probs_map[key][-1])
        subfig.set_ylabel("")
        subfig.set_xlabel("")
        if j == 0:
            subfig.set_ylabel("KA")

        heights = [h.get_height() for h in subfig.patches]
        print("Kaldi: Sum for %s is %4.4f" % (key, sum(heights)))
        print(heights)

        subfig = sns.histplot(data=google_scores_df,
                              x=key,
                              bins=scores_bins_map[key],
                              stat="probability",
                              color="gray",
                              ax=axes[2, j])
        # subfig.set_xlim(cat_bins_map[key][0],cat_bins_map[key][-1])
        # subfig.set_xlim(cat_counts_map[key][0],cat_counts_map[key][-1])
        subfig.set_ylim(scores_probs_map[key][0],scores_probs_map[key][-1])
        subfig.set_ylabel("")
        subfig.set_xlabel("")
        if j == 0:
            subfig.set_ylabel("GWS")

        heights = [h.get_height() for h in subfig.patches]
        print("Google: Sum for %s is %4.4f" % (key, sum(heights)))
        print(heights)


    fig.supxlabel("readability score", fontsize = 12)
    fig.supylabel("normalised count", fontsize = 12)
    fig.tight_layout()
    # plt.show()

    plt.savefig(join(main_dir, "hist_scores.png"), dpi=600)
    plt.clf()

def generate_mixed_plots():
    orig_scores_df,kaldi_scores_df,google_scores_df = load_voa_data()

    metrics = \
        list(set(title_map.keys()).intersection(orig_scores_df.columns.values))
    metrics.sort()
    
    read_metrics = list(set(readability_list).intersection(metrics))
    listen_metrics = list(set(listenability_list).intersection(metrics))
    read_metrics.sort()
    listen_metrics.sort()
    metrics = read_metrics + listen_metrics

    fig, axes = \
        plt.subplots(ncols=len(metrics), nrows=4, figsize=(25,12))

    for n, key in enumerate(metrics):
        i, j = divmod(n, 6)

        # Grouped boxplot of readability scores from actual transcripts
        subfig = sns.boxplot(data=orig_scores_df,
                             x=key,
                             y="LEVEL",
                             notch=True,
                             dodge=False,
                             ax=axes[0, j],
                             hue="LEVEL")

        subfig.legend().set_visible(False)
        subfig.set_xlim(boxplot_xtick_map[key][0],boxplot_xtick_map[key][-1])

        if key in ["FEL", "ELFC", "ELFP", "LW", "RL"]:
            subfig.set_xticks(scores_bins_map[key][::2])
        else:
            subfig.set_xticks(scores_bins_map[key])
        subfig.set(xticklabels=[])

        subfig.tick_params(left=False,
                           axis='both',
                           which='major')
        subfig.set(yticklabels=[])

        subfig.set_xlabel("")
        if j == 0:
            subfig.set_ylabel("VOA")
        else:
            subfig.set_ylabel("")
        subfig.set_title(key)

        subfig.xaxis.grid(linestyle="dashed")
        subfig.set_axisbelow(True)

        # Histogram of readability scores from actual transcripts
        # subfig = sns.histplot(data=orig_scores_df,
        #                       x=key,
        #                       bins=scores_bins_map[key],
        #                       hue="LEVEL",
        #                       stat="probability",
        #                       ax=axes[1, j],
        #                       legend=False)
        subfig = sns.kdeplot(data=orig_scores_df,
                              x=key,
                              hue="LEVEL",
                              ax=axes[1, j],
                              legend=False)
        subfig.set_xlim(scores_bins_map[key][0],scores_bins_map[key][-1])
        subfig.set_ylim(scores_probs_map[key][0],scores_probs_map[key][-1])
        subfig.set_yticks(scores_probs_map[key])

        # subfig.lines[0].set_color('crimson')

        if key in ["FEL", "ELFC", "ELFP", "LW", "RL"]:
            subfig.set_xticks(scores_bins_map[key][::2])
        else:
            subfig.set_xticks(scores_bins_map[key])
        subfig.set(xticklabels=[])

        subfig.set_xlabel("")
        if j == 0:
            subfig.set_ylabel("VOA")
        else:
            subfig.set_ylabel("")

        subfig.grid(linestyle="dashed")
        subfig.set_axisbelow(True)
        plt.legend([],[], frameon=False)
    

        # Histogram of readability scores from KA-based transcripts
        # Limit scores to empirically-determined range
        kaldi_scores_df[key] = np.clip(kaldi_scores_df[key],
                                scores_bins_map[key][0],
                                scores_bins_map[key][-1])

        # subfig = sns.histplot(data=kaldi_scores_df,
        #                       x=key,
        #                       bins=scores_bins_map[key],
        #                       multiple="stack",
        #                       hue="LEVEL",
        #                       stat="probability",
        #                       ax=axes[2, j],
        #                       legend=False)
        subfig = sns.kdeplot(data=kaldi_scores_df,
                              x=key,
                              hue="LEVEL",
                              ax=axes[2, j],
                              legend=False)

        subfig.set_xlim(scores_bins_map[key][0],scores_bins_map[key][-1])
        subfig.set_ylim(scores_probs_map[key][0],scores_probs_map[key][-1])
        subfig.set_yticks(scores_probs_map[key])


        # subfig.lines[0].set_color('crimson')

        if key in ["FEL", "ELFC", "ELFP", "LW", "RL"]:
            subfig.set_xticks(scores_bins_map[key][::2])
        else:
            subfig.set_xticks(scores_bins_map[key])
        subfig.set(xticklabels=[])

        subfig.set_xlabel("")
        if j == 0:
            subfig.set_ylabel("KA")
        else:
            subfig.set_ylabel("")

        subfig.grid(linestyle="dashed")
        subfig.set_axisbelow(True)
        plt.legend([],[], frameon=False)
    

        # Histogram of readability scores from GWS-based transcripts
        google_scores_df[key] = np.clip(google_scores_df[key],
                                scores_bins_map[key][0],
                                scores_bins_map[key][-1])

        # subfig = sns.histplot(data=google_scores_df,
        #                       x=key,
        #                       bins=scores_bins_map[key],
        #                       multiple="stack",
        #                       hue="LEVEL",
        #                       stat="probability",
        #                       ax=axes[3, j],
        #                       legend=False)
        subfig = sns.kdeplot(data=google_scores_df,
                              x=key,
                              hue="LEVEL",
                              ax=axes[3, j],
                              legend=False)

        subfig.set_xlim(scores_bins_map[key][0],scores_bins_map[key][-1])
        subfig.set_ylim(scores_probs_map[key][0],scores_probs_map[key][-1])
        subfig.set_yticks(scores_probs_map[key])

        # subfig.lines[0].set_color('crimson')

        if key in ["FEL", "ELFC", "ELFP", "LW", "RL"]:
            subfig.set_xticks(scores_bins_map[key][::2])
        else:
            subfig.set_xticks(scores_bins_map[key])

        if key in ["FEL", "ELFC", "ELFP", "LLD", "LW", "MER", "RL"]:
            # Remove maximum value label
            plt.setp(axes[3, j].get_xticklabels()[-1], visible=False)

        subfig.set_xlabel("")
        if j == 0:
            subfig.set_ylabel("GWS")
        else:
            subfig.set_ylabel("")

        subfig.grid(linestyle="dashed")
        subfig.set_axisbelow(True)
        plt.legend([],[], frameon=False)
    


    fig.supxlabel("listenability score", fontsize = 12)
    fig.supylabel("distribution",
                  fontsize = 12,
                  x = 0.01,
                  y = 0.64)
    fig.tight_layout()
    
    handles, labels = fig.axes[0].get_legend_handles_labels()
    
    fig.legend(handles[::-1],
               labels[::-1],
               loc="lower center",
               bbox_to_anchor=(0.85, 0),
               ncol=3)

    # plt.show()
    main_dir = "data/voa/results/conf_report"
    plt.savefig(join(main_dir, "mixed_plots.png"), dpi=600)
    # plt.clf()

def load_voa_data():
    # main_dir = "data/voa/results/20220715_slt/readability"
    # orig_dir = join(main_dir, "actual")
    # orig_file = "readability_voa_no-asr_F-chunks_F-punct_T-limit-text_T-save-sntnc.csv"
    #
    # kaldi_dir = join(main_dir, "kaldi-aspire")
    # kaldi_file = "readability_voa_kaldi_T-chunks_T-punct_T-limit-text_T-save-sntnc.csv"
    #
    # google_dir = join(main_dir, "google-web-speech")
    # google_file = "readability_voa_google-norm_T-chunks_T-punct_T-limit-text_T-save-sntnc.csv"

    main_dir = "data/voa/results/conf_report"
    orig_file = "formulae_voa_actual_scores.csv"

    google_file = "formulae_voa_gws_scores.csv"

    kaldi_file = "formulae_voa_ka5_scores.csv"

    orig_scores_df = compare_scores.get_scores_df(main_dir, orig_file)
    kaldi_scores_df = compare_scores.get_scores_df(main_dir, kaldi_file)
    google_scores_df = compare_scores.get_scores_df(main_dir, google_file)

    orig_scores_df = get_voa_levels(orig_scores_df)
    kaldi_scores_df = get_voa_levels(kaldi_scores_df)
    google_scores_df = get_voa_levels(google_scores_df)

    return orig_scores_df,kaldi_scores_df,google_scores_df

def get_voa_levels(scores_df):
    scores_df['LEVEL'] = scores_df['ID'].str.strip().str[-1].astype(int)

    scores_df.loc[scores_df['LEVEL'] == 1, 'LEVEL'] = "beginner"
    scores_df.loc[scores_df['LEVEL'] == 2, 'LEVEL'] = "intermediate"
    scores_df.loc[scores_df['LEVEL'] == 3, 'LEVEL'] = "advanced"

    return scores_df

def main():
    generate_mixed_plots()

if __name__ == "__main__":
    main()
