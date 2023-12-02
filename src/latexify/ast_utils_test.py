"""Tests for latexify.ast_utils."""

from __future__ import annotations

import ast
from typing import Any

import pytest

from latexify import ast_utils, test_utils


def test_parse_expr() -> None:
    test_utils.assert_ast_equal(
        ast_utils.parse_expr("a + b"),
        ast.BinOp(
            left=ast_utils.make_name("a"),
            op=ast.Add(),
            right=ast_utils.make_name("b"),
        ),
    )


def test_make_name() -> None:
    test_utils.assert_ast_equal(
        ast_utils.make_name("foo"), ast.Name(id="foo", ctx=ast.Load())
    )


def test_make_attribute() -> None:
    test_utils.assert_ast_equal(
        ast_utils.make_attribute(ast_utils.make_name("foo"), "bar"),
        ast.Attribute(ast.Name(id="foo", ctx=ast.Load()), attr="bar", ctx=ast.Load()),
    )


@test_utils.require_at_most(7)
@pytest.mark.parametrize(
    "value,expected",
    [
        (None, ast.NameConstant(value=None)),
        (False, ast.NameConstant(value=False)),
        (True, ast.NameConstant(value=True)),
        (..., ast.Ellipsis()),
        (123, ast.Num(n=123)),
        (4.5, ast.Num(n=4.5)),
        (6 + 7j, ast.Num(n=6 + 7j)),
        ("foo", ast.Str(s="foo")),
        (b"bar", ast.Bytes(s=b"bar")),
    ],
)
def test_make_constant_legacy(value: Any, expected: ast.Constant) -> None:
    test_utils.assert_ast_equal(
        observed=ast_utils.make_constant(value),
        expected=expected,
    )


@test_utils.require_at_least(8)
@pytest.mark.parametrize(
    "value,expected",
    [
        (None, ast.Constant(value=None)),
        (False, ast.Constant(value=False)),
        (True, ast.Constant(value=True)),
        (..., ast.Constant(value=...)),
        (123, ast.Constant(value=123)),
        (4.5, ast.Constant(value=4.5)),
        (6 + 7j, ast.Constant(value=6 + 7j)),
        ("foo", ast.Constant(value="foo")),
        (b"bar", ast.Constant(value=b"bar")),
    ],
)
def test_make_constant(value: Any, expected: ast.Constant) -> None:
    test_utils.assert_ast_equal(
        observed=ast_utils.make_constant(value),
        expected=expected,
    )


def test_make_constant_invalid() -> None:
    with pytest.raises(ValueError, match=r"^Unsupported type to generate"):
        ast_utils.make_constant(object())


@test_utils.require_at_most(7)
@pytest.mark.parametrize(
    "value,expected",
    [
        (ast.Bytes(s=b"foo"), True),
        (ast.Constant("bar"), True),
        (ast.Ellipsis(), True),
        (ast.NameConstant(value=None), True),
        (ast.Num(n=123), True),
        (ast.Str(s="baz"), True),
        (ast.Expr(value=ast.Num(456)), False),
        (ast.Global(names=["qux"]), False),
    ],
)
def test_is_constant_legacy(value: ast.AST, expected: bool) -> None:
    assert ast_utils.is_constant(value) is expected


@test_utils.require_at_least(8)
@pytest.mark.parametrize(
    "value,expected",
    [
        (ast.Constant(value="foo"), True),
        (ast.Expr(value=ast.Constant(value=123)), False),
        (ast.Global(names=["bar"]), False),
    ],
)
def test_is_constant(value: ast.AST, expected: bool) -> None:
    assert ast_utils.is_constant(value) is expected


