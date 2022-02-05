# requires mecab-python3, unidic, pykakasi
import os, sys, shutil, unidic, pykakasi
from .instanceprv import InstancePrv
from .problem import Problem
from .utils import is_kanji, has_kanji, all_kanji


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
			for kanji in additionalreadings:
				reading = additionalreadings[kanji]
				assert isinstance(reading, Reading), "Expected type Reading!"
				cached = []

				if reading.on:
					for k in reading.on:
						h = self._kana2hira(k)

						cached.append((k, h))

				if reading.kun:
					for h in reading.kun:
						k = self._hira2kana(h)

						cached.append((k, h))

				self._addtocache(kanji, cached)

		if customreadings is not None:
			for reading in customreadings:
				assert isinstance(reading, CustomReading), "Expected CustomReading type!"
				word = "".join(reading.on)

				repl = self.customreadings_opentag
				for i in range(len(reading.on)):
					k = reading.on[i]
					r = reading.kun[i]

					if is_kanji(k):
						repl += k + self.opentag + r + self.closetag
					else:
						repl += k
				repl += self.customreadings_closetag

				self.customreadings[word] = repl

		return True

	def process(self, text: str, problems: list[Problem], userdata = None) -> tuple[bool, str]:
		return self._process_text(text, problems, userdata)
