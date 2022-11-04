"""Analyzer functions for specific subtrees."""

from __future__ import annotations

import ast
import dataclasses

from latexify import ast_utils, exceptions


@dataclasses.dataclass(frozen=True, eq=False)
class RangeInfo:
    """Information of the range function."""

    # Argument subtrees. These arguments could be shallow copies of the original
    # subtree.
    start: ast.expr
    stop: ast.expr
    step: ast.expr

    # Integer representation of each argument, when it is possible.
    start_int: int | None
    stop_int: int | None
    step_int: int | None


def analyze_range(node: ast.Call) -> RangeInfo:
    """Obtains RangeInfo from a Call subtree.

    Args:
        node: Subtree to be analyzed.

    Returns:
        RangeInfo extracted from `node`.

    Raises:
        LatexifySyntaxError: Analysis failed.
    """
    if not (
        isinstance(node.func, ast.Name)
        and node.func.id == "range"
        and 1 <= len(node.args) <= 3
    ):
        raise exceptions.LatexifySyntaxError("Unsupported AST for analyze_range.")

    num_args = len(node.args)

    if num_args == 1:
        start = ast_utils.make_constant(0)
        stop = node.args[0]
        step = ast_utils.make_constant(1)
    else:
        start = node.args[0]
        stop = node.args[1]
        step = node.args[2] if num_args == 3 else ast_utils.make_constant(1)

    return RangeInfo(
        start=start,
        stop=stop,
        step=step,
        start_int=ast_utils.extract_int_or_none(start),
        stop_int=ast_utils.extract_int_or_none(stop),
        step_int=ast_utils.extract_int_or_none(step),
    )
