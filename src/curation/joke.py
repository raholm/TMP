class Joke(object):
	pass


class RedditJoke(Joke):
	pass


class FunnyShortJokesJoke(Joke):
	def __init__(self, category, premise, punchline):
		super().__init__()

		self.category = category
		self.premise = premise
		self.joke = punchline

	def __str__(self):
		return "Category: %s\nPremise: %s\n%s" % (self.category, self.premise, self.joke)


class KickassHumorJoke(Joke):
	pass
