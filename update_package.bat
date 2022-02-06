@echo off

copy /y furiganamaker/README.md README.md

del /q dist\*.tar.gz

python setup.py sdist

twine upload dist/*
