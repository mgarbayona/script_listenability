import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import preparation as prep
import seaborn as sns
import utils

from os import makedirs
from os.path import dirname, join
from typing import Dict, List

def bottom_n_features(scores_df: pd.DataFrame, n_bottom: int = 3):
    scores_bottom_n = []

    for n in scores_df['n_features'].unique():
        df = scores_df.loc[scores_df['n_features'] == n]
        scores_bottom_n.append(df.nsmallest(n_bottom, 'median'))
        
    bottom_n_df = pd.concat(scores_bottom_n, ignore_index=True)

    return bottom_n_df

def error_bars(
    scores: Dict, 
    feature_col: str = 'features_str', 
    median_col: str = 'median', 
    lower_col: str = 'lower', 
    upper_col: str = 'upper', 
    score_type_col: str = 'score_type', 
    colors: str = None, 
    score_types: List = None, 
    offsets: List = None, 
):
    """
    Plot error bars for each score type, showing median and confidence 
    interval for each feature.
    
    Plots directly to the current axes.
    """
    if score_types is None:
        score_types = scores[score_type_col].unique()
    if offsets is None:
        offsets = {stype: 0 for stype in score_types}

    feature_labels = scores[feature_col].unique()
    x = np.arange(len(feature_labels))

    fig, axes = plt.subplots(
        nrows=1, ncols=1, figsize=(0.5*len(feature_labels), 6)
    )

    for score_type in score_types:
        d = scores[scores[score_type_col] == score_type]
        x_pos = np.array(
            [np.where(feature_labels == f)[0][0] for f in d[feature_col]]
        )
        x_pos = x_pos + offsets.get(score_type, 0)
        plt.errorbar(
            x_pos,
            d[median_col],
            yerr=[d[median_col] - d[lower_col], d[upper_col] - d[median_col]],
            fmt='o',
            capsize=5,
            label=score_type,
            color=colors[score_type] if colors else None
        )
    
    plt.xticks(x, feature_labels, rotation=90)
    plt.yticks(np.linspace(0.3, 1.0, 8))

    plt.xlabel('Features')
    plt.ylabel('Median (with CI)')

    if len(score_types) > 1:
        plt.legend(title='Score Type')

    plt.grid(True, which="major", axis="y", linestyle="--")
    plt.tight_layout()
    plt.show()

def grouped_box_features(
    scores_df: pd.DataFrame, 
    order: List = None, 
    save_path: str = None
):
    n_labels = scores_df['features_str'].nunique() if order is None else len(order)
    flip = n_labels > 20

    if order is None:
        median_by_feature = scores_df.groupby('features_str')['accs'].median()
        if not flip:
            median_by_feature = median_by_feature.sort_values(ascending=True)
        else:
            median_by_feature = median_by_feature.sort_values(ascending=False)
        feature_labels = median_by_feature.index.tolist()
    else:
        feature_labels = order

    # Format feature_labels for plotting
    formatted_labels = [
        prep.format_feature_label(label) for label in feature_labels
    ]

    palette = {}
    for label, formatted in zip(feature_labels, formatted_labels):
        n_feat = scores_df.loc[
            scores_df['features_str'] == label, 'n_features'
        ].iloc[0]
        palette[formatted] = "#009E73" if n_feat == 1 else "#D55E00"

    # Add a new column for formatted labels for plotting
    scores_df = scores_df.copy()
    scores_df['features_str_formatted'] = scores_df['features_str'].apply(
        prep.format_feature_label
    )

    if flip:
        figsize = (8, 0.25 * n_labels)
        x, y = 'accs', 'features_str_formatted'
        orient = 'h'
        box_width = 0.8
    else:
        figsize = (0.5 * n_labels, 6)
        x, y = 'features_str_formatted', 'accs'
        orient = 'v'
        box_width = 0.8

    fig, axes = plt.subplots(nrows=1, ncols=1, figsize=figsize)

    sns.boxplot(
        data=scores_df,
        x=x, y=y, hue='features_str_formatted',
        notch=True,
        order=formatted_labels,
        palette=palette,
        ax=axes,
        orient=orient,
        width=box_width, 
    )

    if flip:
        plt.xlim((0.2, 1.0))
        plt.xticks(np.linspace(0.2, 1.0, 9))
        plt.yticks(np.arange(n_labels), formatted_labels)
        plt.xlabel('Three-Way Classification Accuracy')
        plt.ylabel('Features')
    else:
        plt.xticks(np.arange(n_labels), formatted_labels, rotation=90)
        plt.yticks(np.linspace(0.2, 1.0, 9))
        plt.ylabel('Three-Way Classification Accuracy')
        plt.xlabel('Features')

    # Legend patches (no wrapping)
    single_patch = mpatches.Patch(
        color="#009E73", 
        label="Single-score feature set (n_features = 1)"
    )
    multi_patch = mpatches.Patch(
        color="#D55E00", 
        label="Multiple-score feature set (n_features > 1)"
    )

    plt.tight_layout()

    if flip:
        # Legend below the plot, centered, no text wrapping
        legend = fig.legend(
            handles=[single_patch, multi_patch],
            title="Feature Set Type",
            loc="lower center",
            bbox_to_anchor=(0.5, 0.0),  # Try -0.12 or lower if needed
            borderaxespad=0,
            ncol=2,
            frameon=True
        )
        legend.get_frame().set_alpha(0.8)
        plt.subplots_adjust(bottom=0.06)  # Increase as needed

    else:
        plt.legend(
            handles=[single_patch, multi_patch],
            title="Feature Set Type",
            loc="lower right"
        )

    plt.grid(True, which="major", axis="x" if flip else "y", linestyle="--")

    if save_path:
        plt.savefig(save_path, dpi=300)

    plt.show()

