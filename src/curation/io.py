import os

from src.util.env import get_env_variable


def get_raw_reddit_joke_files():
	directory = get_env_variable("TMP_DATA_PATH") + "/reddit_raw"
	for file in _get_joke_files(directory):
		yield file


def get_raw_funnyshortjokes_joke_files():
	directory = get_env_variable("TMP_DATA_PATH") + "/funnyshortjokes_raw"
	for file in _get_joke_files(directory):
		yield file


def get_raw_kickasshumor_joke_files():
	directory = get_env_variable("TMP_DATA_PATH") + "/kickasshumor_raw"
	for file in _get_joke_files(directory):
		yield file


def _get_joke_files(directory):
	for root, dirs, files in os.walk(directory):
		for file in files:
			if file.endswith(".json"):
				yield os.path.join(root, file)
