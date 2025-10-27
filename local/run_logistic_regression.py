import csv
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import re

from itertools import combinations
from matplotlib import pyplot
from numpy import mean
from numpy import std
from os.path import join
from scipy.stats import sem
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.model_selection import KFold
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import learning_curve
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

system_map = dict({'actual': 'actual',
                   'gws': 'google-web-speech',
                   'ka5': 'kaldi-aspire-s5'})

scores_file = \
	dict({'actual': 'kotanietal2014_voa_actual_F-chunks_F-punct_T-samp_F-limit_T-save.csv',
       'gws': 'kotanietal2014_voa_gws_T-chunks_T-punct_T-samp_F-limit_T-save.csv',
	   'ka5': 'kotanietal2014_voa_ka5_T-chunks_T-punct_T-samp_F-limit_T-save.csv'})

def evaluate_model(X, y, repeats):
	# prepare the cross-validation procedure
	cv = RepeatedStratifiedKFold(n_splits=10, n_repeats=repeats, random_state=1)

	# create model
	model = LogisticRegression(multi_class='ovr')

	# evaluate model
	scores = cross_val_score(model, X, y, scoring='accuracy', cv=cv, n_jobs=-1)
	return scores

def get_examples(scores_df):
	trimmed_df = scores_df.drop(columns='FKGL').loc[scores_df['LEVEL'] != 2]
	# trimmed_df = scores_df.drop(columns='FKGL')

	X = trimmed_df.drop(columns=['ID', 'LEVEL'])
	y = trimmed_df['LEVEL']

	return X,y

def plot_learning_curve(curve_info):
	plot_id = "-".join(map(str, curve_info[0]))
	plot_text = "task: 3-way, features: " + plot_id
	curve_df = curve_info[1]
	train_sizes = curve_df['train_size']
	train_means = curve_df['train_mean_scr']
	train_stds = curve_df['train_std_scr']
	test_means = curve_df['test_mean_scr']
	test_stds = curve_df['test_std_scr']

	plt.figure()
	plt.xlabel("training examples")
	plt.ylabel("accuracy")

	plt.grid()
	plt.fill_between(train_sizes, train_means - train_stds,
                     train_means + train_stds, alpha=0.1,
                     color="r")
	plt.fill_between(train_sizes, test_means - test_stds,
                     test_means + test_stds, alpha=0.1, color="g")
	plt.plot(train_sizes, train_means, 'o-', color="r",
             label="training score")
	plt.plot(train_sizes, test_means, 'o-', color="g",
             label="cross-validation score")
	plt.legend(loc="best")
	t = plt.text(350, 0.35, plot_text)
	t.set_bbox(dict(facecolor='white', alpha=0.75, linewidth=0))
	
	return plt

def run_learning_curve(X, y, folds, repeats):
	# prepare the cross-validation procedure
	cv = RepeatedStratifiedKFold(n_splits=folds, n_repeats=repeats, random_state=1)

	step_size = 50
	max_size = len(y) * (1 - 1/folds)
	train_sizes = np.arange(0, max_size + step_size, step_size)
	train_sizes[0] = step_size/10
	train_sizes = train_sizes/max_size

	# create model
	model = make_pipeline(StandardScaler(), 
		       LogisticRegression(multi_class='ovr'))

	# evaluate model
	train_sizes, train_scores, test_scores = \
		learning_curve(model, X, y, scoring='accuracy', 
		 cv=cv, n_jobs=-1, train_sizes=train_sizes)
	
	train_means = np.mean(train_scores, axis=1)
	train_stds = np.std(train_scores, axis=1)
	
	test_means = np.mean(test_scores, axis=1)
	test_stds = np.std(test_scores, axis=1)
	
	# report performance
	curve_df = pd.DataFrame()
	curve_df['train_size'] = train_sizes
	curve_df['train_mean_scr'] = train_means
	curve_df['train_std_scr'] = train_stds
	curve_df['test_mean_scr'] = test_means
	curve_df['test_std_scr'] = test_stds

	print(curve_df)

	return curve_df

def run_learning_curve_x_features(scores_df, feature_count):
	folds = 10
	repeats = 15
	curve_infos = []

	y = scores_df['LEVEL']

	metrics = scores_df.columns.tolist()
	metrics.remove("LEVEL")
	metrics.sort()

	metric_combos = list(combinations(metrics, feature_count))

	for metric_combo in metric_combos:
		X = scores_df[list(metric_combo)]
		print('Feature: %s' % ', '.join(map(str, metric_combo)))
		curve_df = run_learning_curve(X, y, folds, repeats)
		curve_infos.append((metric_combo, curve_df))

	return curve_infos

def run_logistic_regression_k_fold(X, y, folds):
	cv = KFold(n_splits=folds, random_state=1, shuffle=True)

	# create model
	model = LogisticRegression(multi_class='ovr')

	# evaluate model
	scores = cross_val_score(model, X, y, scoring='accuracy', cv=cv, n_jobs=-1)

	# report performance
	print('Accuracy: %.4f (%.4f)' % (mean(scores), std(scores)))