def grouped_box_nfeatures_typescore(scores: Dict, save_path: str = None):
    # Concatenate all DataFrames in the scores dict, adding a score_type column
    dfs = []
    for score_type, df in scores.items():
        df = df.copy()
        df['score_type'] = score_type
        dfs.append(df)
    all_scores = pd.concat(dfs, ignore_index=True)

    # Set color palette using mapper_voa_transcript_to_color from utils.py
    palette = utils.mapper_voa_transcript_to_color

    # Set width and dodge for more separation among boxplots at each x value
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.boxplot(
        data=all_scores,
        x='n_features',
        y='accs',
        hue='score_type',
        notch=True,
        ax=ax,
        palette=palette,
        gap=0.2,
    )

    ax.set_title("Boxplot by Number of Features and Transcript Type")
    ax.set_xlabel("Number of Features")
    ax.set_ylabel("Two-Way Classification Accuracy")

    ax.grid(True, which="major", axis="y", linestyle="--")

    # Replace legend labels with pretty labels when available
    handles, labels = ax.get_legend_handles_labels()
    pretty = [utils.pretty_labels.get(l, l) for l in labels]
    ax.legend(handles, pretty, title="Transcript", loc="lower right")

    plt.yticks(np.linspace(0.1, 1.0, 10))

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300)

    plt.show()

