class Joke(object):
	def __init__(self):
		self._category = None
		self._premise = None
		self._punchline = None
		self._text = None

		self._dirty = False

	@property
	def nouns_(self):
		if hasattr(self, "_nouns"):
			return self._nouns
		return None

	@nouns_.setter
	def nouns_(self, value):
		self.nouns_ = value

	@property
	def category(self):
		return self._category

	@property
	def premise(self):
		return self._premise

	@property
	def punchline(self):
		return self._punchline

	@property
	def text(self):
		if self._is_dirty():
			self._text = " ".join((self.premise, self.punchline))
			self._unset_dirty()
		return self._text

	@category.setter
	def category(self, value):
		self._category = value

	@premise.setter
	def premise(self, value):
		self._premise = value
		self._set_dirty()

	@punchline.setter
	def punchline(self, value):
		self._punchline = value
		self._set_dirty()

	def _is_dirty(self):
		return self._dirty

	def _set_dirty(self):
		self._dirty = True

	def _unset_dirty(self):
		self._dirty = False
