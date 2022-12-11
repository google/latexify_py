"""Parsing utilities."""

from __future__ import annotations

import ast
import inspect
import textwrap
from collections.abc import Callable
from typing import Any

import dill  # type: ignore[import]

from latexify import exceptions


def parse_function(fn: Callable[..., Any]) -> ast.Module:
    """Parses given function.

    Args:
        fn: Target function.

    Returns:
        AST tree representing `fn`.
    """
    try:
        source = inspect.getsource(fn)
    except Exception:
        # Maybe running on console.
        source = dill.source.getsource(fn)

    # Remove extra indentation so that ast.parse runs correctly.
    source = textwrap.dedent(source)

    tree = ast.parse(source)
    if not tree.body or not isinstance(tree.body[0], ast.FunctionDef):
        raise exceptions.LatexifySyntaxError("Not a function.")

    return tree
