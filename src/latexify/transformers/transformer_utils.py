"""Utilites for transformers."""

from __future__ import annotations

import ast

from latexify import config as cfg
from latexify import transformers


# NOTE(odashi):
# These prefixes are trimmed by default.
# This behavior shouldn't be controlled by users in the current implementation because
# some processes expects absense of these prefixes.
_COMMON_PREFIXES = {"math", "numpy", "np"}


def apply_transformers(tree: ast.AST, config: cfg.Config) -> ast.AST:
    """Applies AST transformations.

    Args:
        tree: Tree of the function to apply transformers to.
        config: Use defined Config object.

    Returns:
        A transformed AST.
    """
    prefixes = _COMMON_PREFIXES | (config.prefixes or set())
    tree = transformers.PrefixTrimmer(prefixes).visit(tree)

    if config.identifiers is not None:
        tree = transformers.IdentifierReplacer(config.identifiers).visit(tree)
    if config.reduce_assignments:
        tree = transformers.AssignmentReducer().visit(tree)
    if config.expand_functions is not None:
        tree = transformers.FunctionExpander(config.expand_functions).visit(tree)

    return tree
