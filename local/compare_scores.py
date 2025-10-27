import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import researchpy as rp

from os.path import join

bins_map = dict({'DCR': [0, *range(5,12)],
                 'FEL': [*range(0,21)],
                 'FKGL': [*range(0,19)],
                 'FRE': [-40, 0, 10, 30, *range(50,120,10)],
                 'LW': [*range(0,110,10)],
                 'MER': [0, 21, 26, 30, 35],
                 'RL': [*range(0,19)]})
title_map = dict({'DCR': "Dale–Chall Readability Formula",
                  'FEL': "Fang Easy Listening",
                  'FKGL': "Flesch–Kincaid Grade Level",
                  'FRE': "Flesch Reading-Ease",
                  'LW': "Linsear Write",
                  'MER': "McAlpine EFLAW(TM) Readability"})
voa_levels = dict({'1': "beginner",
                   '2': "intermediate",
                   '3': "advanced"})
elllo_levels = dict({'1': "low beg",
                     '2': "mid beg",
                     '3': "high beg",
                     '4': "low int",
                     '5': "mid int",
                     '6': "high int",
                     '7': "adv"})

def compare_levels(df1, df2):
    """
    Compare categorical assignments of two assessments

    Parameters
    ----------
    df1 : pandas.DataFrame
        Scores from first assessment
    df2 : pandas.DataFrame
        Scores from second assessment

    Returns
    -------
    diff_df : pandas.DataFrame
        Differences of scores between the two assessments (df2 - df1)
    """
    diff_df = df2.set_index('ID').subtract(df1.set_index('ID'))
    diff_df.reset_index(inplace=True)
    diff_df['LEVEL'] = diff_df['ID'].str.strip().str[-1].astype(int)

    metrics = list(set(title_map.keys()).intersection(df1.columns.values))

    for metric in metrics:
        col_name = metric + ' cat'
        diff_stats = diff_df[col_name].value_counts().sort_index()
        count = diff_stats.sum()
        diff_stats = diff_stats.to_dict()

        # Calculate mean level difference
        diffs = np.fromiter(diff_stats.keys(), dtype=float)
        diff_counts = np.fromiter(diff_stats.values(), dtype=float)
        mean_diff = np.sum(np.multiply(diffs, diff_counts))/np.sum(diff_counts)
        print(diff_stats)
        print(mean_diff)

        # Calculate percentage of cases where levels are the same
        correct_ratio = diff_stats.get(0, 0)/count

        # Calculate percentage of cases where levels differ by at most one level
        one_diff_ratio = (diff_stats.get(0, 0) \
                         + diff_stats.get(1, 0) \
                         + diff_stats.get(-1, 0))/count

        # Report the result on the command line for easy reference
        print("%s %4.4f %4.4f" % (metric, correct_ratio, one_diff_ratio))

    return diff_df

def generate_stacked_histograms(scores_df, results_dir, level_labels):
    """
    Plot a stacked histogram with stacks representing the creator- or educator-
    assigned levels

    Parameters
    ----------
    scores_df : pandas.DataFrame
        Record of scores for each material
    results_dir : string
        Name of the directory where the stacked histogram will be stored
    level_labels : dict of {str : str}
        Mapping of assigned levels, from numerical to descriptive

    Returns
    -------
    None
    """
    metrics = list(set(title_map.keys()).intersection(scores_df.columns.values))

    for metric in metrics:
        col_name = metric + ' cat'
        num_bins = len(bins_map[metric])

        fig,ax = plt.subplots(1,1)
        # n,bins,patches = \
        #     plt.hist([scores_df.loc[scores_df['LEVEL'] == 1, col_name],
        #               scores_df.loc[scores_df['LEVEL'] == 2, col_name],
        #               scores_df.loc[scores_df['LEVEL'] == 3, col_name]],
        #               bins=np.arange(-num_bins,num_bins+1) - 0.5,
        #               rwidth=0.9,
        #               stacked=True,
        #               label=level_labels)

        n,bins,patches = \
            plt.hist([scores_df.loc[scores_df['LEVEL'] == 1, col_name],
                      scores_df.loc[scores_df['LEVEL'] == 2, col_name],
                      scores_df.loc[scores_df['LEVEL'] == 3, col_name],
                      scores_df.loc[scores_df['LEVEL'] == 4, col_name],
                      scores_df.loc[scores_df['LEVEL'] == 5, col_name],
                      scores_df.loc[scores_df['LEVEL'] == 6, col_name],
                      scores_df.loc[scores_df['LEVEL'] == 7, col_name]],
                      bins=np.arange(-num_bins,num_bins+1) - 0.5,
                      rwidth=0.9,
                      stacked=True,
                      label=level_labels)

        plt.xlabel("difference in levels")
        plt.ylabel("frequency")
        plt.title("Distribution of difference in " + title_map[metric] + " levels")
        plt.legend(loc="upper right")

        plt.xticks([*range(-(num_bins + (num_bins % 2) - 2),0,2),
                    *range(0,(num_bins + (num_bins % 2)),2)])
        # plt.setp(ax.get_xticklabels(), rotation=90, horizontalalignment='right')
        # plt.yticks(ytick_map[key])
        plt.grid(axis='y')

        plt.savefig(results_dir + "/" + metric + "_diff-level-stacked-hist.png")
        plt.clf()

