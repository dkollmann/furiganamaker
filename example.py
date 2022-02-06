# requires mecab-python3, unidic, pykakasi, jamdict, wheel, jamdict-data package
import os
import sys
import MeCab
import pykakasi
from jamdict import Jamdict

# hack only for this example. Not needed for your own code.
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import furiganamaker

mecab = MeCab.Tagger()
kakasi = pykakasi.kakasi()
jam = Jamdict()

kanjireadings = {

}

wordreadings = {

}

problems = []
maker = furiganamaker.Instance("[", "]", kakasi, mecab, jam)

maker.add_kanjireadings(kanjireadings)
maker.add_wordreadings(wordreadings)

hasfurigana, newtext = maker.process("ナイトシティで動物を見たのは初めてだ。もちろん、ゴキブリを除いてな", problems)

print(newtext)