def line_accuracies(
    accuracies: Dict[str, pd.DataFrame],
    features_col: str = "features",
    mean_col: str = "mean",
    stdev_col: str = "stdev",
    figsize: tuple = (10, 6),
    save_path: str = None,
):
    """
    Plot line chart of accuracies for multiple score types.
    - accuracies: dict mapping legend label -> DataFrame
      Each DataFrame must contain columns named by features_col, mean_col, stdev_col.
    - Dots represent the 'mean' values; error bars use 'stdev'.
    - X-axis labels come from the 'features' column (union, order preserved).
    """
    # Build ordered union of feature labels (preserve first appearance)
    seen = []
    for df in accuracies.values():
        for f in df[features_col].astype(str).tolist():
            if f not in seen:
                seen.append(f)
    feature_labels = seen
    x_ticks = np.arange(len(feature_labels))

    sns.set_style("whitegrid")
    fig, ax = plt.subplots(figsize=figsize)

    # color palette
    palette = sns.color_palette(n_colors=len(accuracies))
    palette_map = {k: palette[i] for i, k in enumerate(accuracies.keys())}

    for key, df in accuracies.items():
        df = df.copy()
        # ensure features are strings
        df[features_col] = df[features_col].astype(str)
        # determine x positions for this dataframe
        x_pos = [feature_labels.index(f) for f in df[features_col]]

        pretty_label = utils.pretty_labels.get(key, key)

        # plot markers only (no connecting lines)
        sns.scatterplot(
            x=x_pos,
            y=df[mean_col],
            s=65,
            color=palette_map[key],
            edgecolor="w",
            linewidth=0.5,
            label=pretty_label,  # use pretty label here
            ax=ax,
        )

        # add error bars from stdev using matplotlib
        ax.errorbar(
            x_pos,
            df[mean_col],
            yerr=df[stdev_col],
            fmt="none",
            ecolor=palette_map[key],
            elinewidth=1.25,
            capsize=4,
            alpha=0.7,
        )

    ax.set_xticks(x_ticks)
    ax.set_xticklabels(feature_labels, rotation=90)
    ax.set_xlabel("features")
    ax.set_ylabel("classifier accuracy")

    # Dynamically compute ymin/ymax from means ± stdev across all input dataframes
    all_lows = []
    all_highs = []
    for df in accuracies.values():
        df_loc = df.copy()
        m = pd.to_numeric(df_loc.get(mean_col), errors='coerce').fillna(0.0)
        s = pd.to_numeric(df_loc.get(stdev_col, pd.Series(0, index=df_loc.index)), errors='coerce').fillna(0.0)
        if not m.empty:
            all_lows.append((m - s).min())
            all_highs.append((m + s).max())

    if all_lows and all_highs:
        ymin = float(np.nanmin(all_lows))
        ymax = float(np.nanmax(all_highs))
        # Round to nearest tenth outward
        ymin_rounded = np.floor(ymin * 10.0) / 10.0
        ymax_rounded = np.ceil(ymax * 10.0) / 10.0
        if np.isclose(ymin_rounded, ymax_rounded):
            ymin_rounded = max(0.0, ymin_rounded - 0.1)
            ymax_rounded = min(1.0, ymax_rounded + 0.1)
        ymin_rounded = max(0.0, ymin_rounded)
        ymax_rounded = min(1.0, ymax_rounded)
        ax.set_ylim(ymin_rounded, ymax_rounded)
        # set yticks at tenths for clarity
        ax.set_yticks(np.arange(ymin_rounded, ymax_rounded + 1e-9, 0.1))

    ax.grid(True, which="major", axis="y", linestyle="--")

    plt.tight_layout()

    if save_path:
        makedirs(dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300)
        plt.close()
        print(f"line_accuracies(): plot saved to {save_path}")
    else:
        plt.show()

