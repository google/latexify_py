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
    [
        (
            "x = 3",
            r"\State $x \gets 3$",
        ),
        (
            "a = b = 0",
            r"\State $a \gets b \gets 0$",
        ),
    ],
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
            r"""
            \begin{algorithmic}
                \Function{f}{$x$}
                    \State \Return $x$
                \EndFunction
            \end{algorithmic}
            """,
        ),
        (
            "def xyz(a, b, c): return 3",
            r"""
            \begin{algorithmic}
                \Function{xyz}{$a, b, c$}
                    \State \Return $3$
                \EndFunction
            \end{algorithmic}
            """,
        ),
    ],
)
def test_visit_functiondef(code: str, latex: str) -> None:
    node = ast.parse(textwrap.dedent(code)).body[0]
    assert isinstance(node, ast.FunctionDef)
    assert (
        algorithmic_codegen.AlgorithmicCodegen().visit(node)
        == textwrap.dedent(latex).strip()
    )


@pytest.mark.parametrize(
    "code,latex",
    [
        (
            "if x < y: return x",
            r"""
            \If{$x < y$}
                \State \Return $x$
            \EndIf
            """,
        ),
        (
            "if True: x\nelse: y",
            r"""
            \If{$\mathrm{True}$}
                \State $x$
            \Else
                \State $y$
            \EndIf
            """,
        ),
    ],
)
def test_visit_if(code: str, latex: str) -> None:
    node = ast.parse(code).body[0]
    assert isinstance(node, ast.If)
    assert (
        algorithmic_codegen.AlgorithmicCodegen().visit(node)
        == textwrap.dedent(latex).strip()
    )


@pytest.mark.parametrize(
    "code,latex",
    [
        (
            "return x + y",
            r"\State \Return $x + y$",
        ),
        (
            "return",
            r"\State \Return",
        ),
    ],
)
def test_visit_return(code: str, latex: str) -> None:
    node = ast.parse(code).body[0]
    assert isinstance(node, ast.Return)
    assert algorithmic_codegen.AlgorithmicCodegen().visit(node) == latex


@pytest.mark.parametrize(
    "code,latex",
    [
        (
            "while x < y: x = x + 1",
            r"""
            \While{$x < y$}
                \State $x \gets x + 1$
            \EndWhile
            """,
        )
    ],
)
def test_visit_while(code: str, latex: str) -> None:
    node = ast.parse(code).body[0]
    assert isinstance(node, ast.While)
    assert (
        algorithmic_codegen.AlgorithmicCodegen().visit(node)
        == textwrap.dedent(latex).strip()
    )


def test_visit_while_with_else() -> None:
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
    with pytest.raises(
        exceptions.LatexifyNotSupportedError,
        match="^While statement with the else clause is not supported$",
    ):
        algorithmic_codegen.AlgorithmicCodegen().visit(node)


@pytest.mark.parametrize(
    "code,latex",
    [
        ("x = 3", r"\displaystyle \hspace{0pt} x \gets 3"),
        ("a = b = 0", r"\displaystyle \hspace{0pt} a \gets b \gets 0"),
    ],
)
def test_visit_assign_jupyter(code: str, latex: str) -> None:
    node = ast.parse(textwrap.dedent(code)).body[0]
    assert isinstance(node, ast.Assign)
    assert algorithmic_codegen.IPythonAlgorithmicCodegen().visit(node) == latex


@pytest.mark.parametrize(
    "code,latex",
    [
        (
            "def f(x): return x",
            (
                r"\displaystyle \hspace{0pt} \mathbf{function}"
                r" \ \mathrm{F}(x) \\"
                r" \displaystyle \hspace{16pt} \mathbf{return} \ x \\"
                r" \displaystyle \hspace{0pt} \mathbf{end \ function}"
            ),
        ),
        (
            "def f(a, b, c): return 3",
            (
                r"\displaystyle \hspace{0pt} \mathbf{function}"
                r" \ \mathrm{F}(a, b, c) \\"
                r" \displaystyle \hspace{16pt} \mathbf{return} \ 3 \\"
                r" \displaystyle \hspace{0pt} \mathbf{end \ function}"
            ),
        ),
    ],
)
def test_visit_functiondef_jupyter(code: str, latex: str) -> None:
    node = ast.parse(textwrap.dedent(code)).body[0]
    assert isinstance(node, ast.FunctionDef)
    assert algorithmic_codegen.IPythonAlgorithmicCodegen().visit(node) == latex


@pytest.mark.parametrize(
    "code,latex",
    [
        (
            "if x < y: return x",
            (
                r"\displaystyle \hspace{0pt} \mathbf{if} \ x < y \\"
                r" \displaystyle \hspace{16pt} \mathbf{return} \ x \\"
                r" \displaystyle \hspace{0pt} \mathbf{end \ if}"
            ),
        ),
        (
            "if True: x\nelse: y",
            (
                r"\displaystyle \hspace{0pt} \mathbf{if} \ \mathrm{True} \\"
                r" \displaystyle \hspace{16pt} x \\"
                r" \displaystyle \hspace{0pt} \mathbf{else} \\"
                r" \displaystyle \hspace{16pt} y \\"
                r" \displaystyle \hspace{0pt} \mathbf{end \ if}"
            ),
        ),
    ],
)
def test_visit_if_jupyter(code: str, latex: str) -> None:
    node = ast.parse(textwrap.dedent(code)).body[0]
    assert isinstance(node, ast.If)
    assert algorithmic_codegen.IPythonAlgorithmicCodegen().visit(node) == latex


@pytest.mark.parametrize(
    "code,latex",
    [
        (
            "return x + y",
            r"\displaystyle \hspace{0pt} \mathbf{return} \ x + y",
        ),
        (
            "return",
            r"\displaystyle \hspace{0pt} \mathbf{return}",
        ),
    ],
)
def test_visit_return_jupyter(code: str, latex: str) -> None:
    node = ast.parse(textwrap.dedent(code)).body[0]
    assert isinstance(node, ast.Return)
    assert algorithmic_codegen.IPythonAlgorithmicCodegen().visit(node) == latex


@pytest.mark.parametrize(
    "code,latex",
    [
        (
            "while x < y: x = x + 1",
            (
                r"\displaystyle \hspace{0pt} \mathbf{while} \ x < y \\"
                r" \displaystyle \hspace{16pt} x \gets x + 1 \\"
                r" \displaystyle \hspace{0pt} \mathbf{end \ while}"
            ),
        )
    ],
)
def test_visit_while_jupyter(code: str, latex: str) -> None:
    node = ast.parse(textwrap.dedent(code)).body[0]
    assert isinstance(node, ast.While)
    assert algorithmic_codegen.IPythonAlgorithmicCodegen().visit(node) == latex


def test_visit_while_with_else_jupyter() -> None:
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
    with pytest.raises(
        exceptions.LatexifyNotSupportedError,
        match="^While statement with the else clause is not supported$",
    ):
        algorithmic_codegen.IPythonAlgorithmicCodegen().visit(node)
