import pandas as pd
import preparation as prep
import results as rslts


def main():
    scores = prep.load_voa_data()
    for score_type in scores.keys():
        scores[score_type].drop(columns=['FEL', 'RL'], inplace=True)

    # Distribution of formulae-based listenability scores
    rslts.mixed_box_kde(
        scores=scores, 
        save_path="assets/issc/mixed-formulae_based_scores.png"
    )

    # Classifier accuracies
    classifier_types = ["2_way", "3_way"]

    for classifier_type in classifier_types:
        accuracies = prep.load_classifier_data(
            classifier_type=classifier_type
        )
        for score_type in accuracies.keys():
            mask = accuracies[score_type]['features'].apply(
                lambda feats: ("FEL" not in feats) and ("RL" not in feats)
            )

            accuracies[score_type] = accuracies[score_type][mask].reset_index(
                drop=True
            )

        # Plot line accuracies for the filtered accuracies dict
        rslts.line_accuracies(
            accuracies=accuracies,
            save_path=f"assets/issc/line-accuracies-{classifier_type}.png"
        )


if __name__ == "__main__":
    main()