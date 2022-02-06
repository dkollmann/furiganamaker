from distutils.core import setup
setup(
	name = 'furiganamaker',         # How you named your package folder (MyLib)
	packages = ['furiganamaker'],   # Chose the same as "name"
	version = '1.0',      # Start with a small number and increase it with every change you make
	license = 'gpl-3.0',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
	description = 'This library allows you to add furigana to Japanese kanji.',   # Give a short description about your library
	author = 'Daniel Kollmann',                   # Type in your name
	author_email = 'dankolle@mail.de',      # Type in your E-Mail
	url = 'https://github.com/dkollmann/furiganamaker',   # Provide either the link to your github or to your website
	download_url = 'https://github.com/dkollmann/furiganamaker/archive/refs/tags/1.0.tar.gz',    # I explain this later on
	keywords = ['furigana', 'japanese', 'kanji', 'mecab', 'pykakasi', 'kakasi', 'jamdict'],   # Keywords that define your package best
	install_requires=[            # I get to this in a second
		'mecab-python3',
		'unidic',
		'pykakasi',
	],
	classifiers=[
		'Development Status :: 4 - Beta',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
		'Intended Audience :: Developers',      # Define that your audience are developers
		'Topic :: Software Development :: Build Tools',
		'License :: OSI Approved :: MIT License',   # Again, pick a license
		'Programming Language :: Python :: 3.9',
	],
)
