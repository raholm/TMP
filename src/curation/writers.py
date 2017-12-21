import json

from src.util.checks import is_iterable


class ProcessedJokeWriter(object):
	def write(self, joke_or_jokes, file):
		raise NotImplementedError


class ProcessedFunnyShortJokesJokeWriter(ProcessedJokeWriter):
	def write(self, joke_or_jokes, file):
		with open(file, "a") as outfile:
			if is_iterable(joke_or_jokes):
				for joke in joke_or_jokes:
					content = json.dumps(joke.__dict__) + "\n"
					outfile.write(content)
			else:
				content = json.dumps(joke_or_jokes.__dict__) + "\n"
				outfile.write(content)
