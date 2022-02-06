# requires mecab-python3, unidic, pykakasi, jamdict, wheel, jamdict-data package
import os
import sys
import MeCab
import pykakasi
from jamdict import Jamdict

# hack only for this example. Not needed for your own code.
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import furiganamaker

# required kakasi instance for converting readings
kakasi = pykakasi.kakasi()

# optional mecab tagger for additional readings
mecab = MeCab.Tagger()

# optional jamdict for additional readings
jam = Jamdict()

# add your own readings, for example from jisho.org. These readings override automatically determined readings.
kanjireadings = {
	#"応": furiganamaker.KanjiReading(("オウ", "ヨウ", "ノウ"), ("あた", "まさに", "こた"))  # from https://jisho.org/search/%E5%BF%9C%20%23kanji
}

# add readings for words, when the automatic readings are incorrrect
wordreadings = [
	#furiganamaker.WordReading(("真", "の", "戦", "士"), ("しん", "の", "せん", "し"))  # read 真の戦士 as しんのせんし. Turns into 真[しん]の戦[せん]士[し].
]

maker = furiganamaker.Instance("[", "]", kakasi, mecab, jam)  # tags furigana as "kanji[furigana]"

maker.add_kanjireadings(kanjireadings)
maker.add_wordreadings(wordreadings)


# read input lines
with open("example_textfile_input.txt", "r", encoding="utf8") as f:
	lines = f.readlines()


# add furigana
problems = []
furiganalines = []
for line in lines:
	hasfurigana, furiganatext = maker.process(line, problems)

	furiganalines.append(furiganatext)


# write output file
with open("example_textfile_output.txt", "w", encoding="utf8") as f:
	f.writelines(furiganalines)


# print problems
if len(problems) > 0:
	# print 100 problems
	furiganamaker.Problems.print_all(problems, 100)

	# sort problems by kanji
	sortedkanji = furiganamaker.Problems.print_kanjiproblems_list(problems)

	# show top problems
	k = sortedkanji[0][0]
	furiganamaker.Problems.print_kanjiproblems(problems, k, 10)