@test_utils.require_at_most(7)
@pytest.mark.parametrize(
    "value,expected",
    [
        (ast.Bytes(s=b"foo"), False),
        (ast.Constant("bar"), True),
        (ast.Ellipsis(), False),
        (ast.NameConstant(value=None), False),
        (ast.Num(n=123), False),
        (ast.Str(s="baz"), True),
        (ast.Expr(value=ast.Num(456)), False),
        (ast.Global(names=["qux"]), False),
    ],
)
def test_is_str_legacy(value: ast.AST, expected: bool) -> None:
    assert ast_utils.is_str(value) is expected


@test_utils.require_at_least(8)
@pytest.mark.parametrize(
    "value,expected",
    [
        (ast.Constant(value=123), False),
        (ast.Constant(value="foo"), True),
        (ast.Expr(value=ast.Constant(value="foo")), False),
        (ast.Global(names=["foo"]), False),
    ],
)
def test_is_str(value: ast.AST, expected: bool) -> None:
    assert ast_utils.is_str(value) is expected


def test_extract_int_or_none() -> None:
    assert ast_utils.extract_int_or_none(ast_utils.make_constant(-123)) == -123
    assert ast_utils.extract_int_or_none(ast_utils.make_constant(0)) == 0
    assert ast_utils.extract_int_or_none(ast_utils.make_constant(123)) == 123


def test_extract_int_or_none_invalid() -> None:
    # Not a Constant node with int.
    assert ast_utils.extract_int_or_none(ast_utils.make_constant(None)) is None
    assert ast_utils.extract_int_or_none(ast_utils.make_constant(True)) is None
    assert ast_utils.extract_int_or_none(ast_utils.make_constant(...)) is None
    assert ast_utils.extract_int_or_none(ast_utils.make_constant(123.0)) is None
    assert ast_utils.extract_int_or_none(ast_utils.make_constant(4 + 5j)) is None
    assert ast_utils.extract_int_or_none(ast_utils.make_constant("123")) is None
    assert ast_utils.extract_int_or_none(ast_utils.make_constant(b"123")) is None


def test_extract_int() -> None:
    assert ast_utils.extract_int(ast_utils.make_constant(-123)) == -123
    assert ast_utils.extract_int(ast_utils.make_constant(0)) == 0
    assert ast_utils.extract_int(ast_utils.make_constant(123)) == 123


def test_extract_int_invalid() -> None:
    # Not a Constant node with int.
    with pytest.raises(ValueError, match=r"^Unsupported node to extract int"):
        ast_utils.extract_int(ast_utils.make_constant(None))
    with pytest.raises(ValueError, match=r"^Unsupported node to extract int"):
        ast_utils.extract_int(ast_utils.make_constant(True))
    with pytest.raises(ValueError, match=r"^Unsupported node to extract int"):
        ast_utils.extract_int(ast_utils.make_constant(...))
    with pytest.raises(ValueError, match=r"^Unsupported node to extract int"):
        ast_utils.extract_int(ast_utils.make_constant(123.0))
    with pytest.raises(ValueError, match=r"^Unsupported node to extract int"):
        ast_utils.extract_int(ast_utils.make_constant(4 + 5j))
    with pytest.raises(ValueError, match=r"^Unsupported node to extract int"):
        ast_utils.extract_int(ast_utils.make_constant("123"))
    with pytest.raises(ValueError, match=r"^Unsupported node to extract int"):
        ast_utils.extract_int(ast_utils.make_constant(b"123"))


@pytest.mark.parametrize(
    "value,expected",
    [
        (
            ast.Call(
                func=ast.Name(id="hypot", ctx=ast.Load()),
                args=[],
            ),
            "hypot",
        ),
        (
            ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id="math", ctx=ast.Load()),
                    attr="hypot",
                    ctx=ast.Load(),
                ),
                args=[],
            ),
            "hypot",
        ),
        (
            ast.Call(
                func=ast.Call(func=ast.Name(id="foo", ctx=ast.Load()), args=[]),
                args=[],
            ),
            None,
        ),
    ],
)
def test_extract_function_name_or_none(value: ast.Call, expected: str | None) -> None:
    assert ast_utils.extract_function_name_or_none(value) == expected
