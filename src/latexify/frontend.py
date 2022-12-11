"""Frontend interfaces of latexify."""

from __future__ import annotations

import enum
from collections.abc import Callable
from typing import Any, overload

from latexify import codegen
from latexify import config as cfg
from latexify import output, parser, transformers

# NOTE(odashi):
# These prefixes are trimmed by default.
# This behavior shouldn't be controlled by users in the current implementation because
# some processes expects absense of these prefixes.
_COMMON_PREFIXES = {"math", "numpy", "np"}


class Environment(enum.Enum):
    JUPYTER_NOTEBOOK = "jupyter-notebook"
    LATEX = "latex"


class Style(enum.Enum):
    ALGORITHMIC = "algorithmic"
    EXPRESSION = "expression"
    FUNCTION = "function"


def get_latex(
    fn: Callable[..., Any],
    *,
    environment: Environment = Environment.LATEX,
    style: Style = Style.FUNCTION,
    config: cfg.Config | None = None,
    **kwargs,
) -> str:
    """Obtains LaTeX description from the function's source.

    Args:
        fn: Reference to a function to analyze.
        environment: Environment to target, the default is LATEX.
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
        if environment == Environment.LATEX:
            return codegen.AlgorithmicCodegen(
                use_math_symbols=merged_config.use_math_symbols,
                use_set_symbols=merged_config.use_set_symbols,
            ).visit(tree)
        else:
            return codegen.AlgorithmicJupyterCodegen(
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
def algorithmic(alg: Callable[..., Any], **kwargs: Any) -> output.LatexifiedAlgorithm:
    ...


@overload
def algorithmic(
    **kwargs: Any,
) -> Callable[[Callable[..., Any]], output.LatexifiedAlgorithm]:
    ...


def algorithmic(
    alg: Callable[..., Any] | None = None, **kwargs: Any
) -> output.LatexifiedAlgorithm | Callable[
    [Callable[..., Any]], output.LatexifiedAlgorithm
]:
    """Attach LaTeX pretty-printing to the given algorithm.

    This function works with or without specifying the target algorithm as the
    positional argument. The following two syntaxes works similarly.
        - latexify.algorithmic(alg, **kwargs)
        - latexify.algorithmic(**kwargs)(alg)

    Args:
        alg: Callable to be wrapped.
        **kwargs: Arguments to control behavior. See also get_latex().

    Returns:
        - If `alg` is passed, returns the wrapped function.
        - Otherwise, returns the wrapper function with given settings.
    """
    if "style" not in kwargs:
        kwargs["style"] = Style.ALGORITHMIC

    if alg is not None:
        return output.LatexifiedAlgorithm(alg, **kwargs)

    def wrapper(a):
        return output.LatexifiedAlgorithm(a, **kwargs)

    return wrapper


@overload
def function(fn: Callable[..., Any], **kwargs: Any) -> output.LatexifiedFunction:
    ...


@overload
def function(
    **kwargs: Any,
) -> Callable[[Callable[..., Any]], output.LatexifiedFunction]:
    ...


def function(
    fn: Callable[..., Any] | None = None, **kwargs: Any
) -> output.LatexifiedFunction | Callable[
    [Callable[..., Any]], output.LatexifiedFunction
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
        return output.LatexifiedFunction(fn, **kwargs)

    def wrapper(f):
        return output.LatexifiedFunction(f, **kwargs)

    return wrapper


@overload
def expression(fn: Callable[..., Any], **kwargs: Any) -> output.LatexifiedFunction:
    ...


@overload
def expression(
    **kwargs: Any,
) -> Callable[[Callable[..., Any]], output.LatexifiedFunction]:
    ...


def expression(
    fn: Callable[..., Any] | None = None, **kwargs: Any
) -> output.LatexifiedFunction | Callable[
    [Callable[..., Any]], output.LatexifiedFunction
]:
    """Attach LaTeX pretty-printing to the given function.

    This function is a shortcut for `latexify.function` with the default parameter
    `use_signature=False`.
    """
    kwargs["style"] = Style.EXPRESSION
    if fn is not None:
        return function(fn, **kwargs)
    else:
        return function(**kwargs)
