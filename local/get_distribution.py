import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import ptitprince as pt
import seaborn as sns

from matplotlib.ticker import Locator
from os.path import join

bins_map = dict({'DCR': [0, *range(5,12)],
                 'FELC': [*range(0,21)],
                 'FELP': [*range(0,21)],
                 'FKGL': [*range(0,19)],
                 'FRE': [0, 10, 30, *range(50,120,10)],
                 'LLD': [*range(1,7)],
                 'LW': [*range(0,19)],
                 'MER': [0, 21, 26, 30, 35],
                 'RLF': [*range(0,19)],
                 'SR': np.arange(1.5,6.0,0.5),
                 'SRSD': np.arange(1.0,3.0,0.5),
                 'SRMAD': np.arange(0.5,2.5,0.5)})
title_map = dict({'DCR': "Dale–Chall Readability Formula",
                  'FELC': "Fang Easy Listening (cainesap)",
                  'FELP': "Fang Easy Listening (pyphen)",
                  'FKGL': "Flesch–Kincaid Grade Level",
                  'FRE': "Flesch Reading-Ease",
                  'LLD': "Lin Lexical Difficulty",
                  'LW': "Linsear Write",
                  'MER': "McAlpine EFLAW(TM) Readability",
                  'RLF': "Rogers Listenability Formula",
                  'SR': "Speaking Rate",
                  'SRSD': "Speaking Rate Standard Deviation",
                  'SRMAD': "Speaking Rate Mean Absolute Deviation"})
ytick_map = dict({'DCR': [*range(0,600,100)],
                  'FELC': [*range(0,250,50)],
                  'FELP': [*range(0,250,50)],
                  'FKGL': [*range(0,350,50)],
                  'FRE': [*range(0,600,100)],
                  'LLD': [*range(0,450,50)],
                  'LW': [*range(0,300,50)],
                  'MER': [*range(0,800,100)],
                  'RLF': [*range(0,350,50)],
                  'SR': np.arange(1.5,6.0,1.5)})
boxplot_ytick_map = dict({'DCR': [*range(0,11,2)],
                          'FELC': [*range(0,80,10)],
                          'FELP': [*range(0,70,10)],
                          'FKGL': [*range(0,21,2)],
                          'FRE': [*range(0,120,10)],
                          'LLD': [*range(0,7)],
                          'LW': [*range(0,21,2)],
                          'MER': [*range(0,55,5)],
                          'RLF': [*range(0,45,5)],
                          'SR': np.arange(1.5,5.0,0.5),
                          'SRSD': np.arange(1.0,3.0,0.5),
                          'SRMAD': np.arange(0.5,2.5,0.5)})
boxzoom_ytick_map = dict({'DCR': [*range(6,13)],
                          'FELC': [*range(0,30,5)],
                          'FELP': [*range(0,25,5)],
                          'FKGL': [*range(2,18,2)],
                          'FRE': [10, 30, *range(50,110,10)],
                          'LLD': [*range(0,7)],
                          'LW': [*range(3,18)],
                          'MER': [10, 21, 26, 30, 40],
                          'RLF': [*range(0,20,5)],
                          'SR': np.arange(1.5,6.0,1.5)})
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

def generate_boxplots(scores_df,
                      results_dir,
                      metrics,
                      level_labels,
                      plot_labels,
                      is_zoom=False):
    """
    Create boxplots for each metric listed in "metrics".

    Parameters
    ----------
    scores_df : pandas.DataFrame
        Record of comprehensibility (readability or listenability) scores for
        each material
    results_dir : string
        Directory where the boxplots will be saved
    metrics : list of str
        Comprehensibility metric scores that will be plotted
    plot_labels : dict of {str : str}
        Boxplot labels

    Returns
    -------
    None
    """
    xtick_values = np.sort(scores_df.LEVEL.unique())

    for metric in metrics:
        scores_df.boxplot(column=metric,
                          by=['LEVEL'])

        plt.xlabel(plot_labels['x'])
        plt.ylabel(plot_labels['y'])
        plt.title(title_map[metric])

        if is_zoom:
            plt.xticks(np.fromiter(level_labels.keys(), dtype=float),
                       list(level_labels.values()))
            plt.yticks(boxzoom_ytick_map[metric])
            plt.ylim(boxzoom_ytick_map[metric][0],
                     boxzoom_ytick_map[metric][-1])

            plt.savefig(results_dir + "/" + metric + "_boxplot-zoomed.png")
        else:
            # plt.xticks(np.fromiter(level_labels.keys(), dtype=float),
            #            list(level_labels.values()))
            plt.yticks(boxplot_ytick_map[metric])
            plt.ylim(boxplot_ytick_map[metric][0],
                     boxplot_ytick_map[metric][-1])

            plt.savefig(results_dir + "/" + metric + "_boxplot.png")

        plt.clf()

def generate_histograms(scores_df, results_dir, metrics, hist_x_label):
    for metric in metrics:
        fig,ax = plt.subplots(1,1)
        plt.hist(np.clip(scores_df[metric],
                         bins_map[metric][0],
                         bins_map[metric][-1]),
                 bins=bins_map[metric],
                 rwidth=0.9)

        plt.xlabel(hist_x_label)
        plt.ylabel("Frequency")
        plt.title("Distribution of " + title_map[metric] + " scores")

        plt.xticks(bins_map[metric][:-1])
        plt.yticks(ytick_map[metric])
        plt.grid(axis='y')

        xticklabels = [str(xtick) for xtick in bins_map[metric][:-1]]
        xticklabels[-1] += '+'
        ax.set_xticklabels(xticklabels)

        plt.savefig(results_dir + "/" + metric + "_score-hist.png")
        plt.clf()

