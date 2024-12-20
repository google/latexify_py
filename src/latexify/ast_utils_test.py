"""Tests for latexify.ast_utils."""

from __future__ import annotations

import ast
import sys
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
                keywords=[],
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
                keywords=[],
            ),
            "hypot",
        ),
        (
            ast.Call(
                func=ast.Call(
                    func=ast.Name(id="foo", ctx=ast.Load()), args=[], keywords=[]
                ),
                args=[],
                keywords=[],
            ),
            None,
        ),
    ],
)
def test_extract_function_name_or_none(value: ast.Call, expected: str | None) -> None:
    assert ast_utils.extract_function_name_or_none(value) == expected


def test_create_function_def() -> None:
    expected_args = ast.arguments(
        posonlyargs=[],
        args=[ast.arg(arg="x")],
        vararg=None,
        kwonlyargs=[],
        kw_defaults=[],
        kwarg=None,
        defaults=[],
    )

    kwargs = {
        "name": "test_func",
        "args": expected_args,
        "body": [ast.Return(value=ast.Name(id="x", ctx=ast.Load()))],
        "decorator_list": [],
        "returns": None,
        "type_comment": None,
        "lineno": 1,
        "col_offset": 0,
        "end_lineno": 2,
        "end_col_offset": 0,
    }
    if sys.version_info.minor >= 12:
        kwargs["type_params"] = []

    func_def = ast_utils.create_function_def(**kwargs)
    assert isinstance(func_def, ast.FunctionDef)
    assert func_def.name == "test_func"

    assert func_def.args.posonlyargs == expected_args.posonlyargs
    assert func_def.args.args == expected_args.args
    assert func_def.args.kwonlyargs == expected_args.kwonlyargs
    assert func_def.args.kw_defaults == expected_args.kw_defaults
    assert func_def.args.defaults == expected_args.defaults
