# `latexify`

`latexify` is a Python package to compile a fragment of Python source code to a
corresponding $\LaTeX$ expression.

`latexify` provides the following functionalities:

* Libraries to compile Python source code or AST to $\LaTeX$.
* IPython classes to pretty-print compiled functions.


## FAQs

1. *Which Python versions are supported?*

   Syntaxes on **Pythons 3.7 to 3.10** are officially supported, or will be supported.

2. *Which technique is used?*

   `latexify` is implemented as a rule-based system on the official `ast` package.

3. *Are "AI" techniques adopted?*

   `latexify` is based on traditional parsing techniques.
   If the "AI" meant some techniques around machine learning, the answer is no.


## Getting started

The following
[Google Colaboratory notebook](https://colab.research.google.com/drive/1MuiawKpVIZ12MWwyYuzZHmbKThdM5wNJ?usp=sharing)
provides several examples to use this package.

See also the official [documentation](docs/index.md) for more details.

## How to Contribute

To contribute to this project, please refer
[CONTRIBUTING.md](https://github.com/google/latexify_py/blob/develop/CONTRIBUTING.md).


## Disclaimer

This software is currently hosted on https://github.com/google, but not officially
supported by Google.

If you have any issues and/or questions about this software, please visit the
[issue tracker](https://github.com/google/latexify_py/issues)
or contact the [main maintainer](https://github.com/odashi).


## License 

This Repository follows
[Apache License 2.0](https://github.com/google/latexify_py/blob/develop/LICENSE).
