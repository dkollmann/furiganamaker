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

import sys


class Problem:
	"""
	Represents a problem found while processing text. See Instance.process().
	"""
	def __init__(self, description: str, kanji: str, userdata):
		"""
		Creates a new problem object. Only created by the Instance and not the user.
		:param description: A text describing the problem.
		:param kanji: The kanji the problem is related to. Can be None.
		:param userdata: The userdata given as an argument to Instance.process().
		"""
		self.description = description
		self.kanji = kanji
		self.userdata = userdata


class Problems:
	"""
	Helper class for functions to print problems.
	"""
	@staticmethod
	def print_all(problems: list[Problem], limit: int = 100000) -> None:
		"""
		Prints all found problems on the screen.
		:param problems: The list of problems after calling Instance.process().
		:param limit: Limit the number of problems listed.
		:return:
		"""
		for i in range(min(limit, len(problems))):
			p = problems[i]
			if p.userdata is not None:
				print(str(p.userdata) + ": " + p.description)
			else:
				print(p.description)
		print("Found " + str(len(problems)) + " problems...")

	@staticmethod
	def print_kanjiproblems_list(problems: list[Problem]) -> list[str]:
		"""
		Prints all problems found for each kanji with a problem. Sorted by the number of problems.
		:param problems: The list of problems after calling Instance.process().
		:return: The list of kanjis with problems, sorted by the number of problems.
		"""
		counted = {}
		for p in problems:
			if p.kanji is not None:
				if p.kanji in counted:
					counted[p.kanji] += 1
				else:
					counted[p.kanji] = 1

		sort = sorted(counted.items(), key=lambda x: x[1], reverse=True)

		sys.stdout.write("Issues: ")
		for k, n in sort:
			sys.stdout.write(k + ": " + str(n) + ", ")
		print(".")

		return sort

	@staticmethod
	def print_kanjiproblems(problems: list[Problem], kanji: str, limit: int = 10) -> None:
		"""
		Prints all problems for a specific kanji.
		:param problems: The list of problems after calling Instance.process().
		:param kanji: The kanji to print problems for.
		:param limit: Limit the number of problems being printed.
		:return:
		"""
		i = 0
		for p in problems:
			if p.kanji == kanji:
				i += 1
				if p.userdata is not None:
					print(str(p.userdata) + ": " + p.description)
				else:
					print(p.description)
				if i >= limit:
					break
