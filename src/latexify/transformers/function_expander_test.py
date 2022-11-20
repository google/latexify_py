"""Tests for latexify.transformers.function_expander."""

from __future__ import annotations

import ast
import math

from latexify import ast_utils, parser, test_utils
from latexify.transformers.function_expander import FunctionExpander


def _make_ast(args: list[str], body: ast.AST) -> ast.Module:
    """Helper function to generate an AST for f(x).

    Args:
        args: The arguments passed to the method.
        body: The body of the return statement.

    Returns:
        Generated AST.
    """
    return ast.Module(
        body=[
            ast.FunctionDef(
                name="f",
                args=ast.arguments(
                    args=list(map(lambda arg: ast.arg(arg=arg), args)),
                    kwonlyargs=[],
                    kw_defaults=[],
                    defaults=[],
                ),
                body=[ast.Return(body)],
                decorator_list=[],
            )
        ],
    )


def test_hypot_unchanged_without_attribute_access() -> None:
    from math import hypot

    def f(x, y):
        return hypot(x, y)

    expected = _make_ast(
        ["x", "y"], ast.Call(ast.Name("hypot"), [ast.Name("x"), ast.Name("y")])
    )
    transformed = FunctionExpander(set()).visit(parser.parse_function(f))
    test_utils.assert_ast_equal(transformed, expected)


def test_hypot_unchanged() -> None:
    def f(x, y):
        return math.hypot(x, y)

    expected = _make_ast(
        ["x", "y"],
        ast.Call(
            ast.Attribute(ast.Name("math"), "hypot", ast.Load()),
            [ast.Name("x"), ast.Name("y")],
        ),
    )
    transformed = FunctionExpander(set()).visit(parser.parse_function(f))
    test_utils.assert_ast_equal(transformed, expected)


def test_hypot_expanded() -> None:
    def f(x, y):
        return math.hypot(x, y)

    expected = _make_ast(
        ["x", "y"],
        ast.Call(
            ast.Name("sqrt"),
            [
                ast.BinOp(
                    ast.BinOp(ast.Name("x"), ast.Pow(), ast_utils.make_constant(2)),
                    ast.Add(),
                    ast.BinOp(ast.Name("y"), ast.Pow(), ast_utils.make_constant(2)),
                )
            ],
        ),
    )
    transformed = FunctionExpander({"hypot"}).visit(parser.parse_function(f))
    test_utils.assert_ast_equal(transformed, expected)


def test_hypot_expanded_no_args() -> None:
    def f():
        return math.hypot()

    expected = _make_ast(
        [],
        ast_utils.make_constant(0),
    )
    transformed = FunctionExpander({"hypot"}).visit(parser.parse_function(f))
    test_utils.assert_ast_equal(transformed, expected)
