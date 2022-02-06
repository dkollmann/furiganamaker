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
