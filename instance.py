"""
furiganamaker
Copyright (C) 2022  Daniel Kollmann

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

# requires mecab-python3, unidic, pykakasi
import os
from typing import Sequence
import pykakasi
import unidic

from .instanceprv import InstancePrv, CachedReading
from .problem import Problem
from .utils import is_kanji


class KanjiReading:
	"""
	Represents the different readings for a given kanji.
	"""
	def __init__(self, onreadings: Sequence[str], kunreadings: Sequence[str]):
		"""
		Creates a reading for a kanji.
		:param onreadings: The Chinese on readings in katakana.
		:param kunreadings: The Japanese kun readings in hiragana.
		"""
		assert isinstance(onreadings, tuple) or isinstance(onreadings, list), "Expected tuple or list for on readings. Did you for get a comma?"
		assert isinstance(kunreadings, tuple) or isinstance(kunreadings, list), "Expected tuple or list for kun readings. Did you for get a comma?"

		for kun in kunreadings:
			assert "." not in kun, "Did you accidentially copy the '.'? Only use what is in front of the dot."
			assert "-" not in kun, "Did you accidentially copy the '-'? Only use what is behind the '-'."

		self.on = onreadings
		self.kun = kunreadings


class WordReading:
	"""
	Represents a reading for a word, which can contain multiple kanjis.
	"""
	def __init__(self, onreading: Sequence[str], kunreading: Sequence[str]):
		"""
		Creates a reading for a word, allowing multiple kanjis.
		Both readings must consist of a tuple containing the individual parts of the word.
		:param onreading: The Chinese on readings in katakana.
		:param kunreading: The Japanese kun readings in hiragana.
		"""
		assert isinstance(onreading, tuple) or isinstance(onreading, list), "Expected tuple or list for on readings. Did you for get a comma?"
		assert isinstance(kunreading, tuple) or isinstance(kunreading, list), "Expected tuple or list for kun readings. Did you for get a comma?"
		assert len(onreading) == len(kunreading), "Both readings must have the same length as one is the translation of the other."

		self.on = onreading
		self.kun = kunreading


class Instance(InstancePrv):
	"""
	This class implements all the private functions for Instance.
	"""
	def __init__(self, opentag: str, closetag: str, kakasi: pykakasi.kakasi, mecabtagger = None, jamdict = None):
		"""
		Creates a new instance.
		:param opentag: The tag used to mark the beginning of a furigana block.
		:param closetag: The tag used to mark the end of a furigana block.
		:param kakasi: The main library used to generate the furigana readings and convert readings in general.
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

	def add_kanjireadings(self, additionalreadings: dict[str, KanjiReading]) -> None:
		"""
		Adds readings for individual kanjis.
		:param additionalreadings: This is a dictionary where for every kanji/key in it, there is a KanjiReading object.
		:return:
		"""
		for kanji in additionalreadings:
			assert len(kanji) == 1, "Only individual kanji are supported. Use add_wordreadings to add readings for words."
			reading = additionalreadings[kanji]
			assert isinstance(reading, KanjiReading), "Expected type KanjiReading!"
			cached = []

			if reading.on:
				for k in reading.on:
					h = self._kana2hira(k)

					cached.append(CachedReading(k, h))

			if reading.kun:
				for h in reading.kun:
					k = self._hira2kana(h)

					cached.append(CachedReading(k, h))

			self._addtocache(kanji, cached)

	def add_wordreadings(self, customreadings: Sequence[WordReading]) -> None:
		"""
		Adds a reading for a words.
		:param customreadings: A list of readings for different words.
		:return:
		"""
		for reading in customreadings:
			assert isinstance(reading, WordReading), "Expected WordReading type!"
			word = "".join(reading.on)

			repl = self.customreadings_opentag
			for i in range(len(reading.on)):
				k = reading.on[i]
				r = reading.kun[i]

				if len(k) == 1 and is_kanji(k):
					repl += k + self.opentag + r + self.closetag
				else:
					repl += k
			repl += self.customreadings_closetag

			self.customreadings[word] = repl

	def process(self, text: str, problems: list[Problem], userdata = None) -> tuple[bool, str]:
		"""
		Takes a string and adds furigana to it.
		:param text: The text you want to add furigana to it.
		:param problems: Any problem found during the processing is added here.
		:param userdata: This data is added to any problem which was found, allowing you to trackback where the text came from, e.g. line in file.
		:return: Returns a tuple (hasfurigana, processedtext), where hasfurigana tells you if furigana has been added and processedtext is the resulting text.
		"""
		return self._process_text(text, problems, userdata)
