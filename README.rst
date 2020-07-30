############
``fgb_sage``
############

.. image:: https://travis-ci.com/mwageringel/fgb_sage.svg?branch=master
   :target: https://travis-ci.com/mwageringel/fgb_sage
   :alt: Build Status
.. image:: https://readthedocs.org/projects/fgb-sage/badge/?version=latest
   :target: https://fgb-sage.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

************************
A Sage interface for FGb
************************

This package is a `SageMath <SAGE_>`_ interface to FGb_ and
can be installed as a Python package for use with Sage. It provides a simple
link between the C-interface of FGb and polynomials and ideals in Sage.

FGb is a C-library by J. C. Faugère for Gröbner basis computations, with
support for:

* Gröbner bases over ℚ and finite prime fields
* parallel computations (over finite fields)
* elimination/block orders (degree-reverse-lexicographic, only)

Examples
========

See the examples and documentation at
`https://fgb-sage.readthedocs.io <fgb_sage_rdt_>`_.

Installation
============

**Requirements**: Linux with a recent version of `Sage <SAGE_>`_
(tested with CentOS 7.5.1804, Sage 8.1, 8.4, 8.8, and on Travis-CI with
Ubuntu 18.04).

First, clone the `repository from GitHub <fgb_sage_gh_>`_ and then compile and
run the tests::

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

* macOS: Support for macOS has been dropped for the time being due to difficulties in
  compiling this package with ``-fopenmp`` since Sage version 8.8. Compiling
  the entirety of Sage with GCC support might make this work, but this was not
  tested. See `issue #3 <https://github.com/mwageringel/fgb_sage/issues/3>`_.

* Packaged versions of Sage: Installing this package can fail if Sage was
  installed via a package manager of a Linux distribution; see `issue #2
  <https://github.com/mwageringel/fgb_sage/issues/3>`_.  As a workaround,
  download a `Sage binary <https://www.sagemath.org/download.html>`_,
  use `Sage via Docker <https://hub.docker.com/r/sagemath/sagemath>`_ or
  install Sage from source.

* Memory leaks: The underlying FGb program leaks memory, which can be a problem
  when computing many Gröbner bases in a single long-lived process. In this
  case, it might be better to split the computation into several processes or
  use a different Gröbner basis algorithm `available in Sage <sage_docs_gb_>`_.

.. _SAGE: https://www.sagemath.org/
.. _FGb: https://www-polsys.lip6.fr/~jcf/FGb/index.html
.. _fgb_sage_gh: https://github.com/mwageringel/fgb_sage
.. _fgb_sage_rdt: https://fgb-sage.readthedocs.io/en/latest/#module-fgb_sage
.. _sage_docs_gb: https://doc.sagemath.org/html/en/reference/polynomial_rings/sage/rings/polynomial/multi_polynomial_ideal.html#sage.rings.polynomial.multi_polynomial_ideal.MPolynomialIdeal.groebner_basis
