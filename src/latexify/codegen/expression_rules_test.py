"""Tests for latexify.codegen.expression_rules."""

from __future__ import annotations

import ast

import pytest

from latexify.codegen import expression_rules


@pytest.mark.parametrize(
    "node,precedence",
    [
        (ast.Call(), expression_rules._CALL_PRECEDENCE),
        (ast.BinOp(op=ast.Add()), expression_rules._PRECEDENCES[ast.Add]),
        (ast.UnaryOp(op=ast.UAdd()), expression_rules._PRECEDENCES[ast.UAdd]),
        (ast.BoolOp(op=ast.And()), expression_rules._PRECEDENCES[ast.And]),
        (ast.Compare(ops=[ast.Eq()]), expression_rules._PRECEDENCES[ast.Eq]),
        (ast.Name(), expression_rules._INF_PRECEDENCE),
        (ast.Attribute(), expression_rules._INF_PRECEDENCE),
    ],
)
def test_get_precedence(node: ast.AST, precedence: int) -> None:
    assert expression_rules.get_precedence(node) == precedence
