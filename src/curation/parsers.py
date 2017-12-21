import json


class RawJokeParser(object):
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

			jokes.append(joke)

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


class RawRedditJokeParser(RawJokeParser):
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


class RawFunnyShortJokesJokeParser(RawJokeParser):
	def _parse_category(self, joke):
		category = joke["category"].lower()
		category = category.replace("jokes", "")
		return category.strip()

	def _parse_premise(self, joke):
		return joke["premise"].strip()

	def _parse_punchline(self, joke):
		return joke["punchline"].strip()


class RawKickassHumorJokeParser(RawJokeParser):
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
