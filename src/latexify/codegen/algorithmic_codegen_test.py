"""Tests for latexify.codegen.algorithmic_codegen."""

from __future__ import annotations

import ast
import textwrap

import pytest

from latexify import exceptions
from latexify.codegen import algorithmic_codegen


def test_generic_visit() -> None:
    class UnknownNode(ast.AST):
        pass

    with pytest.raises(
        exceptions.LatexifyNotSupportedError,
        match=r"^Unsupported AST: UnknownNode$",
    ):
        algorithmic_codegen.AlgorithmicCodegen().visit(UnknownNode())


@pytest.mark.parametrize(
    "code,latex",
    [("x = 3", r"\State $x \gets 3$"), ("a = b = 0", r"\State $a \gets b \gets 0$")],
)
def test_visit_assign(code: str, latex: str) -> None:
    node = ast.parse(textwrap.dedent(code)).body[0]
    assert isinstance(node, ast.Assign)
    assert algorithmic_codegen.AlgorithmicCodegen().visit(node) == latex


@pytest.mark.parametrize(
    "code,latex",
    [
        (
            "def f(x): return x",
            (
                r"\begin{algorithmic} "
                r"\Procedure{f}{$x$} "
                r"\State \Return $x$ "
                r"\EndProcedure "
                r"\end{algorithmic}"
            ),
        ),
        (
            "def xyz(a, b, c): return 3",
            (
                r"\begin{algorithmic} "
                r"\Procedure{xyz}{$a,b,c$} "
                r"\State \Return $3$ "
                r"\EndProcedure "
                r"\end{algorithmic}"
            ),
        ),
    ],
)
def test_visit_functiondef(code: str, latex: str) -> None:
    node = ast.parse(textwrap.dedent(code)).body[0]
    assert isinstance(node, ast.FunctionDef)
    assert algorithmic_codegen.AlgorithmicCodegen().visit(node) == latex


@pytest.mark.parametrize(
    "code,latex",
    [
        ("if x < y: return x", r"\If{$x < y$} \State \Return $x$ \EndIf"),
        (
            "if True: x\nelse: y",
            r"\If{$\mathrm{True}$} \State $x$ \Else \State $y$ \EndIf",
        ),
    ],
)
def test_visit_if(code: str, latex: str) -> None:
    node = ast.parse(textwrap.dedent(code)).body[0]
    assert isinstance(node, ast.If)
    assert algorithmic_codegen.AlgorithmicCodegen().visit(node) == latex


@pytest.mark.parametrize(
    "code,latex",
    [
        (
            "return x + y",
            r"\State \Return $x + y$",
        ),
        (
            "return",
            r"\State \Return $\mathrm{None}$",
        ),
    ],
)
def test_visit_return(code: str, latex: str) -> None:
    node = ast.parse(textwrap.dedent(code)).body[0]
    assert isinstance(node, ast.Return)
    assert algorithmic_codegen.AlgorithmicCodegen().visit(node) == latex


@pytest.mark.parametrize(
    "code,latex",
    [
        (
            "while x < y: x = x + 1",
            r"\While{$x < y$} \State $x \gets x + 1$ \EndWhile",
        )
    ],
)
def test_visit_while(code: str, latex: str) -> None:
    node = ast.parse(textwrap.dedent(code)).body[0]
    assert isinstance(node, ast.While)
    assert algorithmic_codegen.AlgorithmicCodegen().visit(node) == latex


def test_visit_while_with_else() -> None:
    with pytest.raises(exceptions.LatexifyNotSupportedError):
        node = ast.parse(
            textwrap.dedent(
                """
                while True:
                    x = x
                else:
                    x = y
                """
            )
        ).body[0]
        assert isinstance(node, ast.While)
        algorithmic_codegen.AlgorithmicCodegen().visit(node)
