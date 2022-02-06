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

# add your own readings, for example from jisho.org. These readings override automatically determined readings.
kanjireadings = {
	#"応": furiganamaker.KanjiReading(("オウ", "ヨウ", "ノウ"), ("あた", "まさに", "こた"))  # from https://jisho.org/search/%E5%BF%9C%20%23kanji
}

# add readings for words, when the automatic readings are incorrrect
wordreadings = {
	#furiganamaker.WordReading(("真", "の", "戦", "士"), ("しん", "の", "せん", "し"))  # read 真の戦士 as しんのせんし. Turns into 真[しん]の戦[せん]士[し].
}

maker = furiganamaker.Instance("[", "]", kakasi, mecab, jam)  # tags furigana as "kanji[furigana]"

maker.add_kanjireadings(kanjireadings)
maker.add_wordreadings(wordreadings)

problems = []
hasfurigana, newtext = maker.process("ナイトシティで動物を見たのは初めてだ。もちろん、ゴキブリを除いてな", problems)

print(newtext)
