"""Tests for latexify.codegen.expression_rules."""

from __future__ import annotations

import ast

import pytest

from latexify.codegen import expression_rules


@pytest.mark.parametrize(
    "node,precedence",
    [
        (
            ast.Call(func=ast.Name(id="func", ctx=ast.Load()), args=[], keywords=[]),
            expression_rules._CALL_PRECEDENCE,
        ),
        (
            ast.BinOp(
                left=ast.Name(id="left", ctx=ast.Load()),
                op=ast.Add(),
                right=ast.Name(id="right", ctx=ast.Load()),
            ),
            expression_rules._PRECEDENCES[ast.Add],
        ),
        (
            ast.UnaryOp(op=ast.UAdd(), operand=ast.Name(id="operand", ctx=ast.Load())),
            expression_rules._PRECEDENCES[ast.UAdd],
        ),
        (
            ast.BoolOp(op=ast.And(), values=[ast.Name(id="value", ctx=ast.Load())]),
            expression_rules._PRECEDENCES[ast.And],
        ),
        (
            ast.Compare(
                left=ast.Name(id="left", ctx=ast.Load()),
                ops=[ast.Eq()],
                comparators=[ast.Name(id="right", ctx=ast.Load())],
            ),
            expression_rules._PRECEDENCES[ast.Eq],
        ),
        (ast.Name(id="name", ctx=ast.Load()), expression_rules._INF_PRECEDENCE),
        (
            ast.Attribute(
                value=ast.Name(id="value", ctx=ast.Load()), attr="attr", ctx=ast.Load()
            ),
            expression_rules._INF_PRECEDENCE,
        ),
    ],
)
def test_get_precedence(node: ast.AST, precedence: int) -> None:
    assert expression_rules.get_precedence(node) == precedence