def run_logistic_regression_repeated_k_fold(X, y, folds, repeats):
	# prepare the cross-validation procedure
	cv = RepeatedStratifiedKFold(n_splits=folds, n_repeats=repeats, random_state=1)
	# create model
	# model = LogisticRegression()
	# model = LogisticRegression(multi_class='ovr')
	# model = make_pipeline(StandardScaler(), LogisticRegression())
	model = make_pipeline(StandardScaler(), 
		       LogisticRegression(multi_class='ovr'))

	# evaluate model
	scores = cross_val_score(model, X, y, scoring='accuracy', cv=cv, n_jobs=-1)
	# report performance
	print('Accuracy: %.4f (%.4f)' % (mean(scores), std(scores)))

	return (mean(scores), std(scores))

def run_logistic_regression_x_features(scores_df, feature_count):
	folds = 10
	repeats = 15
	accuracies = []

	y = scores_df['LEVEL']

	metrics = scores_df.columns.tolist()
	metrics.remove("LEVEL")
	metrics.sort()

	metric_combos = list(combinations(metrics, feature_count))

	for metric_combo in metric_combos:
		X = scores_df[list(metric_combo)]
		print('Feature: %s' % ', '.join(map(str, metric_combo)))
		result = \
			list(run_logistic_regression_repeated_k_fold(X, y, folds, repeats))
		result.insert(0, metric_combo)
		accuracies.append(tuple(result))

	return accuracies

def kotani_get_densities(scores_df):
	scores_df['L_WORD'] = scores_df['C_SYLL'].div(scores_df['C_WORD'].values)
	scores_df['L_SENT'] = scores_df['C_WORD'].div(scores_df['C_SENT'].values)
	scores_df['P_DIFF_WORDS'] \
		= scores_df['C_DIFF_WORDS'].div(scores_df['C_WORD'].values)
	scores_df['P_POLY_WORDS'] \
		= scores_df['C_POLY_WORDS'].div(scores_df['C_WORD'].values)
	scores_df['P_CONTRACTIONS'] \
		= scores_df['C_CONTRACTIONS'].div(scores_df['C_WORD'].values)
	scores_df['P_DEDUCTIONS'] \
		= scores_df['C_DEDUCTIONS'].div(scores_df['C_WORD'].values)
	scores_df['P_ELISIONS'] \
		= scores_df['C_ELISIONS'].div(scores_df['C_WORD'].values)
	scores_df['P_LINKINGS'] \
		= scores_df['C_LINKINGS'].div(scores_df['C_WORD'].values)
	scores_df['P_REDUCTIONS'] \
		= scores_df['C_REDUCTIONS'].div(scores_df['C_WORD'].values)
	scores_df['P_TOTAL'] \
		= scores_df['C_TOTAL'].div(scores_df['C_WORD'].values)
	
	return scores_df

def content_prepare(scores_df):
	scores_df['AVE_NOT_IN_DALE'] \
		= scores_df['NOT_IN_DALE_COUNT'].div(scores_df['WORD_COUNT'].values)
	scores_df['AVE_MONOSYLL_COUNT'] \
		= scores_df['MONOSYLL_COUNT'].div(scores_df['WORD_COUNT'].values)
	scores_df['INV_AVE_SENT_LEN'] = 1 / scores_df['AVE_SENT_LEN']
	scores_df['AVE_MINIW_COUNT'] \
		= scores_df['MINIW_COUNT'].div(scores_df['WORD_COUNT'].values)

	return scores_df

def main():
	classifier_type = "3-way"	# "2-way" or "3-way"
	data_type = "voa"			# "voa", "ka5", "gws"

	folds = 10
	repeats = 15

	scores_path = join(
		"data", data_type, f"listenability_scores-{data_type}.csv"
	)

	scores_df = pd.read_csv(scores_path)
	scores_df.columns = scores_df.columns.str.upper()
	scores_df['LEVEL'] = scores_df['ID'].str.strip().str[-1].astype(int)

	if classifier_type == "2-way":
		trimmed_df = scores_df.drop(columns='ID').loc[scores_df['LEVEL'] != 2]
	else:
		trimmed_df = scores_df.drop(columns='ID')
	
	accuracies = []
	for feature_count in range(1, len(trimmed_df.columns)):
		accuracies.extend(
			run_logistic_regression_x_features(trimmed_df, feature_count)
		)
	
	results_path = join(
		"data", data_type, f"log_reg-{classifier_type}-{data_type}.csv"
	)
	with open(results_path, mode = 'w') as results_f:
		writer = csv.writer(results_f)
		writer.writerow(["features", "mean", "stdev"])
		writer.writerows(accuracies)

	curve_infos = []
	for feature_count in range(1, len(trimmed_df.columns)):
		curve_infos.extend(
			run_learning_curve_x_features(trimmed_df, feature_count)
		)
	
	for curve_info in curve_infos:
		plot_id = "-".join(map(str, curve_info[0]))
		plot_learning_curve(curve_info)
		
		plt.savefig(
			join(
				"assets", "learning_curves", 
				f"lr_lrncrv-voa_{data_type}-{plot_id}.png"
			), 
			dpi=600
		)

if __name__ == "__main__":
	main()
