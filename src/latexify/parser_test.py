"""Tests for latexify.parser."""

from __future__ import annotations

import ast

import pytest

from latexify import exceptions, parser, test_utils


def test_parse_function_with_posonlyargs() -> None:
    def f(x):
        return x

    expected = ast.Module(
        body=[
            ast.FunctionDef(
                name="f",
                args=ast.arguments(
                    posonlyargs=[],
                    args=[ast.arg(arg="x")],
                    vararg=None,
                    kwonlyargs=[],
                    kw_defaults=[],
                    kwarg=None,
                    defaults=[],
                ),
                body=[ast.Return(value=ast.Name(id="x", ctx=ast.Load()))],
                decorator_list=[],
                returns=None,
                type_comment=None,
                type_params=[],
                lineno=1,
                col_offset=0,
                end_lineno=2,
                end_col_offset=0,
            )
        ],
        type_ignores=[],
    )

    obtained = parser.parse_function(f)
    test_utils.assert_ast_equal(obtained, expected)


def test_parse_function_with_lambda() -> None:
    with pytest.raises(exceptions.LatexifySyntaxError, match=r"^Not a function\.$"):
        parser.parse_function(lambda: ())
    with pytest.raises(exceptions.LatexifySyntaxError, match=r"^Not a function\.$"):
        x = lambda: ()  # noqa: E731
        parser.parse_function(x)
