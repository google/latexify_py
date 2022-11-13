"""Latexify root package."""

try:
    from latexify import _version

    __version__ = _version.__version__
except:
    __version__ = ""

from latexify import frontend

get_latex = frontend.get_latex

function = frontend.function
expression = frontend.expression

# Deprecated
with_latex = frontend.with_latex
