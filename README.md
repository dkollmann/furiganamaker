# furiganamaker
This library allows you to add furigana to Japanese kanji.


## Why a new library?
I could not find a library which allowed me to...
- Handle many different cases with modern/casual Japanese.
- List problems which were found during the process.
- Allow you to improve the results.


## What features does the library provide?
- Support for multiple conversion libraries for best results.
  - [pykakasi](https://github.com/miurahr/pykakasi)
  - [mecab-python3](https://github.com/SamuraiT/mecab-python3) (optional)
  - [jamdict](https://github.com/neocl/jamdict) (optional)
- Problems found during the process are collected and returned.
- Helper functions to filter and print problems, to easily improve results.
- Provide custom readings for kanji, to improve results.
- Provide custom readings for words, to improve results.
- Match furigana to individual kanjis, instead of just having one furigana for each word.
- Cache readings to improve performance.
- Several small improvements:
  - Correctly retain katakana when mixed with kanji.
  - Handle kanji numbers.
  - Handle URLs.


## How to install this?
This library can be installed using "pip install furiganamaker".</br>
Then you need the data for unidic, so have to run "python -m unidic download".

To use the library after installing it, you need to follow one or both of the following steps...


### Using mecab-python3 (Fast but limited)
- Run "pip install mecab-python3".


### Using jamdict (Comprehensive but slow)
- Run "pip install wheel", which is required for installing the data.
- Run "pip install jamdict jamdict-data".


## Examples
- Includes a simple example [example.py](https://github.com/dkollmann/furiganamaker/blob/main/example.py).
- Includes an example to add furigana to a text file [example_textfile.py](https://github.com/dkollmann/furiganamaker/blob/main/example_textfile.py).


## API Overview
A general overview of the API.


### Instance(opentag: str, closetag: str, kakasi: pykakasi.kakasi, mecabtagger = None, jamdict = None)
Creates a new instance and sets some basic settings.

- opentag - The tag used to mark the beginning of a furigana block.
- closetag - The tag used to mark the end of a furigana block.
- kakasi - The main library used to generate the furigana readings and convert readings in general.
- mecabtagger - An optional MeCab.Tagger() which can be used to get additional readings.
- jamdict - An optional Jamdict() which can be used to get additional readings.


### Instance.add_kanjireadings(additionalreadings: dict[str, KanjiReading])
Adds custom readings for individual kanjis.

- additionalreadings - This is a dictionary where for every kanji/key in it, there is a KanjiReading object.


### Instance.add_wordreadings(customreadings: Sequence[WordReading])
Adds a reading for a words.

- customreadings - A list of readings for different words.


### Instance.process(text: str, problems: list[Problem], userdata = None)
Adds furigana to a given text. Gets a list of where to store all problems that have been found. The user data is added

- text - The text you want to add furigana to it.
- problems - Any problem found during the processing is added here.
- userdata - This data is added to any problem which was found, allowing you to trackback where the text came from, e.g. line in file.
- Returns a tuple (hasfurigana, processedtext), where hasfurigana tells you if furigana has been added and processedtext is the resulting text.


### Problems.print_all(problems: list[Problem], limit: int = 100000)
Prints all found problems on the screen.

- problems - The list of problems after calling Instance.process().
- limit - Limit the number of problems listed.


### Problems.print_kanjiproblems_list(problems: list[Problem])
Prints all problems found for each kanji with a problem. Sorted by the number of problems.

- problems - The list of problems after calling Instance.process().
- Returns the list of kanjis with problems, sorted by the number of problems.


### Problems.print_kanjiproblems(problems: list[Problem], kanji: str, limit: int = 10)
Prints all problems for a specific kanji.

- problems - The list of problems after calling Instance.process().
- kanji - The kanji to print problems for.
- limit - Limit the number of problems being printed.
