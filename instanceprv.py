from problem import Problem

class InstancePrv:
	def __init__(self):
		self.readingscache = {}
		self.customreadings = {}

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

	def _process_textpart(self, text: str, problems: list[Problem], userdata) -> tuple[bool, str]:
		assert self.kakasi is not None, "An kakasi instance is required."

		str = ""
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
				str += orig
				continue

			hasfurigana = True

			# find the kanji blocks
			split_kanjis = split_kanji(orig)

			if len(split_kanjis) > 1:
				kana = fix_longvowels(orig, kana)

				split_hira = split_hiragana(split_kanjis, hira, kana)
				split_kana = split_katakana(split_hira, kana)
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
						matchedkana = find_reading(kanji, katakana, readings, userdata)

					if matchedkana:
						for k in range(len(kanji)):
							s += kanji[k] + self.opentag + readings[k] + self.closetag
					else:
						s += kanji + self.opentag + hiragana + self.closetag

				else:
					s += kanji

			str += s

		return (hasfurigana, str)

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

		textparts = split_custreadtags(text2, self.customreadings_opentag, self.customreadings_closetag)

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
