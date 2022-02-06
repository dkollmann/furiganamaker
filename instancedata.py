def katakana_vowels_init():
	"""
	Helper function which generates a dictionary where for ord(katakana), we get the katakana vowel. So ord(キ) provides 'イ'.
	:return: the generated dictionary.
	"""
	result = {}

	vowels = {
		"ア": ("ア", "カ", "サ", "タ", "ナ", "ハ", "マ", "ヤ", "ラ", "ワ", "ガ", "ザ", "ダ", "バ", "パ", "ャ"),
		"イ": ("イ", "キ", "シ", "チ", "ニ", "ヒ", "ミ", "リ", "ヰ", "ギ", "ジ", "ヂ", "ビ", "ピ"),
		"ウ": ("ウ", "ク", "ス", "ツ", "ヌ", "フ", "ム", "ユ", "ル", "グ", "ズ", "ヅ", "ブ", "プ", "ュ"),
		"エ": ("エ", "ケ", "セ", "テ", "ネ", "ヘ", "メ", "レ", "ヱ", "ゲ", "ゼ", "デ", "ベ", "ペ"),
		"オ": ("オ", "コ", "ソ", "ト", "ノ", "ホ", "モ", "ヨ", "ロ", "ヲ", "ゴ", "ゾ", "ド", "ボ", "ポ", "ョ")
	}

	for v in vowels:
		for k in vowels[v]:
			result[ord(k)] = v

	return result


class InstanceData:
	"""
	This class provides some pre-generated data for InstancePrv.
	"""

	""" A dictionary where for ord(katakana), we get the katakana vowel. So ord(キ) provides 'イ'. """
	_katakana_vowels = katakana_vowels_init()

	""" Maps a variant of a hiragana wording to its base wording. """
	_basehiragana = {
		"が": "か", "ざ": "さ", "だ": "た", "ば": "は", "ぱ": "は",
		"ぎ": "き", "じ": "し", "ぢ": "ち", "び": "ひ", "ぴ": "ひ",
		"ぐ": "く", "ず": "す", "づ": "つ", "ぶ": "ふ", "ぷ": "ふ",
		"げ": "け", "ぜ": "せ", "で": "て", "べ": "へ", "ぺ": "へ",
		"ご": "こ", "ぞ": "そ", "ど": "と", "ぼ": "ほ", "ぽ": "ほ"
	}

	""" A list of most of the kanji numbers. Used to detect numbers. """
	_kanjinumbers = ("一", "二", "三", "四", "五", "六", "七", "八", "九", "十", "零")
