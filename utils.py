def is_kanji(ch: str) -> bool:
	"""
	Checks if a given character is a kanji or not.
	:param ch: The character to check.
	:return: Returns True when 'ch' is a kanji.
	"""
	assert len(ch) == 1, "Expected single character!"

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
