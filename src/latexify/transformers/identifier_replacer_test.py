"""Tests for latexify.transformer.identifier_replacer."""

from __future__ import annotations

import ast

import pytest

from latexify import test_utils
from latexify.transformers.identifier_replacer import IdentifierReplacer


def test_invalid_mapping() -> None:
    with pytest.raises(ValueError, match=r"'123' is not an identifier name."):
        IdentifierReplacer({"123": "foo"})
    with pytest.raises(ValueError, match=r"'456' is not an identifier name."):
        IdentifierReplacer({"foo": "456"})


def test_name_replaced() -> None:
    source = ast.Name(id="foo", ctx=ast.Load())
    expected = ast.Name(id="bar", ctx=ast.Load())
    transformed = IdentifierReplacer({"foo": "bar"}).visit(source)
    test_utils.assert_ast_equal(transformed, expected)


def test_name_not_replaced() -> None:
    source = ast.Name(id="foo", ctx=ast.Load())
    expected = ast.Name(id="foo", ctx=ast.Load())
    transformed = IdentifierReplacer({"fo": "bar"}).visit(source)
    test_utils.assert_ast_equal(transformed, expected)
    transformed = IdentifierReplacer({"fooo": "bar"}).visit(source)
    test_utils.assert_ast_equal(transformed, expected)


@test_utils.require_at_most(7)
def test_functiondef() -> None:
    # Subtree of:
    #     @d
    #     def f(y=b, *, z=c):
    #         pass
    source = ast.FunctionDef(
        name="f",
        args=ast.arguments(
            args=[ast.arg(arg="y")],
            kwonlyargs=[ast.arg(arg="z")],
            kw_defaults=[ast.Name(id="c", ctx=ast.Load())],
            defaults=[
                ast.Name(id="a", ctx=ast.Load()),
                ast.Name(id="b", ctx=ast.Load()),
            ],
        ),
        body=[ast.Pass()],
        decorator_list=[ast.Name(id="d", ctx=ast.Load())],
    )

    expected = ast.FunctionDef(
        name="F",
        args=ast.arguments(
            args=[ast.arg(arg="Y")],
            kwonlyargs=[ast.arg(arg="Z")],
            kw_defaults=[ast.Name(id="C", ctx=ast.Load())],
            defaults=[
                ast.Name(id="A", ctx=ast.Load()),
                ast.Name(id="B", ctx=ast.Load()),
            ],
        ),
        body=[ast.Pass()],
        decorator_list=[ast.Name(id="D", ctx=ast.Load())],
    )

    mapping = {x: x.upper() for x in "abcdfyz"}
    transformed = IdentifierReplacer(mapping).visit(source)
    test_utils.assert_ast_equal(transformed, expected)


@test_utils.require_at_least(8)
def test_functiondef_with_posonlyargs() -> None:
    # Subtree of:
    #     @d
    #     def f(x=a, /, y=b, *, z=c):
    #         pass
    source = ast.FunctionDef(
        name="f",
        args=ast.arguments(
            posonlyargs=[ast.arg(arg="x")],
            args=[ast.arg(arg="y")],
            kwonlyargs=[ast.arg(arg="z")],
            kw_defaults=[ast.Name(id="c", ctx=ast.Load())],
            defaults=[
                ast.Name(id="a", ctx=ast.Load()),
                ast.Name(id="b", ctx=ast.Load()),
            ],
        ),
        body=[ast.Pass()],
        decorator_list=[ast.Name(id="d", ctx=ast.Load())],
    )

    expected = ast.FunctionDef(
        name="F",
        args=ast.arguments(
            posonlyargs=[ast.arg(arg="X")],
            args=[ast.arg(arg="Y")],
            kwonlyargs=[ast.arg(arg="Z")],
            kw_defaults=[ast.Name(id="C", ctx=ast.Load())],
            defaults=[
                ast.Name(id="A", ctx=ast.Load()),
                ast.Name(id="B", ctx=ast.Load()),
            ],
        ),
        body=[ast.Pass()],
        decorator_list=[ast.Name(id="D", ctx=ast.Load())],
    )

    mapping = {x: x.upper() for x in "abcdfxyz"}
    transformed = IdentifierReplacer(mapping).visit(source)
    test_utils.assert_ast_equal(transformed, expected)


def test_expr() -> None:
    # Subtree of:
    #     (x + y) * z
    source = ast.BinOp(
        left=ast.BinOp(
            left=ast.Name(id="x", ctx=ast.Load()),
            op=ast.Add(),
            right=ast.Name(id="y", ctx=ast.Load()),
        ),
        op=ast.Mult(),
        right=ast.Name(id="z", ctx=ast.Load()),
    )

    expected = ast.BinOp(
        left=ast.BinOp(
            left=ast.Name(id="X", ctx=ast.Load()),
            op=ast.Add(),
            right=ast.Name(id="Y", ctx=ast.Load()),
        ),
        op=ast.Mult(),
        right=ast.Name(id="Z", ctx=ast.Load()),
    )

    mapping = {x: x.upper() for x in "xyz"}
    transformed = IdentifierReplacer(mapping).visit(source)
    test_utils.assert_ast_equal(transformed, expected)
