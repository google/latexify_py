"""Generate LaTeX code."""

from __future__ import annotations

import enum
from collections.abc import Callable
from typing import Any

from latexify import codegen
from latexify import config as cfg
from latexify import parser, transformers

# NOTE(odashi):
# These prefixes are trimmed by default.
# This behavior shouldn't be controlled by users in the current implementation because
# some processes expects absense of these prefixes.
_COMMON_PREFIXES = {"math", "numpy", "np"}


class Style(enum.Enum):
    """The style of the generated LaTeX."""

    ALGORITHMIC = "algorithmic"
    EXPRESSION = "expression"
    FUNCTION = "function"
    IPYTHON_ALGORITHMIC = "ipython-algorithmic"


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

    # Obtains the source AST.
    tree = parser.parse_function(fn)

    # Applies AST transformations.
    if merged_config.prefixes is not None:
        tree = transformers.PrefixTrimmer(merged_config.prefixes).visit(tree)
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
    elif style == Style.IPYTHON_ALGORITHMIC:
        # TODO(ZibingZhang): implement algorithmic codegen for ipython
        raise NotImplementedError
    else:
        if style == Style.EXPRESSION:
            kwargs["use_signature"] = kwargs.get("use_signature", False)
        return codegen.FunctionCodegen(
            use_math_symbols=merged_config.use_math_symbols,
            use_signature=merged_config.use_signature,
            use_set_symbols=merged_config.use_set_symbols,
        ).visit(tree)
