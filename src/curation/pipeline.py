import nltk
import re

import spacy

from src.curation.joke import FSJJoke


class PipelineProcess(object):
    def process(self, joke):
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

    def process(self, joke):
        if not joke:
            return None

        text = joke["premise"] + joke["punchline"]
        tokens = self.tokenizer(text)
        tags = self.tagger(tokens)
        nouns = (word for word, tag in tags if self._is_noun(tag))

        # nouns = (token.text for token in self.nlp(text) if self._is_noun(token.tag_))

        joke["nouns"] = " ".join(nouns)
        return joke

    @staticmethod
    def _is_noun(tag):
        return tag.startswith("NNP")


class Lowercase(PipelineProcess):
    def process(self, joke):
        if not joke:
            return None

        for key, value in joke.items():
            if isinstance(value, str):
                joke[key] = value.lower()

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
    def __init__(self):
        pass

    def process(self, joke):
        if isinstance(joke, FSJJoke):
            return self._clean_fsj_joke(joke)

        raise ValueError("Unknown joke type : %s" % (type(joke)))

    def _clean_fsj_joke(self, joke):
        if joke.punchline.startsWith("Q."):
            joke.punchline = joke.punchline.replace("Q.", "").replace("\nA.", "")

        return joke
