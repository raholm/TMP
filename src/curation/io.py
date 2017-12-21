import os

from src.util.env import get_project_data_path


def get_raw_reddit_joke_files():
    directory = os.path.join(get_project_data_path(), "reddit_raw")
    for file in _get_joke_files(directory):
        yield file


def get_raw_funnyshortjokes_joke_files():
    directory = os.path.join(get_project_data_path(), "funnyshortjokes_raw")
    for file in _get_joke_files(directory):
        yield file


def get_raw_kickasshumor_joke_files():
    directory = os.path.join(get_project_data_path(), "kickasshumor_raw")
    for file in _get_joke_files(directory):
        yield file


def _get_joke_files(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".json"):
                yield os.path.join(root, file)
