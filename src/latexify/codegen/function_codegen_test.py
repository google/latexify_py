"""Tests for latexify.codegen.function_codegen."""

from __future__ import annotations

import ast
import textwrap

import pytest

from latexify import exceptions
from latexify.codegen import function_codegen


def test_generic_visit() -> None:
    class UnknownNode(ast.AST):
        pass

    with pytest.raises(
        exceptions.LatexifyNotSupportedError,
        match=r"^Unsupported AST: UnknownNode$",
    ):
        function_codegen.FunctionCodegen().visit(UnknownNode())


def test_visit_functiondef_use_signature() -> None:
    tree = ast.parse(
        textwrap.dedent(
            """
            def f(x):
                return x
            """
        )
    ).body[0]
    assert isinstance(tree, ast.FunctionDef)

    latex_without_flag = "x"
    latex_with_flag = r"f(x) = x"
    assert function_codegen.FunctionCodegen().visit(tree) == latex_with_flag
    assert (
        function_codegen.FunctionCodegen(use_signature=False).visit(tree)
        == latex_without_flag
    )
    assert (
        function_codegen.FunctionCodegen(use_signature=True).visit(tree)
        == latex_with_flag
    )


def test_visit_functiondef_ignore_docstring() -> None:
    tree = ast.parse(
        textwrap.dedent(
            """
            def f(x):
                '''docstring'''
                return x
            """
        )
    ).body[0]
    assert isinstance(tree, ast.FunctionDef)

    latex = r"f(x) = x"
    assert function_codegen.FunctionCodegen().visit(tree) == latex


def test_visit_functiondef_ignore_multiple_constants() -> None:
    tree = ast.parse(
        textwrap.dedent(
            """
            def f(x):
                '''docstring'''
                3
                True
                return x
            """
        )
    ).body[0]
    assert isinstance(tree, ast.FunctionDef)

    latex = r"f(x) = x"
    assert function_codegen.FunctionCodegen().visit(tree) == latex
