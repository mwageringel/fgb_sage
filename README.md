# fgb_sage

This is a [SageMath](https://www.sagemath.org/) interface to
[FGb](https://www-polsys.lip6.fr/~jcf/FGb/index.html).
*FGb* is a C-library by J. C. Faugère for Gröbner basis computations, with
support for:

* Gröbner bases over ℚ and finite fields
* parallel computations (over finite fields)
* elimination/block orders (degree-reverse-lexicographic, only)

This Python package *fgb_sage* is implemented in Cython and provides a simple
interface between the C-interface to *FGb* and polynomials and ideals in
*Sage*.

## Examples

See the examples in [src/fgb_sage.py](src/fgb_sage.py).

## Installation

Requirements: Linux with a recent version of Sage.
(Tested with CentOS 7.5.1804, Sage 8.1, 8.4, 8.8)

First, in this directory, compile and run the tests with
```
sage setup.py test
```

After the tests passed successfully, run
```
sage -pip install --upgrade --no-index -v .
```

Alternatively, to install into the Python user install directory (no root
access required), run
```
sage -pip install --upgrade --no-index -v --user .
```

## Issues

* Support for macOS was dropped due to difficulties in compiling this package
  with `-fopenmp` since Sage version 8.8. Compiling the entirety of Sage with
  GCC support might make this work, but this was not tested.

## License

MIT for this package *fgb_sage*. However, note that *FGb* is licensed for
academic use only.

## Author

Markus Wageringel.
