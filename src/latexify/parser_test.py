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
                    args=[ast.arg(arg="x")],
                ),
                body=[ast.Return(value=ast.Name(id="x", ctx=ast.Load()))],
            )
        ],
    )

    obtained = parser.parse_function(f)
    test_utils.assert_ast_equal(obtained, expected)


def test_parse_function_with_lambda() -> None:
    with pytest.raises(exceptions.LatexifySyntaxError, match=r"^Not a function\.$"):
        parser.parse_function(lambda: ())
    with pytest.raises(exceptions.LatexifySyntaxError, match=r"^Not a function\.$"):
        x = lambda: ()  # noqa: E731
        parser.parse_function(x)
