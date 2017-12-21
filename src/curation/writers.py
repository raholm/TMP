import json

from src.util.checks import is_iterable


class ProcessedJokeWriter(object):
	def __init__(self, output):
		self.output = output

	def write(self, joke_or_jokes):
		raise NotImplementedError


class ProcessedFunnyShortJokesJokeWriter(ProcessedJokeWriter):
	def __init__(self, output):
		super().__init__(output)

	def write(self, joke_or_jokes):
		with open(self.output, "a") as outfile:
			if is_iterable(joke_or_jokes):
				for joke in joke_or_jokes:
					content = json.dumps(joke.__dict__) + "\n"
					outfile.write(content)
			else:
				content = json.dumps(joke_or_jokes.__dict__) + "\n"
				outfile.write(content)
