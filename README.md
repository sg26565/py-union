[![Python package](https://github.com/sg26565/py-union/actions/workflows/python-package.yml/badge.svg)](https://github.com/sg26565/py-union/actions/workflows/python-package.yml)

# C-like bitfields and unions in pure Python

This package provides base classes that allow to build bitfields and unions known from the C language.
The code was implemented in pure Python without any external dependencies.

The code uses the typing.Union syntax introduced with Python 3.10 (i.e. def fun(param: A|B)). Therefore, it will not run on Python 3.9 or earlier.
