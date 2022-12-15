"""Utilities for integration tests."""

from __future__ import annotations

from typing import Any, Callable

from latexify import frontend


def check_function(
    fn: Callable[..., Any],
    latex: str,
    **kwargs,
) -> None:
    """Helper to check if the obtained function has the expected LaTeX form.

    Args:
        fn: Function to check.
        latex: LaTeX form of `fn`.
        **kwargs: Arguments passed to `frontend.function`.
    """
    # Checks the syntax:
    #     @function
    #     def fn(...):
    #         ...
    if not kwargs:
        latexified = frontend.function(fn)
        assert str(latexified) == latex
        assert latexified._repr_latex_() == rf"$$ \displaystyle {latex} $$"

    # Checks the syntax:
    #     @function(**kwargs)
    #     def fn(...):
    #         ...
    latexified = frontend.function(**kwargs)(fn)
    assert str(latexified) == latex
    assert latexified._repr_latex_() == rf"$$ \displaystyle {latex} $$"

    # Checks the syntax:
    #     def fn(...):
    #         ...
    #     latexified = function(fn, **kwargs)
    latexified = frontend.function(fn, **kwargs)
    assert str(latexified) == latex
    assert latexified._repr_latex_() == rf"$$ \displaystyle {latex} $$"


def check_algorithm(
    fn: Callable[..., Any],
    latex: str,
    ipython_latex: str,
    **kwargs,
) -> None:
    """Helper to check if the obtained function has the expected LaTeX form.

    Args:
        fn: Function to check.
        latex: LaTeX form of `fn`.
        ipython_latex: IPython LaTeX form of `fn`
        **kwargs: Arguments passed to `frontend.get_latex`.
    """
    # Checks the syntax:
    #     @algorithmic
    #     def fn(...):
    #         ...
    if not kwargs:
        latexified = frontend.algorithmic(fn)
        assert str(latexified) == latex
        assert latexified._repr_latex_() == f"$ {ipython_latex} $"

    # Checks the syntax:
    #     @algorithmic(**kwargs)
    #     def fn(...):
    #         ...
    latexified = frontend.algorithmic(**kwargs)(fn)
    assert str(latexified) == latex
    assert latexified._repr_latex_() == f"$ {ipython_latex} $"

    # Checks the syntax:
    #     def fn(...):
    #         ...
    #     latexified = algorithmic(fn, **kwargs)
    latexified = frontend.algorithmic(fn, **kwargs)
    assert str(latexified) == latex
    assert latexified._repr_latex_() == f"$ {ipython_latex} $"
