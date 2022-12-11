"""Output of the frontend function decorators."""

from __future__ import annotations

import abc
import functools
from typing import Any, Callable

from latexify import exceptions, frontend


class LatexifiedRepr(abc.ABC):
    """Object with LaTeX representation."""

    _fn: Callable[..., Any]
    _latex: str | None
    _error: str | None

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

    def __str__(self):
        return self._latex if self._latex is not None else self._error

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
    _jupyter_latex: str | None
    _jupyter_error: str | None

    def __init__(self, fn, **kwargs):
        super().__init__(fn)
        try:
            kwargs["environment"] = frontend.Environment.LATEX
            self._latex = frontend.get_latex(fn, **kwargs)
            self._error = None
        except exceptions.LatexifyError as e:
            self._latex = None
            self._error = f"{type(e).__name__}: {str(e)}"
        try:
            kwargs["environment"] = frontend.Environment.JUPYTER_NOTEBOOK
            self._jupyter_latex = frontend.get_latex(fn, **kwargs)
            self._jupyter_error = None
        except exceptions.LatexifyError as e:
            self._jupyter_latex = None
            self._jupyter_error = f"{type(e).__name__}: {str(e)}"

    @functools.cached_property
    def _repr_html_(self):
        """IPython hook to display HTML visualization."""
        return (
            '<span style="color: red;">' + self._jupyter_error + "</span>"
            if self._jupyter_error is not None
            else None
        )

    @functools.cached_property
    def _repr_latex_(self):
        """IPython hook to display LaTeX visualization."""
        return (
            r"$$ \displaystyle " + self._jupyter_latex + " $$"
            if self._jupyter_latex is not None
            else self._jupyter_error
        )


class LatexifiedFunction(LatexifiedRepr):
    """Function with latex representation."""

    def __init__(self, fn, **kwargs):
        super().__init__(fn, **kwargs)
        try:
            self._latex = frontend.get_latex(fn, **kwargs)
            self._error = None
        except exceptions.LatexifyError as e:
            self._latex = None
            self._error = f"{type(e).__name__}: {str(e)}"

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
