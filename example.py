# requires mecab-python3, unidic, pykakasi, jamdict, wheel, jamdict-data package
import os, sys, shutil, MeCab, pykakasi
from jamdict import Jamdict

import __init__ as furiganamaker

mecab = MeCab.Tagger()
kakasi = pykakasi.kakasi()
jam = Jamdict()

problems = []
maker = furiganamaker.Instance("{", "}", problems, kakasi, mecab, jam)
