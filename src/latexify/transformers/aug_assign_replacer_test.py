"""Tests for latexify.transformers.aug_assign_replacer."""

import ast

from latexify import test_utils
from latexify.transformers.aug_assign_replacer import AugAssignReplacer


def test_replace() -> None:
    tree = ast.AugAssign(
        target=ast.Name(id="x", ctx=ast.Store()),
        op=ast.Add(),
        value=ast.Name(id="y", ctx=ast.Load()),
    )
    expected = ast.Assign(
        targets=[ast.Name(id="x", ctx=ast.Store())],
        value=ast.BinOp(
            left=ast.Name(id="x", ctx=ast.Load()),
            op=ast.Add(),
            right=ast.Name(id="y", ctx=ast.Load()),
        ),
    )
    transformed = AugAssignReplacer().visit(tree)
    test_utils.assert_ast_equal(transformed, expected)
