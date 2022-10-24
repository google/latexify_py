"""Test utilities."""

from __future__ import annotations

import ast
from typing import cast


def ast_equal(tree1: ast.AST, tree2: ast.AST) -> bool:
    """Checks the equality between two ASTs.

    Args:
        tree1: An AST to compare.
        tree2: Another AST.

    Returns:
        True if tree1 and tree2 represent the same AST, False otherwise.
    """
    try:
        assert type(tree1) is type(tree2)

        for k, v1 in vars(tree1).items():
            v2 = getattr(tree2, k)

            if isinstance(v1, ast.AST):
                assert ast_equal(v1, cast(ast.AST, v2))
            elif isinstance(v1, list):
                v2 = cast(list, v2)
                assert len(v1) == len(v2)
                assert all(
                    ast_equal(cast(ast.AST, c1), cast(ast.AST, c2))
                    for c1, c2 in zip(v1, v2)
                )
            else:
                assert v1 == v2

    except AssertionError:
        return False

    return True


def assert_ast_equal(tree1: ast.AST, tree2: ast.AST) -> None:
    """Asserts the equality between two ASTs.

    Args:
        tree1: An AST to compare.
        tree2: Another AST.

    Raises:
        AssertionError: tree1 and tree2 represent different ASTs.
    """
    assert ast_equal(
        tree1, tree2
    ), f"""\
AST does not match.
tree1={ast.dump(tree1, indent=4)}
tree2={ast.dump(tree2, indent=4)}
"""