def mixed_box_kde(scores: Dict, save_path: str = None):
    # Get all metric enums present in the actual scores DataFrame
    available_metrics = set(scores['actual'].columns.values)
    metrics = [m for m in utils.title_map.keys() if m.name in available_metrics]

    # Separate into readability and listenability metrics, preserving order
    read_metrics = [m for m in utils.readability_list if m in metrics]
    lstn_metrics = [m for m in utils.listenability_list if m in metrics]
    metrics = read_metrics + lstn_metrics

    # Set color palette for LEVEL using mapper_voa_level_to_color
    level_order = list(utils.mapper_voa_level_to_color.keys())
    palette = utils.mapper_voa_level_to_color

    fig, axes = plt.subplots(ncols=len(metrics), nrows=4, figsize=(18, 9))

    for j, key in enumerate(metrics):
        # Boxplot (row 0)
        subfig = sns.boxplot(
            data=scores['actual'], x=key.name, y="LEVEL", hue="LEVEL",
            notch=True, 
            hue_order=level_order, palette=palette,
            legend=True, ax=axes[0, j],
        )
        subfig.set_xlim(
            utils.boxplot_xtick_map[key][0], utils.boxplot_xtick_map[key][-1]
        )
        subfig.set_xticks(utils.bins_map[key])
        subfig.set_xticklabels(utils.xticklabels_map[key])
        subfig.tick_params(left=False, axis='both', which='major')
        subfig.set(yticklabels=[])
        subfig.set_xlabel("")
        subfig.set_ylabel("VoA actual" if j == 0 else "")
        subfig.set_title(key.name)
        subfig.xaxis.grid(linestyle="dashed")
        subfig.set_axisbelow(True)
        # Hide all legends in the first row except the first column
        if j != 0 and subfig.legend_:
            subfig.legend_.remove()

        # KDE for scores['actual'] (row 1)
        subfig = sns.kdeplot(
            data=scores['actual'], x=key.name, hue="LEVEL",
            hue_order=level_order, palette=palette, 
            linewidth=2, 
            ax=axes[1, j], legend=False, 
        )
        subfig.set_xlim(utils.bins_map[key][0], utils.bins_map[key][-1])
        if key in utils.ytick_map:
            subfig.set_ylim(utils.ytick_map[key][0], utils.ytick_map[key][-1])
            subfig.set_yticks(utils.ytick_map[key])
        subfig.set_xticks(utils.bins_map[key])
        subfig.set_xticklabels(utils.xticklabels_map[key])
        subfig.set_xlabel("")
        subfig.set_ylabel("VoA actual" if j == 0 else "")
        subfig.grid(linestyle="dashed")
        subfig.set_axisbelow(True)

        # KDE for scores['ka5'] (row 2)
        scores['ka5'][key.name] = np.clip(
            scores['ka5'][key.name],
            utils.bins_map[key][0],
            utils.bins_map[key][-1]
        )
        subfig = sns.kdeplot(
            data=scores['ka5'], x=key.name, hue="LEVEL",
            hue_order=level_order, palette=palette,
            linewidth=2, 
            ax=axes[2, j], legend=False,        
            )
        subfig.set_xlim(utils.bins_map[key][0], utils.bins_map[key][-1])
        if key in utils.ytick_map:
            subfig.set_ylim(utils.ytick_map[key][0], utils.ytick_map[key][-1])
            subfig.set_yticks(utils.ytick_map[key])
        subfig.set_xticks(utils.bins_map[key])
        subfig.set_xticklabels(utils.xticklabels_map[key])
        subfig.set_xlabel("")
        subfig.set_ylabel("Kaldi ASpIRE" if j == 0 else "")
        subfig.grid(linestyle="dashed")
        subfig.set_axisbelow(True)

        # KDE for scores['gws'] (row 3)
        scores['gws'][key.name] = np.clip(
            scores['gws'][key.name],
            utils.bins_map[key][0],
            utils.bins_map[key][-1]
        )
        subfig = sns.kdeplot(
            data=scores['gws'], x=key.name, hue="LEVEL",
            hue_order=level_order, palette=palette,
            linewidth=2, 
            ax=axes[3, j], legend=False,
        )
        subfig.set_xlim(utils.bins_map[key][0], utils.bins_map[key][-1])
        if key in utils.ytick_map:
            subfig.set_ylim(utils.ytick_map[key][0], utils.ytick_map[key][-1])
            subfig.set_yticks(utils.ytick_map[key])
        subfig.set_xticks(utils.bins_map[key])
        subfig.set_xticklabels(utils.xticklabels_map[key])
        subfig.set_xlabel("")
        subfig.set_ylabel("Google Web Speech" if j == 0 else "")
        subfig.grid(linestyle="dashed")
        subfig.set_axisbelow(True)

    fig.supxlabel("listenability score", fontsize=12)
    fig.supylabel("", fontsize=12, x=0, y=0.5)
    fig.tight_layout()
    plt.subplots_adjust(left=0.07)  # Increase as needed for your ylabel

    # Add a ylabel for the boxplot (rows 1)
    fig.text(
        0.005, 0.86, "boxplot per VOA level", 
        va='center', ha='left', rotation='vertical', fontsize=12,
    )

    # Add a group ylabel for the KDE plots (rows 2–4)
    fig.text(
        0.005, 0.405, "KDE plots", 
        va='center', ha='left', rotation='vertical', fontsize=12,
    )

    # Get legend handles/labels from the first boxplot axis (which has hue)
    handles, labels = axes[0, 0].get_legend_handles_labels()
    # Remove the legend from the subplot itself if it exists
    if axes[0, 0].legend_:
        axes[0, 0].legend_.remove()

    # Place a single legend at the bottom right
    fig.legend(
        handles, labels, 
        loc="lower right", bbox_to_anchor=(1, 0), ncol=len(labels)
    )

    if save_path:
        makedirs(dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=600)
        plt.close()
        print(f"mixed_box_kde(): plot saved to {save_path}")
    else:
        plt.show()

def top_n_features(scores_df: pd.DataFrame, n_top: int = 3):
    scores_top_n = []

    for n in scores_df['n_features'].unique():
        df = scores_df.loc[scores_df['n_features'] == n]
        scores_top_n.append(df.nlargest(n_top, 'median'))
        
    top_n_df = pd.concat(scores_top_n, ignore_index=True)

    return top_n_df

def main():
    scores_path = "data/voa/listenability-scores_voa-actual.csv"
    scores_df = prep.load_scores(scores_path=scores_path)

    print(scores_df)

if __name__ == "__main__":
    main()

