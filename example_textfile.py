"""
furiganamaker example
Copyright (C) 2022  Daniel Kollmann

Use of this source code is governed by an MIT-style
license that can be found in the LICENSE file or at
https://opensource.org/licenses/MIT.
"""

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

# this is just for testing, so you see the problems without adding additional readings
fixproblems = True

# add your own readings, for example from jisho.org. These readings override automatically determined readings. Sort by length!
kanjireadings = {
	"戸": furiganamaker.KanjiReading(("コ",), ("と", "ど")),  # from https://jisho.org/search/%E6%88%B8%20%23kanji
	"軽": furiganamaker.KanjiReading(("キョウ", "ケイ", "キン"), ("かる", "がる", "かろ")),  # from https://jisho.org/search/%E8%BB%BD%20%23kanji
	"間": furiganamaker.KanjiReading(("カン", "ケン", "ゲン"), ("あいだ", "あい", "ま")),  # from https://jisho.org/search/%E9%96%93%20%23kanji
	"近": furiganamaker.KanjiReading(("キン", "コン"), ("ちか", "じか")),  # from https://jisho.org/search/%E8%BF%91%23kanji
	"日": furiganamaker.KanjiReading(("ニチ", "ジツ", "ニ"), ("ひ", "び", "か")),  # from https://jisho.org/search/%E6%97%A5%20%23kanji
}

# add readings for words, when the automatic readings are incorrrect
wordreadings = [
	furiganamaker.WordReading(("行", "灯"), ("あん", "どん")),  # read 行灯 as あんどん. Turns into 行[あん]灯[どん]. See https://jisho.org/search/%E8%A1%8C%E7%81%AF
	furiganamaker.WordReading(("神", "秘", "性"), ("しん", "ぴ", "せい")),  # read 神秘性 as しんぴせい. Turns into 神[しん]秘[ぴ]性[せい]. See https://jisho.org/search/%E7%A5%9E%E7%A7%98%E6%80%A7
	furiganamaker.WordReading(("入", "って"), ("はい", "って")),  # read 入って as はいって. Turns into 入[はい]って. See https://jisho.org/search/%E5%85%A5%E3%81%A3%E3%81%A6
	furiganamaker.WordReading(("百", "科", "事", "典"), ("ひゃっ", "か", "じ", "てん")),  # See https://jisho.org/search/%E7%99%BE%E7%A7%91%E4%BA%8B%E5%85%B8
	furiganamaker.WordReading(("化", "猫", "遊", "女"), ("ばけ", "ねこ", "ゆう", "じょ")),  # See https://ja.wikipedia.org/wiki/%E5%8C%96%E7%8C%AB%E9%81%8A%E5%A5%B3
]

maker = furiganamaker.Instance("[", "]", kakasi, mecab, jam)  # tags furigana as "kanji[furigana]"

if fixproblems:
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
