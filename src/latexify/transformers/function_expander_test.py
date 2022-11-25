"""Tests for latexify.transformers.function_expander."""

from __future__ import annotations

import ast
import math

from latexify import ast_utils, constants, parser, test_utils
from latexify.transformers.function_expander import FunctionExpander


def _make_ast(args: list[str], body: ast.expr) -> ast.Module:
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
                    args=[ast.arg(arg=arg) for arg in args],
                    kwonlyargs=[],
                    kw_defaults=[],
                    defaults=[],
                ),
                body=[ast.Return(body)],
                decorator_list=[],
            )
        ],
    )


def test_atan2_expanded() -> None:
    def f(x, y):
        return math.atan2(y, x)

    expected = _make_ast(
        ["x", "y"],
        ast.Call(
            func=ast.Name(id="atan", ctx=ast.Load()),
            args=[
                ast.BinOp(
                    left=ast.Name(id="y", ctx=ast.Load()),
                    op=ast.Div(),
                    right=ast.Name(id="x", ctx=ast.Load()),
                )
            ],
        ),
    )
    transformed = FunctionExpander({"atan2"}).visit(parser.parse_function(f))
    test_utils.assert_ast_equal(transformed, expected)


def test_exp_expanded() -> None:
    def f(x):
        return math.exp(x)

    expected = _make_ast(
        ["x"],
        ast.BinOp(
            left=ast.Name(id="e", ctx=ast.Load()),
            op=ast.Pow(),
            right=ast.Name(id="x", ctx=ast.Load()),
        ),
    )
    transformed = FunctionExpander({"exp"}).visit(parser.parse_function(f))
    test_utils.assert_ast_equal(transformed, expected)


def test_exp2_expanded() -> None:
    def f(x):
        return math.exp2(x)

    expected = _make_ast(
        ["x"],
        ast.BinOp(
            left=ast_utils.make_constant(2),
            op=ast.Pow(),
            right=ast.Name(id="x", ctx=ast.Load()),
        ),
    )
    transformed = FunctionExpander({"exp2"}).visit(parser.parse_function(f))
    test_utils.assert_ast_equal(transformed, expected)


def test_expm1_expanded() -> None:
    def f(x):
        return math.expm1(x)

    expected = _make_ast(
        ["x"],
        ast.BinOp(
            left=ast.Call(
                func=ast.Name(id=constants.BuiltinFnName.EXP.value, ctx=ast.Load()),
                args=[ast.Name(id="x", ctx=ast.Load())],
            ),
            op=ast.Sub(),
            right=ast_utils.make_constant(1),
        ),
    )
    transformed = FunctionExpander({"expm1"}).visit(parser.parse_function(f))
    test_utils.assert_ast_equal(transformed, expected)


def test_hypot_unchanged_without_attribute_access() -> None:
    from math import hypot

    def f(x, y):
        return hypot(x, y)

    expected = _make_ast(
        ["x", "y"],
        ast.Call(
            func=ast.Name(id="hypot"),
            args=[ast.Name(id="x", ctx=ast.Load()), ast.Name(id="y", ctx=ast.Load())],
        ),
    )
    transformed = FunctionExpander(set()).visit(parser.parse_function(f))
    test_utils.assert_ast_equal(transformed, expected)


def test_hypot_unchanged() -> None:
    def f(x, y):
        return math.hypot(x, y)

    expected = _make_ast(
        ["x", "y"],
        ast.Call(
            func=ast.Attribute(
                ast.Name(id="math", ctx=ast.Load()), attr="hypot", ctx=ast.Load()
            ),
            args=[ast.Name(id="x", ctx=ast.Load()), ast.Name(id="y", ctx=ast.Load())],
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
            func=ast.Name(id="sqrt", ctx=ast.Load()),
            args=[
                ast.BinOp(
                    left=ast.BinOp(
                        left=ast.Name(id="x", ctx=ast.Load()),
                        op=ast.Pow(),
                        right=ast_utils.make_constant(2),
                    ),
                    op=ast.Add(),
                    right=ast.BinOp(
                        left=ast.Name(id="y", ctx=ast.Load()),
                        op=ast.Pow(),
                        right=ast_utils.make_constant(2),
                    ),
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


def test_log1p_expanded() -> None:
    def f(x):
        return math.log1p(x)

    expected = _make_ast(
        ["x"],
        ast.Call(
            func=ast.Name(id=constants.BuiltinFnName.LOG.value, ctx=ast.Load()),
            args=[
                ast.BinOp(
                    left=ast_utils.make_constant(1),
                    op=ast.Add(),
                    right=ast.Name(id="x", ctx=ast.Load()),
                )
            ],
        ),
    )
    transformed = FunctionExpander({"log1p"}).visit(parser.parse_function(f))
    test_utils.assert_ast_equal(transformed, expected)