def get_scores_df(scores_dir, scores_file):
    """
    Load scores from a given path (directory + filename)

    Parameters
    ----------
    scores_dir : string
        Name of the directory where the file of scores are stored
    scores_file : string
        Name of the CSV file containing the scores

    Returns
    -------
    scores_df : pandas.DataFrame
        Record of scores for each material
    """
    scores_path = join(scores_dir, scores_file)
    scores_df = pd.read_csv(scores_path)
    scores_df.columns = scores_df.columns.str.upper()

    scores_df = map_to_levels(scores_df)

    return scores_df

def map_to_levels(scores_df):
    """
    Map raw scores to numerical levels

    Parameters
    ----------
    scores_df : pandas.DataFrame
        Record of raw scores for each material

    Returns
    -------
    scores_df : pandas.DataFrame
        Record of raw scores and corresponding numerical levels for each
        material
    """
    metrics = list(set(title_map.keys()).intersection(scores_df.columns.values))

    for metric in metrics:
        col_name = metric + ' cat'
        bins = bins_map[metric]
        bins[-1] = np.inf
        labels = [*range(0,len(bins)-1)]
        if metric == "FRE":
            labels = labels[::-1]

        scores_df[col_name] = pd.to_numeric(pd.cut(scores_df[metric],
                                                   bins,
                                                   labels=labels))

    return scores_df

def run_elllo_example():
    """
    Sample run with scores on ELLLO materials
    """
    scores1_dir = "data/elllo/results/no-asr_F-chunks_F-punct_F-limit_F-save"
    scores1_file = "listenability-pyphen_elllo_no-asr_F-chunks_F-punct_F-limit-text_F-save-sntnc.csv"
    scores1_df = get_scores_df(scores1_dir, scores1_file)

    scores2_dir = "data/elllo/results/no-asr_F-chunks_F-punct_F-limit_F-save"
    scores2_file = "listenability-cainesap_elllo_no-asr_F-chunks_F-punct_F-limit-text_F-save-sntnc.csv"
    scores2_df = get_scores_df(scores2_dir, scores2_file)

    diff_df = compare_levels(scores1_df, scores2_df)
    generate_stacked_histograms(diff_df, \
                                scores1_dir, \
                                list(elllo_levels.values()))

def run_voa_example():
    """
    Sample run with scores on VOA Learning English materials
    """
    main_dir = "data/voa/results/20220715_slt/readability"
    scores1_dir = join(main_dir, "actual")
    scores1_file = "readability_voa_no-asr_F-chunks_F-punct_T-limit-text_T-save-sntnc.csv"
    scores1_df = get_scores_df(scores1_dir, scores1_file)

    scores2_dir = join(main_dir, "kaldi-aspire")
    scores2_file = "readability_voa_kaldi_T-chunks_T-punct_T-limit-text_T-save-sntnc.csv"
    # scores2_dir = join(main_dir, "google-web-speech")
    # scores2_file = "readability_voa_google-norm_T-chunks_T-punct_T-limit-text_T-save-sntnc.csv"
    scores2_df = get_scores_df(scores2_dir, scores2_file)

    diff_df = compare_levels(scores1_df, scores2_df)
    # generate_stacked_histograms(diff_df, scores1_dir, list(voa_levels.values()))

def main():
    # run_elllo_example()
    run_voa_example()

if __name__ == "__main__":
    main()
