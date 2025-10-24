import preparation as prep
import results as rslts


def main():
    scores = prep.load_voa_data()
    for score_type in scores.keys():
        scores[score_type].drop(columns=['FEL', 'RL'], inplace=True)

    rslts.mixed_box_kde(
        scores=scores, 
        save_path="assets/issc/mixed-formulae_based_scores.png"
    )

if __name__ == "__main__":
    main()