import json

from src.curation.joke import FunnyShortJokesJoke


class RawJokeReader(object):
	def parse(self, file):
		jokes = []
		data = self._load_data(file)

		for raw_joke in data.values():
			premise = self._parse_premise(raw_joke)
			punchline = self._parse_punchline(raw_joke)
			category = self._parse_category(raw_joke)

			joke = {"premise": premise,
					"punchline": punchline,
					"category": category}

			jokes.append(self._create_joke(joke))

		return jokes

	@staticmethod
	def _load_data(file):
		with open(file, "r") as infile:
			data = json.load(infile)

		return data

	def _parse_premise(self, joke):
		raise NotImplementedError

	def _parse_punchline(self, joke):
		raise NotImplementedError

	def _parse_category(self, joke):
		raise NotImplementedError

	def _create_joke(self, joke):
		raise NotImplementedError


class RawRedditJokeReader(RawJokeReader):
	def _parse_category(self, joke):
		subreddit = joke["subreddit"]

		category = subreddit.split("/")[-2].lower()
		category = category.replace("jokes", "")

		if not category:
			category = "general"

		return category.strip()

	def _parse_premise(self, joke):
		return joke["premise"].strip()

	def _parse_punchline(self, joke):
		return joke["punchline"].strip()


class RawFunnyShortJokesJokeReader(RawJokeReader):
	def _parse_category(self, joke):
		return joke["category"]

	def _parse_premise(self, joke):
		return joke["premise"]

	def _parse_punchline(self, joke):
		return joke["punchline"]

	def _create_joke(self, joke):
		return FunnyShortJokesJoke(**joke)


class RawKickassHumorJokeReader(RawJokeReader):
	def _parse_punchline(self, joke):
		return joke["punchline"].strip()

	def _parse_premise(self, joke):
		return ""

	def _parse_category(self, joke):
		category = joke["category"].lower()
		category = category.replace("-", " ") \
			.replace("funny", "") \
			.replace("jokes", "")
		return category.strip()
