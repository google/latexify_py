"""Tests for latexify.transformer.prefix_trimmer."""

from __future__ import annotations

import ast

from latexify import test_utils
from latexify.transformers.prefix_trimmer import PrefixTrimmer


def test_correct_call_trim() -> None:
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
    transformed = PrefixTrimmer(["math"]).visit(source)
    test_utils.assert_ast_equal(transformed, expected)
