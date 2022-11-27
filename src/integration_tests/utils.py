from collections.abc import Callable
from typing import Any

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
