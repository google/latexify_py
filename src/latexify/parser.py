"""Parsing utilities."""

from __future__ import annotations

from collections.abc import Callable
import ast
import inspect
import textwrap
from typing import Any

import dill

from latexify import exceptions


def parse_function(fn: Callable[..., Any]) -> ast.FunctionDef:
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
