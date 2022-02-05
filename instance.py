# requires mecab-python3, unidic, pykakasi
import os, sys, shutil, unidic, pykakasi
from instanceprv import InstancePrv
from problem import Problem


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


class CustomReading:
	def __init__(self, onreading: tuple[str], kunreading: tuple[str]):
		assert isinstance(onreading, tuple), "Expected tuple for on readings. Did you for get a comma?"
		assert isinstance(kunreading, tuple), "Expected tuple for kun readings. Did you for get a comma?"
		assert len(onreading) == len(kunreading), "Both readings must have the same length as one is the translation of the other."

		self.on = onreading
		self.kun = kunreading


class Instance(InstancePrv):
	def __init__(self, opentag: str, closetag: str, kakasi: pykakasi.kakasi, mecabtagger = None, jamdict = None):
		"""
		Creates a new instance.
		:param opentag: The tag used to mark the beginning of a furigana block.
		:param closetag: The tag used to mark the end of a furigana block.
		:param kakasi: The main libaryr used to generate the furigana readings and convert readings in general.
		:param mecabtagger: An optional MeCab.Tagger() which can be used to get additional readings.
		:param jamdict: An optional Jamdict() which can be used to get additional readings.
		"""
		matrixpath = os.path.join(unidic.DICDIR, "matrix.bin")
		if not os.path.isfile(matrixpath):
			raise Exception("Could not find \"" + matrixpath + "\". Did you run \"python -m unidic download\"? Might require admin rights.")

		InstancePrv.__init__(self)

		self.mecab = mecabtagger
		self.kakasi = kakasi
		self.jam = jamdict
		self.opentag = opentag
		self.closetag = closetag
		self.customreadings_opentag = "<"
		self.customreadings_closetag = ">"

	def init(self, additionalreadings: dict[str, Reading] = None, customreadings: tuple[CustomReading] = None):
		if additionalreadings is not None:
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

				self._addtocache(r, cached)

		if customreadings is not None:
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

		return True

	def process(self, text: str, problems: list[Problem], userdata = None) -> tuple[bool, str]:
		return self._process_text(text, problems, userdata)
