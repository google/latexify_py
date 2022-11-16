"""Tests for latexify.transformer.prefix_trimmer."""

from __future__ import annotations

import ast
import pytest
from latexify import test_utils
from latexify.transformers.prefix_trimmer import PrefixTrimmer


def test_correct_trim() -> None:
    source = ast.Call(
        func=ast.Attribute(
            value=ast.Name(id="math", ctx=ast.Load()), attr="sqrt", ctx=ast.Load()
        ),
        args=[ast.Name(id="x", ctx=ast.Load())],
        keywords=[],
    )
    expected = ast.Call(
        func=ast.Name(id="sqrt", ctx=ast.Load()),
        args=[ast.Name(id="x", ctx=ast.Load())],
        keywords=[],
    )
    transformed = PrefixTrimmer({"math"}).visit(source)
    test_utils.assert_ast_equal(transformed, expected)


def test_correct_recursive_trim() -> None:
    source = ast.Call(
        func=ast.Attribute(
            value=ast.Attribute(
                value=ast.Name(id="foo", ctx=ast.Load()), attr="bar", ctx=ast.Load()
            ),
            attr="lat",
            ctx=ast.Load(),
        ),
        args=[ast.Name(id="x", ctx=ast.Load())],
        keywords=[],
    )
    expected = ast.Call(
        func=ast.Name(id="lat", ctx=ast.Load()),
        args=[ast.Name(id="x", ctx=ast.Load())],
        keywords=[],
    )
    transformed = PrefixTrimmer({"foo"}).visit(source)
    test_utils.assert_ast_equal(transformed, expected)


def test_not_correct_trim() -> None:
    source = ast.Call(
        func=ast.Attribute(
            value=ast.Name(id="math", ctx=ast.Load()), attr="sqrt", ctx=ast.Load()
        ),
        args=[ast.Name(id="x", ctx=ast.Load())],
        keywords=[],
    )
    expected = ast.Call(
        func=ast.Name(id="sqrt", ctx=ast.Load()),
        args=[ast.Name(id="x", ctx=ast.Load())],
        keywords=[],
    )
    transformed = PrefixTrimmer({""}).visit(source)
    with pytest.raises(AssertionError):
        test_utils.assert_ast_equal(transformed, expected)


def test_not_correct_recursive_trim() -> None:
    source = ast.Call(
        func=ast.Attribute(
            value=ast.Attribute(
                value=ast.Name(id="foo", ctx=ast.Load()), attr="bar", ctx=ast.Load()
            ),
            attr="lat",
            ctx=ast.Load(),
        ),
        args=[ast.Name(id="x", ctx=ast.Load())],
        keywords=[],
    )
    expected = ast.Call(
        func=ast.Name(id="lat", ctx=ast.Load()),
        args=[ast.Name(id="x", ctx=ast.Load())],
        keywords=[],
    )
    transformed = PrefixTrimmer({"lat"}).visit(source)
    with pytest.raises(AssertionError):
        test_utils.assert_ast_equal(transformed, expected)
