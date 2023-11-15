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
            "for i in {1}: x = i",
            r"""
            \For{$i \in \mathopen{}\left\{ 1 \mathclose{}\right\}$}
                \State $x \gets i$
            \EndFor
            """,
        ),
    ],
)
def test_visit_for(code: str, latex: str) -> None:
    node = ast.parse(textwrap.dedent(code)).body[0]
    assert isinstance(node, ast.For)
    assert (
        algorithmic_codegen.AlgorithmicCodegen().visit(node)
        == textwrap.dedent(latex).strip()
    )


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


def test_visit_pass() -> None:
    node = ast.parse("pass").body[0]
    assert isinstance(node, ast.Pass)
    assert (
        algorithmic_codegen.AlgorithmicCodegen().visit(node)
        == r"\State $\mathbf{pass}$"
    )


def test_visit_break() -> None:
    node = ast.parse("break").body[0]
    assert isinstance(node, ast.Break)
    assert (
        algorithmic_codegen.AlgorithmicCodegen().visit(node)
        == r"\State $\mathbf{break}$"
    )


def test_visit_continue() -> None:
    node = ast.parse("continue").body[0]
    assert isinstance(node, ast.Continue)
    assert (
        algorithmic_codegen.AlgorithmicCodegen().visit(node)
        == r"\State $\mathbf{continue}$"
    )


@pytest.mark.parametrize(
    "code,latex",
    [
        ("x = 3", r"x \gets 3"),
        ("a = b = 0", r"a \gets b \gets 0"),
    ],
)
def test_visit_assign_ipython(code: str, latex: str) -> None:
    node = ast.parse(textwrap.dedent(code)).body[0]
    assert isinstance(node, ast.Assign)
    assert algorithmic_codegen.IPythonAlgorithmicCodegen().visit(node) == latex


@pytest.mark.parametrize(
    "code,latex",
    [
        (
            "for i in {1}: x = i",
            (
                r"\mathbf{for} \ i \in \mathopen{}\left\{ 1 \mathclose{}\right\}"
                r" \ \mathbf{do} \\"
                r" \hspace{1em} x \gets i \\"
                r" \mathbf{end \ for}"
            ),
        ),
    ],
)
def test_visit_for_ipython(code: str, latex: str) -> None:
    node = ast.parse(textwrap.dedent(code)).body[0]
    assert isinstance(node, ast.For)
    assert (
        algorithmic_codegen.IPythonAlgorithmicCodegen().visit(node)
        == textwrap.dedent(latex).strip()
    )


@pytest.mark.parametrize(
    "code,latex",
    [
        (
            "def f(x): return x",
            (
                r"\begin{array}{l}"
                r" \mathbf{function}"
                r" \ f(x) \\"
                r" \hspace{1em} \mathbf{return} \ x \\"
                r" \mathbf{end \ function}"
                r" \end{array}"
            ),
        ),
        (
            "def f(a, b, c): return 3",
            (
                r"\begin{array}{l}"
                r" \mathbf{function}"
                r" \ f(a, b, c) \\"
                r" \hspace{1em} \mathbf{return} \ 3 \\"
                r" \mathbf{end \ function}"
                r" \end{array}"
            ),
        ),
    ],
)
def test_visit_functiondef_ipython(code: str, latex: str) -> None:
    node = ast.parse(textwrap.dedent(code)).body[0]
    assert isinstance(node, ast.FunctionDef)
    assert algorithmic_codegen.IPythonAlgorithmicCodegen().visit(node) == latex


@pytest.mark.parametrize(
    "code,latex",
    [
        (
            "if x < y: return x",
            (
                r"\mathbf{if} \ x < y \\"
                r" \hspace{1em} \mathbf{return} \ x \\"
                r" \mathbf{end \ if}"
            ),
        ),
        (
            "if True: x\nelse: y",
            (
                r"\mathbf{if} \ \mathrm{True} \\"
                r" \hspace{1em} x \\"
                r" \mathbf{else} \\"
                r" \hspace{1em} y \\"
                r" \mathbf{end \ if}"
            ),
        ),
    ],
)
def test_visit_if_ipython(code: str, latex: str) -> None:
    node = ast.parse(textwrap.dedent(code)).body[0]
    assert isinstance(node, ast.If)
    assert algorithmic_codegen.IPythonAlgorithmicCodegen().visit(node) == latex


@pytest.mark.parametrize(
    "code,latex",
    [
        (
            "return x + y",
            r"\mathbf{return} \ x + y",
        ),
        (
            "return",
            r"\mathbf{return}",
        ),
    ],
)
def test_visit_return_ipython(code: str, latex: str) -> None:
    node = ast.parse(textwrap.dedent(code)).body[0]
    assert isinstance(node, ast.Return)
    assert algorithmic_codegen.IPythonAlgorithmicCodegen().visit(node) == latex


@pytest.mark.parametrize(
    "code,latex",
    [
        (
            "while x < y: x = x + 1",
            (
                r"\mathbf{while} \ x < y \\"
                r" \hspace{1em} x \gets x + 1 \\"
                r" \mathbf{end \ while}"
            ),
        )
    ],
)
def test_visit_while_ipython(code: str, latex: str) -> None:
    node = ast.parse(textwrap.dedent(code)).body[0]
    assert isinstance(node, ast.While)
    assert algorithmic_codegen.IPythonAlgorithmicCodegen().visit(node) == latex


def test_visit_while_with_else_ipython() -> None:
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


def test_visit_pass_ipython() -> None:
    node = ast.parse("pass").body[0]
    assert isinstance(node, ast.Pass)
    assert (
        algorithmic_codegen.IPythonAlgorithmicCodegen().visit(node) == r"\mathbf{pass}"
    )


def test_visit_break_ipython() -> None:
    node = ast.parse("break").body[0]
    assert isinstance(node, ast.Break)
    assert (
        algorithmic_codegen.IPythonAlgorithmicCodegen().visit(node) == r"\mathbf{break}"
    )


def test_visit_continue_ipython() -> None:
    node = ast.parse("continue").body[0]
    assert isinstance(node, ast.Continue)
    assert (
        algorithmic_codegen.IPythonAlgorithmicCodegen().visit(node)
        == r"\mathbf{continue}"
    )
