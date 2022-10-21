"""Frontend interfaces of latexify."""

from __future__ import annotations

import ast
from collections.abc import Callable
import inspect
import textwrap
from typing import Any

import dill

from latexify import latexify_visitor


def get_latex(
    fn: Callable[..., Any],
    *,
    use_math_symbols: bool = False,
    use_raw_function_name: bool = False,
    reduce_assignments: bool = False,
) -> str:
    """Obtains LaTeX description from the function's source.

    Args:
        fn: Reference to a function to analyze.
        use_math_symbols: Whether to convert identifiers with a math symbol surface
            (e.g., "alpha") to the LaTeX symbol (e.g., "\\alpha").
        use_raw_function_name: Whether to keep underscores "_" in the function name,
            or convert it to subscript.
        reduce_assignments: If True, assignment statements are used to synthesize
            the final expression.

    Returns:
        Generatee LaTeX description.
    """
    try:
        source = inspect.getsource(fn)
    except Exception:
        # Maybe running on console.
        source = dill.source.getsource(fn)

    # Remove extra indentation so that ast.parse runs correctly.
    source = textwrap.dedent(source)

    tree = ast.parse(source)

    visitor = latexify_visitor.LatexifyVisitor(
        use_math_symbols=use_math_symbols,
        use_raw_function_name=use_raw_function_name,
        reduce_assignments=reduce_assignments,
    )

    return visitor.visit(tree)


class LatexifiedFunction:
    """Function with latex representation."""

    def __init__(self, fn, **kwargs):
        self._fn = fn
        self._str = get_latex(fn, **kwargs)

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
        return self._str

    def _repr_latex_(self):
        """IPython hook to display LaTeX visualization."""
        return r"$$ \displaystyle " + self._str + " $$"


def with_latex(*args, **kwargs) -> Callable[[Callable[..., Any]], LatexifiedFunction]:
    """Translate a function with latex representation.

    This function works with or without specifying the target function as the positional
    argument. The following two syntaxes works similarly.
        - with_latex(fn, **kwargs)
        - with_latex(**kwargs)(fn)

    Args:
        *args: No argument, or a callable.
        **kwargs: Arguments to control behavior. See also get_latex().

    Returns:
        - If the target function is passed directly, returns the wrapped function.
        - Otherwise, returns the wrapper function with given settings.
    """
    if len(args) == 1 and isinstance(args[0], Callable):
        return LatexifiedFunction(args[0], **kwargs)

    def wrapper(fn):
        return LatexifiedFunction(fn, **kwargs)

    return wrapper
