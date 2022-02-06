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

from .instancedata import InstanceData
from .problem import Problem
from .utils import is_kanji, has_kanji


class CachedReading:
	"""
	An entry for the readings cache to improve performance.
	"""

	def __init__(self, katakana, hiragana):
		"""
		Creates a new cache entry.
		:param katakana: The reading in katakana.
		:param hiragana: The reading in furigana.
		"""
		self.katakana = katakana
		self.hiragana = hiragana


class InstancePrv(InstanceData):
	"""
	Base class of Instance which implements all the private functions.
	"""

	def __init__(self):
		"""
		Creates some default values for members.
		"""
		self.mecab = None
		self.kakasi = None
		self.jam = None
		self.opentag: str = ""
		self.closetag: str = ""
		self.customreadings_opentag: str = "<"
		self.customreadings_closetag: str = ">"
		self.readingscache: dict[str, list[CachedReading]] = {}
		self.customreadings: dict[str, str] = {}

	@staticmethod
	def _has_reading_kana(readings: list[CachedReading], katakana: str) -> bool:
		"""
		Checks if there is already a reading, based on katakana.
		:param readings: The list of readings to check.
		:param katakana: The katakana to search for.
		:return: Returns true when 'readings' contains an entry for 'katakana'.
		"""
		for r in readings:
			if r.katakana == katakana:
				return True

		return False

	@staticmethod
	def _has_reading_hira(readings: list[CachedReading], hiragana: str) -> bool:
		"""
		Checks if there is already a reading, based on hiragana.
		:param readings: The list of readings to check.
		:param hiragana: The hiragana to search for.
		:return: Returns true when 'readings' contains an entry for 'hiragana'.
		"""
		for r in readings:
			if r.hiragana == hiragana:
				return True

		return False

	def _get_kanjireading(self, kanji: str, katakana: str = None) -> list[CachedReading]:
		"""
		Gets a reading for a kanji. Uses the cache to improve performance.
		:param kanji: The kanji to find a reading for.
		:param katakana: The katakana of the complete word the kanji is part of. Only needed when using mecab.
		:return: A list of readings for 'kanji'.
		"""
		if kanji in self.readingscache:
			return self.readingscache[kanji]

		assert len(kanji) == 1, "Has to be a single kanji"

		foundreadings = []

		# check jamkit
		if self.jam is not None:
			data = self.jam.lookup(kanji, strict_lookup=True, lookup_ne=False)
			if len(data.chars) > 0:
				assert len(data.chars) == 1
				assert len(data.chars[0].rm_groups) == 1

				on_readings = data.chars[0].rm_groups[0].on_readings
				for r in on_readings:
					k = r.value

					if not InstancePrv._has_reading_kana(foundreadings, k):
						h = self._kana2hira(k)

						foundreadings.append(CachedReading(k, h))

				kun_readings = data.chars[0].rm_groups[0].kun_readings
				for r in kun_readings:
					h = r.value.lstrip("-")

					dot = h.find(".")
					if dot >= 0:
						h = h[:dot]

					if not InstancePrv._has_reading_hira(foundreadings, h):
						k = self._hira2kana(h)

						foundreadings.append(CachedReading(k, h))

		# check mecab
		if self.mecab is not None:
			assert katakana is not None, "When using mecab, we need the katakana to avoid using the reading of the complete word."
			node = self.mecab.parseToNode(kanji + "一")  # this is a hack to get the Chinese reading
			while node:
				if len(node.surface) > 0:
					sp = node.feature.split(",")
					if len(sp) >= 7:
						kana = sp[6]

						# when the kana is the whole word, skip it
						if len(kana) != len(katakana) and not InstancePrv._has_reading_kana(foundreadings, kana):
							hira = self._kana2hira(kana)

							foundreadings.append(CachedReading(kana, hira))

					node = node.bnext
				else:
					node = node.next

		# check pykakasi
		conv = self.kakasi.convert(kanji)
		for c in conv:
			kana = c["kana"]

			if not InstancePrv._has_reading_kana(foundreadings, kana):
				hira = c["hira"]

				foundreadings.append(CachedReading(kana, hira))

		return self._addtocache(kanji, foundreadings)

	def _find_reading(self, kanji: str, wordoriginal: str, wordkatakana: str, readings: list[str], problems: list[Problem], userdata) -> bool:
		"""
		Finds a reading for a kanji.
		:param kanji: The kanji to find a reading for.
		:param wordoriginal: The original text of the complete word.
		:param wordkatakana: The katakana of the complete word the kanji is part of.
		:param readings: The list of readings that have been found.
		:param problems: The list of problems that occured.
		:param userdata: The user data added to found problems.
		:return: Returns true when readings could be found.
		"""
		showproblem = True

		# check if this is a number
		if len(kanji) == 2 and kanji[0] in InstanceData._kanjinumbers:
			showproblem = False

		# check if this is a "saying"
		if len(kanji) == 2 and kanji[1] == "々":
			return False

		# get all the readings for the kanji
		katakanaleft = wordkatakana

		for k in kanji:
			found = False

			# check if we have an additional reading for this
			foundreadings = self._get_kanjireading(k, wordkatakana)

			# check if we found something
			if len(foundreadings) < 1:
				problems.append(Problem("Failed to find any reading for \"" + k + "\". Occurence: \"" + wordoriginal + "\".", k, userdata))
				return False

			# try to match the kanji with the reading
			for r in foundreadings:
				if katakanaleft.startswith(r.katakana):
					found = True
					readings.append(r.hiragana)
					katakanaleft = katakanaleft[len(r.katakana):]
					break

			# when one kanji fails we have to abort
			if not found:
				if showproblem:
					problems.append(Problem("Could not match kanji \"" + k + "\" to kana \"" + katakanaleft + "\". Occurence: \"" + wordoriginal + "\".", k, userdata))
				return False

		# check if all of the reading was "consumed"
		if len(katakanaleft) > 0:
			problems.append(Problem("Matched all kanji of \"" + kanji + "\" to \"" + wordkatakana + "\" but \"" + katakanaleft + "\" was left over. Occurence: \"" + wordoriginal + "\".", kanji, userdata))
			return False

		assert len(readings) > 0, "There should be readings here"
		return True

	@staticmethod
	def _split_kanji(kanji: str) -> list[tuple[str, bool]]:
		"""
		Splits a string with multiple letters into blocks of kanjis.
		:param kanji: The text to split.
		:return: Returns a list where 'text' was split into parts of (text, iskanji).
		"""
		result = []

		start = 0
		waskanji = is_kanji(kanji[0])

		i = 1
		while i < len(kanji):
			k = kanji[i]
			iskanji = is_kanji(k)

			if waskanji != iskanji:
				kk = kanji[start:i]
				result.append((kk, waskanji))

				start = i
				waskanji = iskanji

			i += 1

		if start < len(kanji):
			kk = kanji[start:]
			result.append((kk, waskanji))

		return result

	@staticmethod
	def _split_katakana(hiraganasplit: list[tuple[str, bool]], katakana: str) -> list[tuple[str, bool]]:
		"""
		Splits katakana into the same parts as a hiragana.
		:param hiraganasplit: The output of _split_hiragana().
		:param katakana: The katakana to split.
		:return: A list like 'hiraganasplit' but for 'katakana'.
		"""
		# sanity check first
		ln = 0
		for t, ik in hiraganasplit:
			ln += len(t)
		assert ln == len(katakana), "The hiragana and the katakana must be the same length"

		# apply the same split to the katakana
		result = []
		start = 0
		for t, ik in hiraganasplit:
			k = katakana[start:len(t)]
			result.append((k, ik))
			start = len(t)

		assert len(result) == len(hiraganasplit), "Both splits must have the same length"

		return result

	@staticmethod
	def _split_hiragana(kanjisplit: list[tuple[str, bool]], hiragana: str, katakana: str) -> list[tuple[str, bool]]:
		"""
		Splits hiragana based on the split word with kanji characters.
		:param kanjisplit: The output of _split_kanji().
		:param hiragana: The hiragana representing the concat string of 'kanjisplit'.
		:param katakana: The katakana representing the concat string of 'kanjisplit'.
		:return: A list like 'kanjisplit' but for 'hiragana'.
		"""
		result = []

		# the conversion to hiragana will also convert any katakana, so we have to reverse this
		assert len(hiragana) == len(katakana), "Expected both to be the same length"

		# we get better results when matching the hiragana from back to start
		end = len(hiragana)
		endfind = end
		for i in range(len(kanjisplit)):
			e = kanjisplit[len(kanjisplit) - i - 1]

			# ignore kanji elements
			if e[1]:
				endfind -= 1
				continue

			# try to find the non-kanji text
			t = e[0]
			text = hiragana
			pos = hiragana.rfind(t, 0, endfind)

			# handle the case that the pronunciation of a character was changed
			if pos < 0 and len(t) == 1 and t in InstancePrv._basehiragana:
				t2 = InstancePrv._basehiragana[t]
				pos = hiragana.rfind(t2, 0, endfind)
			# todo should 'e' be updated to have the hiragana pronunciation?

			# check if this is a unwanted katakana conversion
			if pos < 0:
				text = katakana
				pos = katakana.rfind(t, 0, endfind)

			assert pos >= 0, "Failed to find hiragana"

			start = pos + len(t)
			if start < end:
				kanji = text[start:end]
				result.append((kanji, True))

			result.append(e)
			end = pos
			endfind = end

		if end >= 0:
			kanji = hiragana[:end]

			result.append((kanji, True))

		result.reverse()

		# sanity check results
		assert len(kanjisplit) == len(result), "Both splits must be the same length"
		for i in range(len(kanjisplit)):
			assert kanjisplit[i][1] == result[i][1], "The type of elements must be the same"

			if not kanjisplit[i][1]:
				assert kanjisplit[i][0] == result[i][0], "Non-kanji elements must be the same"

		return result

	def _kana2hira(self, kana: str) -> str:
		"""
		Converts katakana to hiragana.
		:param kana: The katakana to convert.
		:return: Returns the hiragana translation.
		"""
		conv = self.kakasi.convert(kana)

		hira = ""
		for c in conv:
			hira += c["hira"]

		assert len(kana) == len(hira), "Expected both to be the same length"

		return hira

	def _hira2kana(self, hira: str) -> str:
		"""
		Converts hiragana to katakana.
		:param hira: The hiragana to convert.
		:return: Returns the katakana translation.
		"""
		conv = self.kakasi.convert(hira)

		kana = ""
		for c in conv:
			kana += c["kana"]

		assert len(kana) == len(hira), "Expected both to be the same length"

		return kana

	def _addtocache(self, kanji: str, cachedreadings: list[CachedReading]) -> list[CachedReading]:
		"""
		Adds a reading to the cache. The main use of this function is sorting the readings before adding them. This is very important!!
		:param kanji: The kanji to add readings for.
		:param cachedreadings: The list of readings.
		:return: Returns 'cachedreadings', but sorted by length.
		"""
		sort = sorted(cachedreadings, key=lambda x: len(x.katakana), reverse=True)

		self.readingscache[kanji] = sort

		return sort

	@staticmethod
	def _fix_longvowels(original: str, katakana: str) -> str:
		"""
		Replaces hiragana long vowels, written in katakana, with 'ー'.
		:param original: The original text we check for 'ー'.
		:param katakana: The katakana where 'ー' has been replaced with vowel characters.
		:return: Returns 'katakana' but with long vowels written with 'ー'.
		"""
		# when the original string uses a 'ー' character, it is lost during the conversion to katakana, so we restore it
		pos = original.find("ー")

		while pos > 0:
			# determine the vowel which is represented
			vowel = original[pos - 1:pos]
			vowel_ord = ord(vowel)

			if vowel_ord in InstancePrv._katakana_vowels:
				vowel2 = InstancePrv._katakana_vowels[vowel_ord]

				# find the occurence and replace it
				katakana = katakana.replace(vowel + vowel2, vowel + "ー")

			pos = original.find("ー", pos + 1)

		return katakana

	@staticmethod
	def _split_custreadtags(text: str, opentag: str, closetag: str) -> list[tuple[str, bool]]:
		"""
		Splits a text based on the word readings that have been applied.
		:param text: The text that has word readings in it.
		:param opentag: The tag marking a word reading beginning.
		:param closetag: The tag to marking a word reading end.
		:return: Returns a list where 'text' was split into parts of (text, iswordreading).
		"""
		result = []

		start = 0
		while True:
			pos = text.find(opentag, start)
			if pos < 0:
				break

			pos2 = text.find(closetag, pos)
			assert pos2 > pos, "Missing close tag"

			if start < pos:
				# add the previous text
				t = text[start:pos]
				result.append((t, False))

			# add this text
			t2 = text[pos + 1:pos2]
			result.append((t2, True))

			start = pos2 + 1

		# add remaining text
		if start < len(text):
			t = text[start:]
			result.append((t, False))

		return result

	@staticmethod
	def _split_urls(textparts: list[tuple[str, bool]]) -> list[tuple[str, bool]]:
		i = 0
		while i < len(textparts):
			t, iscust = textparts[i]

			if iscust:
				i += 1
				continue

			pos = t.find("://")
			if pos < 0:
				i += 1
				continue

			# find start
			a = pos - 1
			while a >= 0 and not t[a].isspace():
				a -= 1

			# find end
			b = pos + 3
			while b < len(t) and not t[b].isspace():
				b += 1

			prefix = t[:a+1]
			url = t[a+1:b]
			postfix = t[b:]

			# adjust the textparts
			textparts[i] = (prefix, False)
			textparts.insert(i + 1, (url, True))
			textparts.insert(i + 2, (postfix, False))

			i += 2

		return textparts

	def _process_textpart(self, text: str, problems: list[Problem], userdata) -> tuple[bool, str]:
		"""
		Adds furigana to a given text. The difference to _process_text() is that _process_text() applies custom word readings.
		:param text: The text to add furigana to.
		:param problems: The problems that have been found.
		:param userdata: The user data added to every problem found.
		:return: Returns a tuple (hasfurigana, text). When no furigana has been added, 'hasfurigana' is False.
		"""
		assert self.kakasi is not None, "An kakasi instance is required."

		result = ""
		hasfurigana = False
		conv = self.kakasi.convert(text)

		for c in conv:
			orig = c["orig"]
			hira = c["hira"]
			kana = c["kana"]

			assert len(hira) == len(kana), "Expected both to be the same length"

			# handle new lines
			if orig.endswith("\n"):
				result += orig
				continue

			# handle the case of an untranslated kanji
			if len(hira) < 1:
				problems.append(Problem("Failed to translate '" + orig + "'.", orig, userdata))
				continue

			# ignore any conversion other than kanji
			if not has_kanji(orig) or orig == hira:
				result += orig
				continue

			hasfurigana = True

			# find the kanji blocks
			split_kanjis = InstancePrv._split_kanji(orig)

			if len(split_kanjis) > 1:
				kana = InstancePrv._fix_longvowels(orig, kana)

				split_hira = InstancePrv._split_hiragana(split_kanjis, hira, kana)
				split_kana = InstancePrv._split_katakana(split_hira, kana)
			else:
				assert split_kanjis[0][1], "This must be a kanji element"
				split_hira = [(hira, True)]
				split_kana = [(kana, True)]

			# for each kanji block, try to match the individual hiragana
			s = ""
			readings = []
			for i in range(len(split_kanjis)):
				kanji = split_kanjis[i][0]
				iskanji = split_kanjis[i][1]
				hiragana = split_hira[i][0]
				katakana = split_kana[i][0]

				matchedkana = False

				# check if matching needs to happen
				if iskanji:
					if len(katakana) > 1:
						readings = []
						matchedkana = self._find_reading(kanji, orig, katakana, readings, problems, userdata)

					if matchedkana:
						for k in range(len(kanji)):
							s += kanji[k] + self.opentag + readings[k] + self.closetag
					else:
						s += kanji + self.opentag + hiragana + self.closetag

				else:
					s += kanji

			result += s

		return hasfurigana, result

	def _process_text(self, text: str, problems: list[Problem], userdata) -> tuple[bool, str]:
		"""
		Adds furigana to a given text. The difference to _process_textpart() is that _process_textpart() does not apply custom word readings.
		:param text: The text to add furigana to.
		:param problems: The problems that have been found.
		:param userdata: The user data added to every problem found.
		:return: Returns a tuple (hasfurigana, text). When no furigana has been added, 'hasfurigana' is False.
		"""
		# because of our format, the text cannot contain brackets
		assert self.opentag not in text and self.closetag not in text, "We have to use a different syntax"
		assert self.customreadings_opentag not in text and self.customreadings_closetag not in text, "We have to use a different tag for custom readings"

		# try to find custom readings
		hasfurigana = False
		text2 = text
		for kanji in self.customreadings:
			reading = self.customreadings[kanji]

			t = text2.replace(kanji, reading)

			if len(t) != len(text2):
				hasfurigana = True

			text2 = t

		textparts = InstancePrv._split_custreadtags(text2, self.customreadings_opentag, self.customreadings_closetag)

		textparts = InstancePrv._split_urls(textparts)

		textparts2 = []
		for t, iscust in textparts:
			if iscust:
				textparts2.append(t)
				hasfurigana = True
			else:
				hasfuri, result = self._process_textpart(t, problems, userdata)

				textparts2.append(result)

				if hasfuri:
					hasfurigana = True

		tfinal = "".join(textparts2)

		return hasfurigana, tfinal
