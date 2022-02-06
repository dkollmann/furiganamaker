@echo off

copy /y furiganamaker/README.md README.md

python setup.py sdist

twine upload dist/*
