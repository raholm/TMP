from src.curation.io import get_raw_reddit_joke_files, get_raw_kickasshumor_joke_files, \
	get_raw_funnyshortjokes_joke_files
from src.curation.parsers import RawRedditJokeParser, RawKickassHumorJokeParser, RawFunnyShortJokesJokeParser
from src.curation.pipeline import Pipeline, Filter, AddNouns, Lowercase


def test_pipeline():
	pipeline = Pipeline()
	pipeline.add(Filter())
	pipeline.add(AddNouns())
	pipeline.add(Lowercase())
	return pipeline


def reddit_test():
	joke_parser = RawRedditJokeParser()
	pipeline = test_pipeline()

	for file in get_raw_reddit_joke_files():
		jokes = joke_parser.parse(file)
		jokes = (pipeline.process(joke) for joke in jokes)
		jokes = list(filter(lambda joke: joke is not None, jokes))

		print(jokes)
		break


def kickasshumor_test():
	joke_parser = RawKickassHumorJokeParser()
	pipeline = test_pipeline()

	for file in get_raw_kickasshumor_joke_files():
		jokes = joke_parser.parse(file)
		jokes = (pipeline.process(joke) for joke in jokes)
		jokes = list(filter(lambda joke: joke is not None, jokes))

		print(jokes)
		break


def funnyshortjokes_test():
	joke_parser = RawFunnyShortJokesJokeParser()
	pipeline = test_pipeline()

	for file in get_raw_funnyshortjokes_joke_files():
		jokes = joke_parser.parse(file)
		jokes = (pipeline.process(joke) for joke in jokes)
		jokes = list(filter(lambda joke: joke is not None, jokes))

		print(jokes)
		break


def main():
	reddit_test()
	kickasshumor_test()
	funnyshortjokes_test()


if __name__ == "__main__":
	main()
