"""Frontend interfaces of latexify."""

from __future__ import annotations

import enum
from collections.abc import Callable
from typing import Any, overload

from latexify import codegen
from latexify import config as cfg
from latexify import exceptions, parser, transformers

# NOTE(odashi):
# These prefixes are trimmed by default.
# This behavior shouldn't be controlled by users in the current implementation because
# some processes expects absense of these prefixes.
_COMMON_PREFIXES = {"math", "numpy", "np"}


class Style(str, enum.Enum):
    EXPRESSION = "expression"
    FUNCTION = "function"
    ALGORITHMIC = "algorithmic"


def get_latex(
    fn: Callable[..., Any],
    *,
    style: Style = Style.FUNCTION,
    config: cfg.Config | None = None,
    **kwargs,
) -> str:
    """Obtains LaTeX description from the function's source.

    Args:
        fn: Reference to a function to analyze.
        style: Style of the LaTeX description, the default is FUNCTION.
        config: Use defined Config object, if it is None, it will be automatic assigned
            with default value.
        **kwargs: Dict of Config field values that could be defined individually
            by users.

    Returns:
        Generated LaTeX description.

    Raises:
        latexify.exceptions.LatexifyError: Something went wrong during conversion.
    """
    if style == Style.EXPRESSION:
        kwargs["use_signature"] = kwargs.get("use_signature", False)

    merged_config = cfg.Config.defaults().merge(config=config, **kwargs)

    # Obtains the source AST.
    tree = parser.parse_function(fn)

    # Applies AST transformations.

    prefixes = _COMMON_PREFIXES | (merged_config.prefixes or set())
    tree = transformers.PrefixTrimmer(prefixes).visit(tree)

    if merged_config.identifiers is not None:
        tree = transformers.IdentifierReplacer(merged_config.identifiers).visit(tree)
    if merged_config.reduce_assignments:
        tree = transformers.AssignmentReducer().visit(tree)
    if merged_config.expand_functions is not None:
        tree = transformers.FunctionExpander(merged_config.expand_functions).visit(tree)

    # Generates LaTeX.
    if style == Style.ALGORITHMIC:
        return codegen.AlgorithmicCodegen(
            use_math_symbols=merged_config.use_math_symbols,
            use_set_symbols=merged_config.use_set_symbols,
        ).visit(tree)
    else:
        return codegen.FunctionCodegen(
            use_math_symbols=merged_config.use_math_symbols,
            use_signature=merged_config.use_signature,
            use_set_symbols=merged_config.use_set_symbols,
        ).visit(tree)


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


@overload
def function(fn: Callable[..., Any], **kwargs: Any) -> LatexifiedFunction:
    ...


@overload
def function(**kwargs: Any) -> Callable[[Callable[..., Any]], LatexifiedFunction]:
    ...


def function(
    fn: Callable[..., Any] | None = None, **kwargs: Any
) -> LatexifiedFunction | Callable[[Callable[..., Any]], LatexifiedFunction]:
    """Attach LaTeX pretty-printing to the given function.

    This function works with or without specifying the target function as the positional
    argument. The following two syntaxes works similarly.
        - latexify.function(fn, **kwargs)
        - latexify.function(**kwargs)(fn)

    Args:
        fn: Callable to be wrapped.
        **kwargs: Arguments to control behavior. See also get_latex().

    Returns:
        - If `fn` is passed, returns the wrapped function.
        - Otherwise, returns the wrapper function with given settings.
    """
    if fn is not None:
        return LatexifiedFunction(fn, **kwargs)

    def wrapper(f):
        return LatexifiedFunction(f, **kwargs)

    return wrapper


@overload
def expression(fn: Callable[..., Any], **kwargs: Any) -> LatexifiedFunction:
    ...


@overload
def expression(**kwargs: Any) -> Callable[[Callable[..., Any]], LatexifiedFunction]:
    ...


def expression(
    fn: Callable[..., Any] | None = None, **kwargs: Any
) -> LatexifiedFunction | Callable[[Callable[..., Any]], LatexifiedFunction]:
    """Attach LaTeX pretty-printing to the given function.

    This function is a shortcut for `latexify.function` with the default parameter
    `use_signature=False`.
    """
    kwargs["style"] = Style.EXPRESSION
    if fn is not None:
        return function(fn, **kwargs)
    else:
        return function(**kwargs)
