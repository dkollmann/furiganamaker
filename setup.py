from distutils.core import setup

setup(
	name = 'furiganamaker',
	packages = ['furiganamaker'],
	version = '1.0.2',
	license = 'gpl-3.0',
	description = 'This library allows you to add furigana to Japanese kanji.',
	author = 'Daniel Kollmann',
	author_email = 'dankolle@mail.de',
	url = 'https://github.com/dkollmann/furiganamaker',
	download_url = 'https://github.com/dkollmann/furiganamaker/archive/refs/tags/1.0.tar.gz',
	keywords = ['furigana', 'japanese', 'kanji', 'mecab', 'pykakasi', 'kakasi', 'jamdict'],
	package_data = {'': ['example_textfile_input.txt']},
	include_package_data = True,
	install_requires = [
		'pykakasi',
	],
	classifiers = [
		'Development Status :: 4 - Beta',
		'Environment :: Console',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
		'Natural Language :: English',
		'Natural Language :: Japanese',
		'Programming Language :: Python :: 3.9',
		'Topic :: Software Development :: Localization',
		'Topic :: Text Processing :: Linguistic',
	],
)
