import os
import csv
import pandas as pd
import numpy as np

from src.util.env import get_project_path


def read_glove_embeddings_df(size=300):
    file_path = _get_glove_file_path(size)
    return pd.read_table(file_path, sep=" ", index_col=0, header=None, quoting=csv.QUOTE_NONE)


def read_glove_embeddings_dict(size=300):
    file_path = _get_glove_file_path(size)

    model = {}

    with open(file_path, "r") as infile:
        for line in infile:
            parts = line.split()
            word = parts[0]
            embedding = np.array([float(val) for val in parts[1:]])
            model[word] = embedding

    return model


def _get_glove_file_path(size):
    if size not in (50, 100, 200, 300):
        raise ValueError("Invalid embedding size : %s" % (size,))

    filename = "glove.6B.%id.txt" % size
    file_path = os.path.join(get_project_path(), "models", filename)

    return file_path


def get_word_embedding(word_or_words, model):
    if isinstance(model, dict):
        if not isinstance(word_or_words, str):
            return np.array([model[word] for word in word_or_words])
        return model[word_or_words]
    elif isinstance(model, pd.DataFrame):
        return model.loc[word_or_words].as_matrix()

    raise ValueError("Unknown model : %s" % type(model))


def main():
    # model = read_glove_embeddings_df(50)
    model = read_glove_embeddings_dict(50)

    print(get_word_embedding("the", model))
    print(get_word_embedding(["the", "what"], model))
    print(get_word_embedding("whatthefuck", model))


if __name__ == '__main__':
    main()
