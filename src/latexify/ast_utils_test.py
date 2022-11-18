"""Tests for latexify.ast_utils."""

from __future__ import annotations

import ast
from typing import Any

import pytest

from latexify import ast_utils, test_utils


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


def test_extract_int_or_none() -> None:
    assert ast_utils.extract_int_or_none(ast_utils.make_constant(-123)) == -123
    assert ast_utils.extract_int_or_none(ast_utils.make_constant(0)) == 0
    assert ast_utils.extract_int_or_none(ast_utils.make_constant(123)) == 123


def test_extract_int_or_none_invalid() -> None:
    # Not a subtree.
    assert ast_utils.extract_int_or_none(123) is None

    # Not a direct Constant node.
    assert (
        ast_utils.extract_int_or_none(ast.Expr(value=ast_utils.make_constant(123)))
        is None
    )

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
    # Not a subtree.
    with pytest.raises(ValueError, match=r"^Unsupported node to extract int"):
        ast_utils.extract_int(123)

    # Not a direct Constant node.
    with pytest.raises(ValueError, match=r"^Unsupported node to extract int"):
        ast_utils.extract_int(ast.Expr(value=ast_utils.make_constant(123)))

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
