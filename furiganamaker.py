# requires mecab-python3, unidic, pykakasi
import os, sys, shutil, unidic, pykakasi


def is_kanji(ch: str) -> bool:
	"""
	Checks if a given character is a kanji or not.
	:param ch: The character to check.
	:return: Returns True when 'ch' is a kanji.
	"""
	n = ord(ch)

	return (19968 <= n <= 40959) or n == 12293 or n == 12534


def has_kanji(text: str) -> bool:
	"""
	Checks if a string has any kanji character in it.
	:param text: The text to check.
	:return: Returns True when any of the characters in 'text' is a kanji.
	"""
	for c in text:
		if is_kanji(c):
			return True

	return False


def all_kanji(text: str) -> bool:
	"""
	Checks if all characters of a string are kanji characters.
	:param text: The text to check.
	:return: Returns True when all of the characters in 'text' are kanji.
	"""
	for c in text:
		if not is_kanji(c):
			return False

	return True


class Reading:
	def __init__(self, onreadings, kunreadings):
		assert isinstance(onreadings, tuple), "Expected tuple for on readings. Did you for get a comma?"
		assert isinstance(kunreadings, tuple), "Expected tuple for kun readings. Did you for get a comma?"

		self.on = onreadings
		self.kun = kunreadings


class Problem:
	def __init__(self, description: str, kanji: str, userdata):
		self.description = description
		self.kanji = kanji
		self.userdata = userdata


class Instance:
	def __init__(self, opentag: str, closetag: str, problems: list[Problem], kakasi: pykakasi.kakasi, mecabtagger = None, jamdict = None):
		"""
		Creates a new instance.
		:param opentag: The tag used to mark the beginning of a furigana block.
		:param closetag: The tag used to mark the end of a furigana block.
		:param problems: A (empty) list where all problems are stored.
		:param kakasi: The main libaryr used to generate the furigana readings and convert readings in general.
		:param mecabtagger: An optional MeCab.Tagger() which can be used to get additional readings.
		:param jamdict: An optional Jamdict() which can be used to get additional readings.
		"""
		matrixpath = os.path.join(unidic.DICDIR, "matrix.bin")
		if not os.path.isfile(matrixpath):
			raise Exception("Could not find \"" + matrixpath + "\". Did you run \"python -m unidic download\"? Might require admin rights.")

		self.mecab = mecabtagger
		self.kakasi = kakasi
		self.jam = jamdict
		self.opentag = opentag
		self.closetag = closetag
		self.readingscache = {}
		self.customreadings = {}
		self.customreadings_opentag = "<"
		self.customreadings_closetag = ">"
		self.problems = problems

	def _kana2hira(self, kana: str) -> str:
		conv = self.kakasi.convert(kana)

		hira = ""
		for c in conv:
			hira += c["hira"]

		assert len(kana) == len(hira), "Expected both to be the same length"

		return hira

	def _hira2kana(self, hira: str) -> str:
		conv = self.kakasi.convert(hira)

		kana = ""
		for c in conv:
			kana += c["kana"]

		assert len(kana) == len(hira), "Expected both to be the same length"

		return kana

	def init(self, additionalreadings: dict[str, Reading], customreadings: tuple[tuple[str], tuple[str]]):
		for r in additionalreadings:
			reading = additionalreadings[r]
			cached = []

			if reading.on:
				for k in reading.on:
					h = self._kana2hira(self, k)

					cached.append((k, h))

			if reading.kun:
				for h in reading.kun:
					k = self._hira2kana(self, h)

					cached.append((k, h))

			self.addtocache(r, cached)

		for kanji, read in customreadings:
			assert len(kanji) == len(read), "The reading must represent the exact parts of the kanji."
			word = "".join(kanji)

			repl = self.customreadings_opentag
			for i in range(len(kanji)):
				k = kanji[i]
				r = read[i]

				if is_kanji(k):
					repl += k + self.opentag + r + self.closetag
				else:
					repl += k
			repl += self.customreadings_closetag

			self.customreadings[word] = repl

	def _addtocache(self, kanji, cachedreadings):
		sort = sorted(cachedreadings, key=lambda x: len(x[0]), reverse=True)
		self.readingscache[kanji] = sort
