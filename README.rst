############
``fgb_sage``
############

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
(tested with Sage 9.5.rc0 on Ubuntu 20.04 as well as with Sage 9.6 from Arch Linux).

First, clone the `repository from GitHub <fgb_sage_gh_>`_ and then compile and
run the tests::

    git clone https://github.com/mwageringel/fgb_sage.git && cd fgb_sage
    sage setup.py test

After the tests passed successfully, run the following command to install the
package for use with Sage::

    sage -python -m pip install --upgrade --no-index -v .

Alternatively, to install into the Python user install directory (no root
access required), run::

    sage -python -m pip install --upgrade --no-index -v --user .

Installing into a virtual environment, assuming Sage is installed system-wide::

    python -m venv --system-site-packages ./sage-venv  # assumes that sage and python-setuptools are available system-wide
    source ./sage-venv/bin/activate                    # redefines `python` and `pip` using virtual environment
    python -m pip install --upgrade --no-index -v .
    cd sage-venv && python -m IPython                  # changing directory is important

        In [1]: from sage.all import *
        In [2]: R = PolynomialRing(QQ, 5, 'x', order="degrevlex(2),degrevlex(3)")
        In [3]: I = sage.rings.ideal.Cyclic(R)
        In [4]: import fgb_sage
        In [5]: gb = fgb_sage.groebner_basis(I)

Packaged versions of Sage
-------------------------

If Sage was installed by the package manager of your Linux distribution, you
may need to install a few more dependencies in order to compile this package.
For example, on

- **Arch Linux**::

     pacman -S --asdeps cython python-pkgconfig

- **Ubuntu**::

     libgsl-dev liblinbox-dev libsingular4-dev libntl-dev libflint-dev libmpfr-dev libpari-dev python3-ipywidgets

Alternatively, you can download a
`Sage binary <https://www.sagemath.org/download.html>`_,
use `Sage via Docker <https://hub.docker.com/r/sagemath/sagemath>`_ or
install Sage from source.
See also `issue #2 <https://github.com/mwageringel/fgb_sage/issues/2>`_.

Issues
------

* macOS: Support for macOS has been dropped for the time being due to difficulties in
  compiling this package with ``-fopenmp`` since Sage version 8.8. Compiling
  the entirety of Sage with GCC support might make this work, but this was not
  tested. See `issue #3 <https://github.com/mwageringel/fgb_sage/issues/3>`_.

* Memory leaks: The underlying FGb program leaks memory, which can be a problem
  when computing many Gröbner bases in a single long-lived process. In this
  case, it might be better to split the computation into several processes or
  use a different Gröbner basis algorithm `available in Sage <sage_docs_gb_>`_.

.. _SAGE: https://www.sagemath.org/
.. _FGb: https://www-polsys.lip6.fr/~jcf/FGb/index.html
.. _fgb_sage_gh: https://github.com/mwageringel/fgb_sage
.. _fgb_sage_rdt: https://fgb-sage.readthedocs.io/en/latest/#module-fgb_sage
.. _sage_docs_gb: https://doc.sagemath.org/html/en/reference/polynomial_rings/sage/rings/polynomial/multi_polynomial_ideal.html#sage.rings.polynomial.multi_polynomial_ideal.MPolynomialIdeal.groebner_basis
