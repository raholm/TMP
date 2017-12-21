import os

from src.curation.io import get_raw_reddit_joke_files, get_raw_kickasshumor_joke_files, \
	get_raw_funnyshortjokes_joke_files

from src.curation.pipeline import Pipeline, Filter, AddNouns, Lowercase, Clean, AddGloveEmbeddings
from src.curation.readers import RawRedditJokeReader, RawKickassHumorJokeReader, RawFunnyShortJokesJokeReader
from src.curation.writers import ProcessedFunnyShortJokesJokeWriter
from src.util.env import get_project_data_path


def test_pipeline():
	pipeline = Pipeline()
	pipeline.add(Filter())
	pipeline.add(AddNouns())
	pipeline.add(Lowercase())
	return pipeline


def reddit_test():
	joke_parser = RawRedditJokeReader()
	pipeline = test_pipeline()

	for file in get_raw_reddit_joke_files():
		jokes = joke_parser.parse(file)
		jokes = (pipeline.process(joke) for joke in jokes)
		jokes = list(filter(lambda joke: joke is not None, jokes))

		print(jokes)
		break


def kickasshumor_test():
	joke_parser = RawKickassHumorJokeReader()
	pipeline = test_pipeline()

	for file in get_raw_kickasshumor_joke_files():
		jokes = joke_parser.parse(file)
		jokes = (pipeline.process(joke) for joke in jokes)
		jokes = list(filter(lambda joke: joke is not None, jokes))

		print(jokes)
		break


def funnyshortjokes_test():
	joke_parser = RawFunnyShortJokesJokeReader()
	pipeline = Pipeline()
	pipeline.add(Clean())
	pipeline.add(AddNouns())
	pipeline.add(Lowercase())
	pipeline.add(AddGloveEmbeddings())

	for file in get_raw_funnyshortjokes_joke_files():
		filename = file.split("/")[-1]
		output_path = os.path.join(get_project_data_path(),
								   "funnyshortjokes_processed",
								   filename)
		writer = ProcessedFunnyShortJokesJokeWriter(output_path)

		jokes = joke_parser.parse(file)
		jokes = (pipeline.process(joke) for joke in jokes)
		writer.write(jokes)

		# jokes = list(filter(lambda joke: joke is not None, jokes))

		# for joke in jokes:
		# 	print(joke)
		# 	print("Nouns:", joke.nouns_)
		# 	print("Embeddings:", joke.embeddings_)

		# print(jokes)
		break


def main():
	# reddit_test()
	# kickasshumor_test()
	funnyshortjokes_test()


if __name__ == "__main__":
	main()
