"""Frontend interfaces of latexify."""

from __future__ import annotations

import enum
from collections.abc import Callable
from typing import Any, overload

from latexify import codegen
from latexify import config as cfg
from latexify import ipython_wrappers, parser
from latexify.transformers import transformer_utils


class Style(enum.Enum):
    """The style of the generated LaTeX."""

    ALGORITHMIC = "algorithmic"
    EXPRESSION = "expression"
    FUNCTION = "function"


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
    merged_config = cfg.Config.defaults().merge(config=config, **kwargs)

    # Obtains the transformed source AST.
    tree = transformer_utils.apply_transformers(
        parser.parse_function(fn), merged_config
    )

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


@overload
def algorithmic(
    fn: Callable[..., Any], **kwargs: Any
) -> ipython_wrappers.LatexifiedAlgorithm:
    ...


@overload
def algorithmic(
    **kwargs: Any,
) -> Callable[[Callable[..., Any]], ipython_wrappers.LatexifiedAlgorithm]:
    ...


def algorithmic(
    fn: Callable[..., Any] | None = None, **kwargs: Any
) -> ipython_wrappers.LatexifiedAlgorithm | Callable[
    [Callable[..., Any]], ipython_wrappers.LatexifiedAlgorithm
]:
    """Attach LaTeX pretty-printing to the given function.

    This function works with or without specifying the target function as the
    positional argument. The following two syntaxes works similarly.
        - latexify.algorithmic(alg, **kwargs)
        - latexify.algorithmic(**kwargs)(alg)

    Args:
        fn: Callable to be wrapped.
        **kwargs: Arguments to control behavior. See also get_latex().

    Returns:
        - If `fn` is passed, returns the wrapped function.
        - Otherwise, returns the wrapper function with given settings.
    """
    if fn is not None:
        return ipython_wrappers.LatexifiedAlgorithm(fn, **kwargs)

    def wrapper(a):
        return ipython_wrappers.LatexifiedAlgorithm(a, **kwargs)

    return wrapper


@overload
def function(
    fn: Callable[..., Any], **kwargs: Any
) -> ipython_wrappers.LatexifiedFunction:
    ...


@overload
def function(
    **kwargs: Any,
) -> Callable[[Callable[..., Any]], ipython_wrappers.LatexifiedFunction]:
    ...


def function(
    fn: Callable[..., Any] | None = None, **kwargs: Any
) -> ipython_wrappers.LatexifiedFunction | Callable[
    [Callable[..., Any]], ipython_wrappers.LatexifiedFunction
]:
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
        return ipython_wrappers.LatexifiedFunction(fn, **kwargs)

    def wrapper(f):
        return ipython_wrappers.LatexifiedFunction(f, **kwargs)

    return wrapper


@overload
def expression(
    fn: Callable[..., Any], **kwargs: Any
) -> ipython_wrappers.LatexifiedFunction:
    ...


@overload
def expression(
    **kwargs: Any,
) -> Callable[[Callable[..., Any]], ipython_wrappers.LatexifiedFunction]:
    ...


def expression(
    fn: Callable[..., Any] | None = None, **kwargs: Any
) -> ipython_wrappers.LatexifiedFunction | Callable[
    [Callable[..., Any]], ipython_wrappers.LatexifiedFunction
]:
    """Attach LaTeX pretty-printing to the given function.

    This function is a shortcut for `latexify.function` with the default parameter
    `use_signature=False`.
    """
    if "use_signature" not in kwargs:
        kwargs["use_signature"] = False

    if fn is not None:
        return function(fn, **kwargs)
    else:
        return function(**kwargs)