def generate_grouped_rainclouds(scores_df,
                                results_dir,
                                metrics,
                                level_labels,
                                plot_labels,
                                is_zoom):
    pal = sns.color_palette('colorblind')

    for metric in metrics:
        fig,ax = plt.subplots(1,1)
        pt.RainCloud(data = scores_df,
                     x = 'LEVEL',
                     y = metric,
                     palette = pal,
                     box_notch = True)

        plt.ylabel(plot_labels['y'])
        plt.xlabel(plot_labels['x'])
        plt.title(title_map[metric])

        metric_xticks = np.fromiter(level_labels.keys(), dtype=float)-1
        plt.xlim(-0.75, max(metric_xticks) + 0.25)
        plt.xticks(metric_xticks,
                   list(level_labels.values()))

        if is_zoom:
            plt.yticks(boxzoom_ytick_map[metric])
            plt.ylim(boxzoom_ytick_map[metric][0],
                     boxzoom_ytick_map[metric][-1])

            plot_file = metric + "_raincloud-zoomed.png"

        else:
            plt.yticks(boxplot_ytick_map[metric])
            plt.ylim(boxplot_ytick_map[metric][0],
                     boxplot_ytick_map[metric][-1])

            plot_file = metric + "_raincloud.png"

        plt.grid(axis='y',
                 linestyle="dashed")

        fig.tight_layout()

        # plt.show()
        plot_path = join(results_dir, plot_file)
        plt.savefig(plot_path)

def generate_stacked_histograms(scores_df,
                                results_dir,
                                level_labels,
                                metrics,
                                hist_x_label):
    for metric in metrics:
        fig,ax = plt.subplots(1,1)

        levels = np.sort(scores_df.LEVEL.unique())
        scores = []

        for level in levels:
            scores.append(np.clip(scores_df.loc[scores_df['LEVEL'] == level,
                                                metric],
                                  bins_map[metric][0],
                                  bins_map[metric][-1]))

        plt.hist(scores,
                 bins=bins_map[metric],
                 rwidth=0.9,
                 stacked=True,
                 label=level_labels)

        plt.xlabel(hist_x_label)
        plt.ylabel("Frequency")
        plt.title("Distribution of " + title_map[metric] + " scores")
        plt.legend(loc="upper right")

        plt.xticks(bins_map[metric][:-1])
        plt.yticks(ytick_map[metric])
        plt.grid(axis='y')

        xticklabels = [str(xtick) for xtick in bins_map[metric][:-1]]

        xticklabels[-1] += '+'
        ax.set_xticklabels(xticklabels)

        plt.savefig(results_dir + "/" + metric + "_score-stacked-hist.png")
        plt.clf()

def run_elllo_example():
    """
    Sample run with scores on ELLLO materials
    """
    main_dir = "data/elllo"
    results_dir = join(main_dir, \
                       "results/speech")
    info_dir = join(main_dir, "info")

    scores_file = "elllo_speaking-rate-stats.csv"
    info_file = "elllo_speakers.csv"

    boxplot_labels = dict({'x': "no. of speakers",
                           'y': "deviation, syllables/sec"})

    scores_path = join(results_dir, scores_file)

    scores_df = pd.read_csv(scores_path)
    scores_df.columns = scores_df.columns.str.upper()

    info_path = join(info_dir, info_file)
    info_df = pd.read_csv(info_path)
    info_df.columns = info_df.columns.str.upper()

    scores_df = pd.merge(scores_df, info_df, on='ID')
    metrics = list(set(title_map.keys()).intersection(scores_df.columns.values))

    generate_boxplots(scores_df,
                      results_dir,
                      metrics,
                      voa_levels,
                      boxplot_labels)
    # generate_histograms(scores_df, results_dir, metrics, boxplot_labels['y'])
    # generate_stacked_histograms(scores_df,
    #                             results_dir,
    #                             list(elllo_levels.values()),
    #                             metrics,
    #                             boxplot_labels['y'])

def run_voa_example():
    """
    Sample run with scores on VOA Learning English materials
    """
    dataset = "voa"
    main_dir = join("data", dataset)
    results_dir = join(main_dir, "results/speech")
    info_dir = join(main_dir, "info")

    scores_file = "voa_speaking-rates.csv"
    info_file = "voa_level-info.csv"

    boxplot_labels = dict({'x': "VOA Level",
                           'y': "Speaking Rate, syllables/sec"})

    scores_path = join(results_dir, scores_file)

    scores_df = pd.read_csv(scores_path)
    scores_df.columns = scores_df.columns.str.upper()

    info_path = join(info_dir, info_file)
    info_df = pd.read_csv(info_path)
    info_df.columns = info_df.columns.str.upper()

    scores_df = pd.merge(scores_df, info_df, on='ID')
    metrics = list(set(title_map.keys()).intersection(scores_df.columns.values))
    metrics.sort()

    generate_boxplots(scores_df,
                      results_dir,
                      metrics,
                      voa_levels,
                      boxplot_labels,
                      is_zoom = False)
    # generate_boxplots(scores_df,
    #                   results_dir,
    #                   metrics,
    #                   voa_levels,
    #                   boxplot_labels,
    #                   is_zoom = True)
    # generate_histograms(scores_df, results_dir, metrics, boxplot_labels['y'])
    # generate_stacked_histograms(scores_df,
    #                             results_dir,
    #                             list(voa_levels.values()),
    #                             metrics,
    #                             boxplot_labels['y'])

    # generate_grouped_rainclouds(scores_df,
    #                             results_dir,
    #                             metrics,
    #                             voa_levels,
    #                             boxplot_labels,
    #                             is_zoom = True)

def main():
    run_elllo_example()
    # run_voa_example()

if __name__ == "__main__":
    main()
