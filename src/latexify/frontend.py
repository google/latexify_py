"""Frontend interfaces of latexify."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from latexify import exceptions, latexify_visitor, parser
from latexify.transformers.identifier_replacer import IdentifierReplacer


def get_latex(
    fn: Callable[..., Any],
    *,
    identifiers: dict[str, str] | None = None,
    reduce_assignments: bool = False,
    use_math_symbols: bool = False,
    use_raw_function_name: bool = False,
) -> str:
    """Obtains LaTeX description from the function's source.

    Args:
        fn: Reference to a function to analyze.
        identifiers: If set, the mapping to replace identifier names in the function.
            Keys are the original names of the identifiers, and corresponding values are
            the replacements.
            Both keys and values have to represent valid Python identifiers:
            ^[A-Za-z_][A-Za-z0-9_]*$
        reduce_assignments: If True, assignment statements are used to synthesize
            the final expression.
        use_math_symbols: Whether to convert identifiers with a math symbol surface
            (e.g., "alpha") to the LaTeX symbol (e.g., "\\alpha").
        use_raw_function_name: Whether to keep underscores "_" in the function name,
            or convert it to subscript.

    Returns:
        Generatee LaTeX description.

    Raises:
        latexify.exceptions.LatexifyError: Something went wrong during conversion.
    """
    tree = parser.parse_function(fn)

    if identifiers is not None:
        tree = IdentifierReplacer(identifiers).visit(tree)

    visitor = latexify_visitor.LatexifyVisitor(
        use_math_symbols=use_math_symbols,
        use_raw_function_name=use_raw_function_name,
        reduce_assignments=reduce_assignments,
    )

    return visitor.visit(tree)


class LatexifiedFunction:
    """Function with latex representation."""

    _fn: Callable[..., Any]
    _latex: str | None
    _error: str | None

    def __init__(self, fn, **kwargs):
        self._fn = fn
        try:
            self._latex = get_latex(fn, **kwargs)
            self._error = None
        except exceptions.LatexifyError as e:
            self._latex = None
            self._error = f"{type(e).__name__}: {str(e)}"

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
