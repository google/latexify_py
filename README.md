# latexify

[![Python](https://img.shields.io/pypi/pyversions/latexify-py.svg)](https://pypi.org/project/latexify-py/)
[![PyPI Latest Release](https://img.shields.io/pypi/v/latexify-py.svg)](https://pypi.org/project/latexify-py/)
[![License](https://img.shields.io/pypi/l/latexify-py.svg)](https://github.com/google/latexify_py/blob/main/LICENSE)
[![Downloads](https://pepy.tech/badge/latexify-py/month)](https://pepy.tech/project/latexify-py)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)

`latexify` is a Python package to compile a fragment of Python source code to a
corresponding $\LaTeX$ expression:

![Example of latexify usage](https://raw.githubusercontent.com/google/latexify_py/main/example.jpg)

`latexify` provides the following functionalities:

* Libraries to compile Python source code or AST to $\LaTeX$.
* IPython classes to pretty-print compiled functions.

## FAQs

1. *Which Python versions are supported?*

   Syntaxes on **Pythons 3.7 to 3.11** are officially supported, or will be supported.

2. *Which technique is used?*

   `latexify` is implemented as a rule-based system on the official `ast` package.

3. *Are "AI" techniques adopted?*

   `latexify` is based on traditional parsing techniques.
   If the "AI" meant some techniques around machine learning, the answer is no.

## Getting started

See the
[example notebook](https://github.com/google/latexify_py/blob/main/examples/latexify_examples.ipynb),
which provides several
use-cases of this library.

You can also try the above notebook on
[Google Colaboratory](https://colab.research.google.com/github/google/latexify_py/blob/main/examples/latexify_examples.ipynb).

See also the official
[documentation](https://github.com/google/latexify_py/blob/main/docs/index.md)
for more details.

## How to Contribute

To contribute to this project, please refer
[CONTRIBUTING.md](https://github.com/google/latexify_py/blob/develop/CONTRIBUTING.md).

## Disclaimer

This software is currently hosted on <https://github.com/google>, but not officially
supported by Google.

If you have any issues and/or questions about this software, please visit the
[issue tracker](https://github.com/google/latexify_py/issues)
or contact the [main maintainer](https://github.com/odashi).

## License

This software adopts the
[Apache License 2.0](https://github.com/google/latexify_py/blob/develop/LICENSE).
