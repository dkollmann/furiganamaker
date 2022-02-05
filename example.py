# requires mecab-python3, unidic, pykakasi, jamdict, wheel, jamdict-data package
import os, sys, shutil, MeCab, pykakasi
from jamdict import Jamdict

import __init__ as furiganamaker

mecab = MeCab.Tagger()
kakasi = pykakasi.kakasi()
jam = Jamdict()

additionalreadings = {

}

customreadings = {

}

problems = []
maker = furiganamaker.Instance("{", "}", kakasi, mecab, jam)

if maker.init(additionalreadings, customreadings):

	maker.process("ffff", problems)
