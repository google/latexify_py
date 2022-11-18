"""Tests for latexify.transformers.assignment_reducer."""

from __future__ import annotations

import ast

from latexify import ast_utils, parser, test_utils
from latexify.transformers.assignment_reducer import AssignmentReducer


def _make_ast(body: list[ast.stmt]) -> ast.Module:
    """Helper function to generate an AST for f(x).

    Args:
        body: The function body.

    Returns:
        Generated AST.
    """
    return ast.Module(
        body=[
            ast.FunctionDef(
                name="f",
                args=ast.arguments(
                    args=[ast.arg(arg="x")],
                    kwonlyargs=[],
                    kw_defaults=[],
                    defaults=[],
                ),
                body=body,
                decorator_list=[],
            )
        ],
    )


def test_unchanged() -> None:
    def f(x):
        return x

    expected = _make_ast(
        [
            ast.Return(value=ast.Name(id="x", ctx=ast.Load())),
        ]
    )
    transformed = AssignmentReducer().visit(parser.parse_function(f))
    test_utils.assert_ast_equal(transformed, expected)


def test_constant() -> None:
    def f(x):
        y = 0
        return y

    expected = _make_ast(
        [
            ast.Return(value=ast_utils.make_constant(0)),
        ]
    )
    transformed = AssignmentReducer().visit(parser.parse_function(f))
    test_utils.assert_ast_equal(transformed, expected)


def test_nested() -> None:
    def f(x):
        y = 2 * x
        return y

    expected = _make_ast(
        [
            ast.Return(
                value=ast.BinOp(
                    left=ast_utils.make_constant(2),
                    op=ast.Mult(),
                    right=ast.Name(id="x", ctx=ast.Load()),
                )
            )
        ]
    )
    transformed = AssignmentReducer().visit(parser.parse_function(f))
    test_utils.assert_ast_equal(transformed, expected)


def test_nested2() -> None:
    def f(x):
        y = 2 * x
        z = 3 + y
        return z

    expected = _make_ast(
        [
            ast.Return(
                value=ast.BinOp(
                    left=ast_utils.make_constant(3),
                    op=ast.Add(),
                    right=ast.BinOp(
                        left=ast_utils.make_constant(2),
                        op=ast.Mult(),
                        right=ast.Name(id="x", ctx=ast.Load()),
                    ),
                )
            )
        ]
    )
    transformed = AssignmentReducer().visit(parser.parse_function(f))
    test_utils.assert_ast_equal(transformed, expected)


def test_overwrite() -> None:
    def f(x):
        y = 2 * x
        y = 3 + x
        return y

    expected = _make_ast(
        [
            ast.Return(
                value=ast.BinOp(
                    left=ast_utils.make_constant(3),
                    op=ast.Add(),
                    right=ast.Name(id="x", ctx=ast.Load()),
                )
            )
        ]
    )
    transformed = AssignmentReducer().visit(parser.parse_function(f))
    test_utils.assert_ast_equal(transformed, expected)
