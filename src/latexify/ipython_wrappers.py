"""Wrapper objects for IPython to display output."""

from __future__ import annotations

import abc
from typing import Any, Callable

from latexify import codegen
from latexify import config as cfg
from latexify import exceptions, parser
from latexify.transformers import transformer_utils


class LatexifiedRepr(metaclass=abc.ABCMeta):
    """Object with LaTeX representation."""

    _fn: Callable[..., Any]

    def __init__(self, fn, **kwargs):
        self._fn = fn

    @property
    def __doc__(self):
        return self._fn.__doc__

    @__doc__.setter
    def __doc__(self, val):
        self._fn.__doc__ = val

    @property
    def __name__(self):
        return self._fn.__name__

    @__name__.setter
    def __name__(self, val):
        self._fn.__name__ = val

    def __call__(self, *args):
        return self._fn(*args)

    @abc.abstractmethod
    def _repr_html_(self):
        """IPython hook to display HTML visualization."""
        ...

    @abc.abstractmethod
    def _repr_latex_(self):
        """IPython hook to display LaTeX visualization."""
        ...


class LatexifiedAlgorithm(LatexifiedRepr):
    """Algorithm with latex representation."""

    _latex: str | None
    _error: str | None
    _ipython_latex: str | None
    _ipython_error: str | None

    def __init__(self, fn, **kwargs):
        super().__init__(fn)
        merged_config = cfg.Config.defaults().merge(**kwargs)

        # Obtains the transformed source AST.
        tree = transformer_utils.apply_transformers(
            parser.parse_function(fn), merged_config
        )

        # Generates LaTeX.
        try:
            self._latex = codegen.AlgorithmicCodegen(
                use_math_symbols=merged_config.use_math_symbols,
                use_set_symbols=merged_config.use_set_symbols,
            ).visit(tree)
            self._error = None
        except exceptions.LatexifyError as e:
            self._latex = None
            self._error = f"{type(e).__name__}: {str(e)}"

        try:
            # TODO(ZibingZhang): implement algorithmic codegen for IPython
            self._ipython_latex = None
            self._ipython_error = None
        except exceptions.LatexifyError as e:
            self._ipython_latex = None
            self._ipython_error = f"{type(e).__name__}: {str(e)}"

    def __str__(self):
        return self._latex if self._latex is not None else self._error

    def _repr_html_(self):
        """IPython hook to display HTML visualization."""
        return (
            '<span style="color: red;">' + self._ipython_error + "</span>"
            if self._ipython_error is not None
            else None
        )

    def _repr_latex_(self):
        """IPython hook to display LaTeX visualization."""
        return (
            r"$ " + self._ipython_latex + " $"
            if self._ipython_latex is not None
            else self._ipython_error
        )


class LatexifiedFunction(LatexifiedRepr):
    """Function with latex representation."""

    _latex: str | None
    _error: str | None

    def __init__(self, fn, **kwargs):
        super().__init__(fn, **kwargs)

        merged_config = cfg.Config.defaults().merge(**kwargs)

        # Obtains the transformed source AST.
        tree = transformer_utils.apply_transformers(
            parser.parse_function(fn), merged_config
        )

        # Generates LaTeX.
        try:
            self._latex = codegen.FunctionCodegen(
                use_math_symbols=merged_config.use_math_symbols,
                use_signature=merged_config.use_signature,
                use_set_symbols=merged_config.use_set_symbols,
            ).visit(tree)
            self._error = None
        except exceptions.LatexifyError as e:
            self._latex = None
            self._error = f"{type(e).__name__}: {str(e)}"

    def __str__(self):
        return self._latex if self._latex is not None else self._error

    def _repr_html_(self):
        """IPython hook to display HTML visualization."""
        return (
            '<span style="color: red;">' + self._error + "</span>"
            if self._error is not None
            else None
        )

    def _repr_latex_(self):
        """IPython hook to display LaTeX visualization."""
        return (
            r"$$ \displaystyle " + self._latex + " $$"
            if self._latex is not None
            else self._error
        )
