# This Makefile is for convenience as a reminder and shortcut for the most used commands

# Package folder
PACKAGE=src

# change to your sage command if needed
SAGE=sage

# On Mac OS X, setting compilers to homebrew version may be necessary
# CC=gcc-8
# CXX=g++-8

all: install test

install:
	$(SAGE) -pip install --upgrade --no-index -v .

install-user:
	$(SAGE) -pip install --upgrade --no-index -v --user .

uninstall:
	$(SAGE) -pip uninstall fgb_sage

develop:
	$(SAGE) -pip install --upgrade -e .

test:
	$(SAGE) setup.py test

coverage:
	$(SAGE) -coverage $(PACKAGE)/*

# doc:
# 	cd docs && $(SAGE) -sh -c "make html"

# doc-pdf:
# 	cd docs && $(SAGE) -sh -c "make latexpdf"

clean: clean-doc
	cd src && rm -rf *.so *.html _fgb_sage_modp.{pyx,cpp} _fgb_sage_int.cpp

clean-doc:
	# cd docs && $(SAGE) -sh -c "make clean"

.PHONY: all install install-user develop test coverage clean clean-doc doc doc-pdf
