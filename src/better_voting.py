import argparse
import csv
import re
from typing import List, Tuple

import numpy as np


RANK_RE = re.compile(r"\(#([0-9]+)\)")


def load_csv(file_name: str) -> List[List[str]]:
	to_return = list()
	with open(file_name, "r", encoding="utf-8", newline="") as csv_file:
		reader = csv.DictReader(csv_file)
		rank_to_name = dict()
		for field_name in reader.fieldnames:
			match = RANK_RE.search(field_name)
			if match is not None:
				rank_number = int(match.group(1))
				rank_to_name[rank_number] = field_name
		for row in reader:
			row_data = [row[rank_to_name[rank]] for rank in sorted(rank_to_name.keys())]
			to_return.append(row_data)
	return to_return


def verify_data(preference_orders: List[List[str]]):
	first_row = preference_orders[0]
	options = set(sorted(first_row))
	assert len(first_row) == len(options)  # no duplicates
	for row in preference_orders[1:]:
		if len(row) != len(first_row):
			raise ValueError(f"row sizes were not consistent:\n{first_row}\nvs\n{row}")
		row_options = set(sorted(row))
		if row_options != options:
			raise ValueError(f"row contents were not consistent:\n{options}\nvs\n{row_options}")


def make_markov_model(preference_orders: List[List[str]]) -> Tuple[List[str], np.ndarray]:
	legend = preference_orders[0].copy()
	legend_reverse = {name: index for index, name in enumerate(legend)}
	n = len(legend)
	counts = list()
	for _ in range(n):
		counts.append([0] * n)
	for order in preference_orders:
		for i in range(n - 1):
			better_option = legend_reverse[order[i]]
			for j in range(i + 1, n):
				worse_option = legend_reverse[order[j]]
				counts[worse_option][better_option] += 1
				counts[better_option][better_option] += 1
	markov_model = np.array(counts, dtype=float).transpose()
	markov_model = markov_model / markov_model.sum(axis=0)
	return legend, markov_model


def get_stable_state(markov_model: np.ndarray) -> np.ndarray:
	eigen_values, eigen_vectors = np.linalg.eig(markov_model)
	for i in range(eigen_values.shape[0]):
		if abs(eigen_values[i] - 1) < 1e-6:
			return eigen_vectors[:, i]
	raise ValueError("could not find stable state")


def markovian_voting(preference_orders: List[List[str]]) -> List[Tuple[str, float]]:
	verify_data(preference_orders)
	legend, markov_model = make_markov_model(preference_orders)
	stable_state = get_stable_state(markov_model)
	stable_state = stable_state / stable_state.sum()
	scores = list(zip(legend, list(stable_state)))
	return scores


if __name__ == "__main__":
	arg_parser = argparse.ArgumentParser()
	arg_parser.add_argument("votes_file_name",
        help="name of the .csv file containing the results of the Google Forms preference survey")
	args = arg_parser.parse_args()
	csv_data = load_csv(args.votes_file_name)
	results = markovian_voting(csv_data)
	for choice_name, score in sorted(results, key=lambda x: x[1], reverse=True):
		score_scaled = 100 * score
		print(f"{score_scaled:.2f} : {choice_name}")
