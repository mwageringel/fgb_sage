# This Makefile is for convenience as a reminder and shortcut for the most used commands

# Package folder
PACKAGE=fgb_sage

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

doc:
	cd docs && $(SAGE) -sh -c "make html"

# doc-pdf:
# 	cd docs && $(SAGE) -sh -c "make latexpdf"

clean: doc-clean
	cd $(PACKAGE) && rm -f *.so *.html *.pyc _fgb_sage_modp.{pyx,cpp} _fgb_sage_int.cpp

doc-clean:
	cd docs && rm -rf _build/

.PHONY: all install install-user develop test coverage clean doc-clean doc doc-pdf
