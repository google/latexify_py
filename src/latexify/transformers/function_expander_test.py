"""Tests for latexify.transformers.function_expander."""

from __future__ import annotations

import ast

from latexify import parser, test_utils
from latexify.test_stubs import hypot
from latexify.transformers.function_expander import FunctionExpander


def _make_ast(args: list[str], call: ast.Call) -> ast.Module:
    """Helper function to generate an AST for f(x).

    Args:
        name: The name of calling method.
        args: The arguments passed to the method.

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
                body=[ast.Return(call)],
                decorator_list=[],
            )
        ],
    )


def test_unchanged() -> None:
    def f(x, y):
        return hypot(x, y)

    expected = _make_ast(
        ["x", "y"], ast.Call(ast.Name("hypot"), [ast.Name("x"), ast.Name("y")])
    )
    transformed = FunctionExpander([]).visit(parser.parse_function(f))
    test_utils.assert_ast_equal(transformed, expected)


def test_expand_hypot() -> None:
    def f(x, y):
        return hypot(x, y)

    expected = _make_ast(
        ["x", "y"],
        ast.Call(
            ast.Name("sqrt"),
            [
                ast.BinOp(
                    ast.BinOp(ast.Name("x"), ast.Pow(), ast.Num(2)),
                    ast.Add(),
                    ast.BinOp(ast.Name("y"), ast.Pow(), ast.Num(2)),
                )
            ],
        ),
    )
    transformed = FunctionExpander(["hypot"]).visit(parser.parse_function(f))
    test_utils.assert_ast_equal(transformed, expected)
