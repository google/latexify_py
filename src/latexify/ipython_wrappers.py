"""Wrapper objects for IPython to display output."""

from __future__ import annotations

import abc
from typing import Any, Callable, cast

from latexify import exceptions, generate_latex


class LatexifiedRepr(metaclass=abc.ABCMeta):
    """Object with LaTeX representation."""

    _fn: Callable[..., Any]

    def __init__(self, fn: Callable[..., Any], **kwargs) -> None:
        self._fn = fn

    @property
    def __doc__(self) -> str | None:
        return self._fn.__doc__

    @__doc__.setter
    def __doc__(self, val: str | None) -> None:
        self._fn.__doc__ = val

    @property
    def __name__(self) -> str:
        return self._fn.__name__

    @__name__.setter
    def __name__(self, val: str) -> None:
        self._fn.__name__ = val

    # After Python 3.7
    # @final
    def __call__(self, *args) -> Any:
        return self._fn(*args)

    @abc.abstractmethod
    def __str__(self) -> str: ...

    @abc.abstractmethod
    def _repr_html_(self) -> str | tuple[str, dict[str, Any]] | None:
        """IPython hook to display HTML visualization."""
        ...

    @abc.abstractmethod
    def _repr_latex_(self) -> str | tuple[str, dict[str, Any]] | None:
        """IPython hook to display LaTeX visualization."""
        ...


class LatexifiedAlgorithm(LatexifiedRepr):
    """Algorithm with latex representation."""

    _latex: str | None
    _error: str | None
    _ipython_latex: str | None
    _ipython_error: str | None

    def __init__(self, fn: Callable[..., Any], **kwargs) -> None:
        super().__init__(fn)

        try:
            self._latex = generate_latex.get_latex(
                fn, style=generate_latex.Style.ALGORITHMIC, **kwargs
            )
            self._error = None
        except exceptions.LatexifyError as e:
            self._latex = None
            self._error = f"{type(e).__name__}: {str(e)}"

        try:
            self._ipython_latex = generate_latex.get_latex(
                fn, style=generate_latex.Style.IPYTHON_ALGORITHMIC, **kwargs
            )
            self._ipython_error = None
        except exceptions.LatexifyError as e:
            self._ipython_latex = None
            self._ipython_error = f"{type(e).__name__}: {str(e)}"

    def __str__(self) -> str:
        return self._latex if self._latex is not None else cast(str, self._error)

    def _repr_html_(self) -> str | tuple[str, dict[str, Any]] | None:
        """IPython hook to display HTML visualization."""
        return (
            '<span style="color: red;">' + self._ipython_error + "</span>"
            if self._ipython_error is not None
            else None
        )

    def _repr_latex_(self) -> str | tuple[str, dict[str, Any]] | None:
        """IPython hook to display LaTeX visualization."""
        return (
            f"$ {self._ipython_latex} $"
            if self._ipython_latex is not None
            else self._ipython_error
        )


class LatexifiedFunction(LatexifiedRepr):
    """Function with latex representation."""

    _latex: str | None
    _error: str | None

    def __init__(self, fn: Callable[..., Any], **kwargs) -> None:
        super().__init__(fn, **kwargs)

        try:
            self._latex = self._latex = generate_latex.get_latex(
                fn, style=generate_latex.Style.FUNCTION, **kwargs
            )
            self._error = None
        except exceptions.LatexifyError as e:
            self._latex = None
            self._error = f"{type(e).__name__}: {str(e)}"

    def __str__(self) -> str:
        return self._latex if self._latex is not None else cast(str, self._error)

    def _repr_html_(self) -> str | tuple[str, dict[str, Any]] | None:
        """IPython hook to display HTML visualization."""
        return (
            '<span style="color: red;">' + self._error + "</span>"
            if self._error is not None
            else None
        )

    def _repr_latex_(self) -> str | tuple[str, dict[str, Any]] | None:
        """IPython hook to display LaTeX visualization."""
        return (
            rf"$$ \displaystyle {self._latex} $$"
            if self._latex is not None
            else self._error
        )
