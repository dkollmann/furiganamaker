from .instancedata import InstanceData
from .problem import Problem
from .utils import is_kanji, has_kanji, all_kanji


class InstancePrv(InstanceData):
	def __init__(self):
		self.mecab = None
		self.kakasi = None
		self.jam = None
		self.readingscache = {}
		self.customreadings = {}

	@staticmethod
	def _has_reading_kana(readings, newkana):
		for r in readings:
			if r[0] == newkana:
				return True

		return False

	@staticmethod
	def _has_reading_hira(readings, newhira):
		for r in readings:
			if r[1] == newhira:
				return True

		return False

	def _get_kanjireading(self, katakana, kanji):
		if kanji in self.readingscache:
			return self.readingscache[kanji]

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

						foundreadings.append((k, h))

				kun_readings = data.chars[0].rm_groups[0].kun_readings
				for r in kun_readings:
					h = r.value.lstrip("-")

					dot = h.find(".")
					if dot >= 0:
						h = h[:dot]

					if not InstancePrv._has_reading_hira(foundreadings, h):
						k = self._hira2kana(h)

						foundreadings.append((k, h))

		# check mecab
		if self.mecab is not None:
			node = self.mecab.parseToNode(kanji + "一")  # this is a hack to get the Chinese reading
			while node:
				if len(node.surface) > 0:
					sp = node.feature.split(",")
					if len(sp) >= 7:
						kana = sp[6]

						# when the kana is the whole word, skip it
						if len(kana) != len(katakana) and not InstancePrv._has_reading_kana(foundreadings, kana):
							hira = self._kana2hira(kana)

							foundreadings.append((kana, hira))

					node = node.bnext
				else:
					node = node.next

		self._addtocache(kanji, foundreadings)

		return foundreadings

	def _find_reading(self, kanji, katakana, readings, problems, userdata):
		showproblem = True

		# check if this is a number
		if len(kanji) == 2 and kanji[0] in InstanceData._kanjinumbers:
			showproblem = False

		# check if this is a "saying"
		if len(kanji) == 2 and kanji[1] == "々":
			return False

		# get all the readings for the kanji
		katakanaleft = katakana

		for k in kanji:
			found = False

			# check if we have an additional reading for this
			foundreadings = self._get_kanjireading(katakana, k)

			# check if we found something
			if len(foundreadings) < 1:
				problems.append(Problem("Failed to find any reading for \"" + k + "\".", k, userdata))
				return False

			# try to match the kanji with the reading
			for kana, hira in foundreadings:
				if katakanaleft.startswith(kana):
					found = True
					readings.append(hira)
					katakanaleft = katakanaleft[len(kana):]
					break

			# when one kanji fails we have to abort
			if not found:
				if showproblem:
					problems.append(Problem("Could not match kanji \"" + k + "\" to kana \"" + katakanaleft + "\".", k, userdata))
				return False

		# check if all of the reading was "consumed"
		if len(katakanaleft) > 0:
			problems.append(Problem("Matched all kanji of \"" + kanji + "\" to \"" + katakana + "\" but \"" + katakanaleft + "\" was left over.", kanji, userdata))
			return False

		assert len(readings) > 0, "There should be readings here"
		return True

	@staticmethod
	def _split_kanji(kanji):
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
	def _split_katakana(hiraganasplit, katakana):
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
	def _split_hiragana(kanjisplit, hiragana, katakana):
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

	def _addtocache(self, kanji, cachedreadings):
		sort = sorted(cachedreadings, key=lambda x: len(x[0]), reverse=True)
		self.readingscache[kanji] = sort

	@staticmethod
	def _fix_longvowels(original, katakana):
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
	def _split_custreadtags(text, opentag, closetag):
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

	def _process_textpart(self, text: str, problems: list[Problem], userdata) -> tuple[bool, str]:
		assert self.kakasi is not None, "An kakasi instance is required."

		result = ""
		hasfurigana = False
		conv = self.kakasi.convert(text)

		for c in conv:
			orig = c["orig"]
			hira = c["hira"]
			kana = c["kana"]

			assert len(hira) == len(kana), "Expected both to be the same length"

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
				split_hira = [ (hira, True) ]
				split_kana = [ (kana, True) ]

			# for each kanji block, try to match the individual hiragana
			s = ""
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
						matchedkana = self._find_reading(kanji, katakana, readings, problems, userdata)

					if matchedkana:
						for k in range(len(kanji)):
							s += kanji[k] + self.opentag + readings[k] + self.closetag
					else:
						s += kanji + self.opentag + hiragana + self.closetag

				else:
					s += kanji

			result += s

		return (hasfurigana, result)

	def _process_text(self, text: str, problems: list[Problem], userdata) -> tuple[bool, str]:
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

		textparts2 = []
		for t, iscust in textparts:
			if iscust:
				textparts2.append(t)
				hasfurigana = True
			else:
				hasfuri, str = self._process_textpart(t, problems, userdata)

				textparts2.append(str)

				if hasfuri:
					hasfurigana = True

		tfinal = "".join(textparts2)

		return (hasfurigana, tfinal)
