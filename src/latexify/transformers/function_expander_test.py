"""Tests for latexify.transformers.function_expander."""

from __future__ import annotations

import ast

from latexify import ast_utils, test_utils
from latexify.transformers.function_expander import FunctionExpander


def test_preserve_keywords() -> None:
    tree = ast.Call(
        func=ast_utils.make_name("f"),
        args=[ast_utils.make_name("x")],
        keywords=[ast.keyword(arg="y", value=ast_utils.make_constant(0))],
    )
    expected = ast.Call(
        func=ast_utils.make_name("f"),
        args=[ast_utils.make_name("x")],
        keywords=[ast.keyword(arg="y", value=ast_utils.make_constant(0))],
    )
    transformed = FunctionExpander(set()).visit(tree)
    test_utils.assert_ast_equal(transformed, expected)


def test_exp() -> None:
    tree = ast.Call(
        func=ast_utils.make_name("exp"),
        args=[ast_utils.make_name("x")],
    )
    expected = ast.BinOp(
        left=ast_utils.make_name("e"),
        op=ast.Pow(),
        right=ast_utils.make_name("x"),
    )
    transformed = FunctionExpander({"exp"}).visit(tree)
    test_utils.assert_ast_equal(transformed, expected)


def test_exp_unchanged() -> None:
    tree = ast.Call(
        func=ast_utils.make_name("exp"),
        args=[ast_utils.make_name("x")],
    )
    expected = ast.Call(
        func=ast_utils.make_name("exp"),
        args=[ast_utils.make_name("x")],
    )
    transformed = FunctionExpander(set()).visit(tree)
    test_utils.assert_ast_equal(transformed, expected)


def test_exp_with_attribute() -> None:
    tree = ast.Call(
        func=ast_utils.make_attribute(ast_utils.make_name("math"), "exp"),
        args=[ast_utils.make_name("x")],
    )
    expected = ast.BinOp(
        left=ast_utils.make_name("e"),
        op=ast.Pow(),
        right=ast_utils.make_name("x"),
    )
    transformed2 = FunctionExpander({"exp"}).visit(tree)
    test_utils.assert_ast_equal(transformed2, expected)


def test_exp_unchanged_with_attribute() -> None:
    tree = ast.Call(
        func=ast_utils.make_attribute(ast_utils.make_name("math"), "exp"),
        args=[ast_utils.make_name("x")],
    )
    expected = ast.Call(
        func=ast_utils.make_attribute(ast_utils.make_name("math"), "exp"),
        args=[ast_utils.make_name("x")],
    )
    transformed = FunctionExpander(set()).visit(tree)
    test_utils.assert_ast_equal(transformed, expected)


def test_exp_nested1() -> None:
    tree = ast.Call(
        func=ast_utils.make_name("exp"),
        args=[
            ast.Call(
                func=ast_utils.make_name("exp"),
                args=[ast_utils.make_name("x")],
            )
        ],
    )
    expected = ast.BinOp(
        left=ast_utils.make_name("e"),
        op=ast.Pow(),
        right=ast.BinOp(
            left=ast_utils.make_name("e"),
            op=ast.Pow(),
            right=ast_utils.make_name("x"),
        ),
    )
    transformed = FunctionExpander({"exp"}).visit(tree)
    test_utils.assert_ast_equal(transformed, expected)


def test_exp_nested2() -> None:
    tree = ast.Call(
        func=ast_utils.make_name("f"),
        args=[
            ast.Call(
                func=ast_utils.make_name("exp"),
                args=[ast_utils.make_name("x")],
            )
        ],
    )
    expected = ast.Call(
        func=ast_utils.make_name("f"),
        args=[
            ast.BinOp(
                left=ast_utils.make_name("e"),
                op=ast.Pow(),
                right=ast_utils.make_name("x"),
            )
        ],
    )
    transformed = FunctionExpander({"exp"}).visit(tree)
    test_utils.assert_ast_equal(transformed, expected)


def test_atan2() -> None:
    tree = ast.Call(
        func=ast_utils.make_name("atan2"),
        args=[ast_utils.make_name("y"), ast_utils.make_name("x")],
    )
    expected = ast.Call(
        func=ast_utils.make_name("atan"),
        args=[
            ast.BinOp(
                left=ast_utils.make_name("y"),
                op=ast.Div(),
                right=ast_utils.make_name("x"),
            )
        ],
    )
    transformed = FunctionExpander({"atan2"}).visit(tree)
    test_utils.assert_ast_equal(transformed, expected)


def test_exp2() -> None:
    tree = ast.Call(
        func=ast_utils.make_name("exp2"),
        args=[ast_utils.make_name("x")],
    )
    expected = ast.BinOp(
        left=ast_utils.make_constant(2),
        op=ast.Pow(),
        right=ast_utils.make_name("x"),
    )
    transformed = FunctionExpander({"exp2"}).visit(tree)
    test_utils.assert_ast_equal(transformed, expected)


def test_expm1() -> None:
    tree = ast.Call(
        func=ast_utils.make_name("expm1"),
        args=[ast_utils.make_name("x")],
    )
    expected = ast.BinOp(
        left=ast.Call(
            func=ast_utils.make_name("exp"),
            args=[ast_utils.make_name("x")],
        ),
        op=ast.Sub(),
        right=ast_utils.make_constant(1),
    )
    transformed = FunctionExpander({"expm1"}).visit(tree)
    test_utils.assert_ast_equal(transformed, expected)


def test_hypot() -> None:
    tree = ast.Call(
        func=ast_utils.make_name("hypot"),
        args=[ast_utils.make_name("x"), ast_utils.make_name("y")],
    )
    expected = ast.Call(
        func=ast_utils.make_name("sqrt"),
        args=[
            ast.BinOp(
                left=ast.BinOp(
                    left=ast_utils.make_name("x"),
                    op=ast.Pow(),
                    right=ast_utils.make_constant(2),
                ),
                op=ast.Add(),
                right=ast.BinOp(
                    left=ast_utils.make_name("y"),
                    op=ast.Pow(),
                    right=ast_utils.make_constant(2),
                ),
            )
        ],
    )
    transformed = FunctionExpander({"hypot"}).visit(tree)
    test_utils.assert_ast_equal(transformed, expected)


def test_hypot_no_args() -> None:
    tree = ast.Call(func=ast_utils.make_name("hypot"), args=[])
    expected = ast_utils.make_constant(0)
    transformed = FunctionExpander({"hypot"}).visit(tree)
    test_utils.assert_ast_equal(transformed, expected)


def test_log1p() -> None:
    tree = ast.Call(
        func=ast_utils.make_name("log1p"),
        args=[ast_utils.make_name("x")],
    )
    expected = ast.Call(
        func=ast_utils.make_name("log"),
        args=[
            ast.BinOp(
                left=ast_utils.make_constant(1),
                op=ast.Add(),
                right=ast_utils.make_name("x"),
            )
        ],
    )
    transformed = FunctionExpander({"log1p"}).visit(tree)
    test_utils.assert_ast_equal(transformed, expected)


def test_pow() -> None:
    tree = ast.Call(
        func=ast_utils.make_name("pow"),
        args=[ast_utils.make_name("x"), ast_utils.make_name("y")],
    )
    expected = ast.BinOp(
        left=ast_utils.make_name("x"),
        op=ast.Pow(),
        right=ast_utils.make_name("y"),
    )
    transformed = FunctionExpander({"pow"}).visit(tree)
    test_utils.assert_ast_equal(transformed, expected)
