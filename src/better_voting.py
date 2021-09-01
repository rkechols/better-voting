import argparse
import csv
import re
from typing import List


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


if __name__ == "__main__":
	arg_parser = argparse.ArgumentParser()
	arg_parser.add_argument("votes_file_name",
        help="name of the .csv file containing the results of the Google Forms preference survey")
	args = arg_parser.parse_args()
	csv_data = load_csv(args.votes_file_name)
	print("hi")
