import numpy as np
import pandas as pd
import utils

def get_voa_levels(scores_df):
    # Extract last character from ID, convert to numeric with nullable integer dtype
    last_char = scores_df['ID'].astype(str).str.strip().str[-1]
    level_nums = pd.to_numeric(last_char, errors='coerce').astype('Int64')

    # Map numeric levels to string labels
    mapping = {1: "beginner", 2: "intermediate", 3: "advanced"}
    scores_df['LEVEL'] = level_nums.map(mapping)

    # Fill unmapped/invalid entries with a safe default
    scores_df['LEVEL'] = scores_df['LEVEL'].fillna("unknown")

    return scores_df

def load_scores(scores_path: str):
    """
    Load scores from a given path (directory + filename)

    Parameters
    ----------
    scores_path : string
        Path of the CSV file containing the scores

    Returns
    -------
    scores_df : pandas.DataFrame
        Record of scores for each material
    """
    scores_df = pd.read_csv(scores_path)
    scores_df.columns = scores_df.columns.str.upper()

    scores_df = map_to_levels(scores_df=scores_df)
    scores_df = get_voa_levels(scores_df=scores_df)

    return scores_df

def load_voa_data():
    scores = {
        'actual': load_scores(
            scores_path="data/voa/listenability_scores-voa_actual.csv"), 
        'ka5': load_scores(
            scores_path="data/kaldi_aspire/listenability_scores-ka5.csv"), 
        'gws': load_scores(
            scores_path="data/google_web_speech/listenability_scores-gws.csv"), 
        }

    return scores

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
    metrics = list(
        set(utils.title_map.keys()).intersection(scores_df.columns.values)
    )

    for metric in metrics:
        col_name = metric + '_cat'
        
        metric_enum = utils.Metric[metric]
        bins = list(utils.bins_map[metric_enum])  # Make a copy as a list
        bins.append(np.inf)  # Add inf without modifying the original

        labels = list(range(0, len(bins) - 1))
        if metric == "FRE":
            labels = labels[::-1]

        scores_df[col_name] = pd.to_numeric(
            pd.cut(scores_df[metric], bins, labels=labels)
        )

    return scores_df
