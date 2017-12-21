import nltk
import re

from src.curation.joke import RedditJoke, KickassHumorJoke, FunnyShortJokesJoke
from src.models.glove import read_glove_embeddings_dict, get_word_embedding_dict


class PipelineProcess(object):
	def process(self, joke):
		if not joke:
			return None

		if isinstance(joke, RedditJoke):
			return self._process_reddit_joke(joke)
		elif isinstance(joke, KickassHumorJoke):
			return self._process_kickasshumor_joke(joke)
		elif isinstance(joke, FunnyShortJokesJoke):
			return self._process_funnyshortjokes_joke(joke)

		raise ValueError("Unknown joke type : %s" % (type(joke),))

	def _process_reddit_joke(self, joke):
		raise NotImplementedError

	def _process_kickasshumor_joke(self, joke):
		raise NotImplementedError

	def _process_funnyshortjokes_joke(self, joke):
		raise NotImplementedError


class Pipeline(PipelineProcess):
	def __init__(self):
		self.pipe = []

	def add(self, process):
		if not isinstance(process, PipelineProcess):
			raise ValueError("Unknown pipeline process")

		self.pipe.append(process)
		return self

	def process(self, joke):
		if not joke:
			return None

		for proc in self.pipe:
			joke = proc.process(joke)

		return joke


class AddNouns(PipelineProcess):
	def __init__(self):
		self.tokenizer = lambda text: nltk.word_tokenize(text)
		self.tagger = lambda tokens: nltk.pos_tag(tokens)

	# self.nlp = spacy.load("en")

	def _process_funnyshortjokes_joke(self, joke):
		tokens = self.tokenizer(joke.joke)
		tags = self.tagger(tokens)
		nouns = {word.lower() for word, tag in tags if self._is_noun(tag)}

		for word in joke.category.split():
			nouns.add(word.lower())

		for word in joke.premise.split():
			nouns.add(word.lower())

		joke.nouns_ = list(nouns)
		return joke

	@staticmethod
	def _is_noun(tag):
		return tag.startswith("NNP")


class AddGloveEmbeddings(PipelineProcess):
	def __init__(self, size=50):
		self.model = read_glove_embeddings_dict(size)

	def process(self, joke):
		if not hasattr(joke, "nouns_"):
			raise ValueError("Joke does not have nouns_. Please run AddNouns before.")

		joke.embeddings_ = get_word_embedding_dict(joke.nouns_, self.model)

		for key, value in joke.embeddings_.items():
			if value is not None:
				joke.embeddings_[key] = value.tolist()

		return joke


class Lowercase(PipelineProcess):
	def _process_funnyshortjokes_joke(self, joke):
		for attr in joke.__dict__.keys():
			value = getattr(joke, attr)
			if isinstance(value, str):
				setattr(joke, attr, value.lower())
		return joke


class Filter(PipelineProcess):
	def __init__(self):
		self.url_regexp = re.compile("^http(s*)://")

	def process(self, joke):
		if not joke:
			return None

		if self._bad_premise(joke):
			return None

		if self._bad_punchline(joke):
			return None

		return joke

	def _bad_premise(self, joke):
		return False

	def _bad_punchline(self, joke):
		punchline = joke["punchline"]

		if self.url_regexp.match(punchline):
			return True

		return False


class Clean(PipelineProcess):
	def _process_funnyshortjokes_joke(self, joke):
		def clean_category(category):
			category = category.replace("Jokes", "")
			return category.strip()

		def clean_premise(premise):
			return premise.strip()

		def clean_joke(joke):
			if joke.startswith("Q.") or joke.startswith("Q:"):
				joke = re.sub("(Q|A)(\.|:)", "", joke)
			return self._clean_whitespace(joke)

		joke.category = clean_category(joke.category)
		joke.premise = clean_premise(joke.premise)
		joke.joke = clean_joke(joke.joke)
		return joke

	def _clean_whitespace(self, joke):
		return " ".join(joke.split())
