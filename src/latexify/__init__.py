"""Latexify root package."""

try:
    from latexify import _version

    __version__ = _version.__version__
except Exception:
    __version__ = ""

from latexify import frontend, generate_latex

Style = generate_latex.Style

get_latex = generate_latex.get_latex

algorithmic = frontend.algorithmic
expression = frontend.expression
function = frontend.function
