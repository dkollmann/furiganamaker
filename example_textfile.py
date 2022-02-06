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
	"戸": furiganamaker.KanjiReading(("コ",), ("と", "ど"))  # from https://jisho.org/search/%E6%88%B8%20%23kanji
}

# add readings for words, when the automatic readings are incorrrect
wordreadings = [
	furiganamaker.WordReading(("行", "灯", "の", "油"), ("あん", "どん", "の", "あぶら"))  # read 行灯の油 as あんどんのあぶら. Turns into 行[あん]灯[どん]の油[あぶら].
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
for i in range(len(lines)):
	hasfurigana, furiganatext = maker.process(lines[i], problems, "Line " + str(i+1))

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
