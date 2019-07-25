############
``fgb_sage``
############

************************
A Sage interface for FGb
************************

This package is a `SageMath <https://www.sagemath.org/>`_ interface to FGb_ and
can be installed as a Python package for use with Sage. It provides a simple
link between the C-interface of FGb and polynomials and ideals in Sage.

FGb is a C-library by J. C. Faugère for Gröbner basis computations, with
support for:

* Gröbner bases over ℚ and finite prime fields
* parallel computations (over finite fields)
* elimination/block orders (degree-reverse-lexicographic, only)

Examples
========

See the examples and documentation in
`fgb_sage/fgb_sage.py <fgb_sage/fgb_sage.py>`_.

Installation
============

**Requirements**: Linux with a recent version of Sage
(tested with CentOS 7.5.1804, Sage 8.1, 8.4, 8.8).

First, clone the `repository from GitHub
<https://github.com/mwageringel/fgb_sage>`_ and then compile and run the
tests::

    git clone https://github.com/mwageringel/fgb_sage.git && cd fgb_sage
    sage setup.py test

After the tests passed successfully, run the following command to install the
package for use with Sage::

    sage -pip install --upgrade --no-index -v .

Alternatively, to install into the Python user install directory (no root
access required), run::

    sage -pip install --upgrade --no-index -v --user .

Issues
------

* Support for macOS was dropped for the time being due to difficulties in
  compiling this package with ``-fopenmp`` since Sage version 8.8. Compiling
  the entirety of Sage with GCC support might make this work, but this was not
  tested.

.. _FGb: https://www-polsys.lip6.fr/~jcf/FGb/index.html
