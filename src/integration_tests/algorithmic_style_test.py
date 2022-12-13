"""End-to-end test cases of algorithmic style."""

from __future__ import annotations

import textwrap
from typing import Any, Callable

from latexify import generate_latex


def check_algorithm(
    fn: Callable[..., Any],
    latex: str,
    style: generate_latex.Style,
    **kwargs,
) -> None:
    """Helper to check if the obtained function has the expected LaTeX form.

    Args:
        fn: Function to check.
        latex: LaTeX form of `fn`.
        style: The style of the output.
        **kwargs: Arguments passed to `frontend.get_latex`.
    """
    # Checks the syntax:
    #     def fn(...):
    #         ...
    #     latexified = get_latex(fn, style=ALGORITHM, **kwargs)
    latexified = generate_latex.get_latex(fn, style=style, **kwargs)
    assert latexified == latex


def test_factorial() -> None:
    def fact(n):
        if n == 0:
            return 1
        else:
            return n * fact(n - 1)

    latex = textwrap.dedent(
        r"""
        \begin{algorithmic}
            \Function{fact}{$n$}
                \If{$n = 0$}
                    \State \Return $1$
                \Else
                    \State \Return $n \cdot \mathrm{fact} \mathopen{}\left( n - 1 \mathclose{}\right)$
                \EndIf
            \EndFunction
        \end{algorithmic}
        """  # noqa: E501
    ).strip()
    check_algorithm(fact, latex, generate_latex.Style.ALGORITHMIC)


def test_collatz() -> None:
    def collatz(n):
        iterations = 0
        while n > 1:
            if n % 2 == 0:
                n = n // 2
            else:
                n = 3 * n + 1
            iterations = iterations + 1
        return iterations

    latex = textwrap.dedent(
        r"""
        \begin{algorithmic}
            \Function{collatz}{$n$}
                \State $\mathrm{iterations} \gets 0$
                \While{$n > 1$}
                    \If{$n \mathbin{\%} 2 = 0$}
                        \State $n \gets \left\lfloor\frac{n}{2}\right\rfloor$
                    \Else
                        \State $n \gets 3 \cdot n + 1$
                    \EndIf
                    \State $\mathrm{iterations} \gets \mathrm{iterations} + 1$
                \EndWhile
                \State \Return $\mathrm{iterations}$
            \EndFunction
        \end{algorithmic}
        """
    ).strip()
    check_algorithm(collatz, latex, generate_latex.Style.ALGORITHMIC)


def test_factorial_jupyter() -> None:
    def fact(n):
        if n == 0:
            return 1
        else:
            return n * fact(n - 1)

    latex = (
        r"\displaystyle \hspace{0pt} \mathbf{function} \ \mathrm{FACT}(n) \\"
        r" \displaystyle \hspace{16pt} \mathbf{if} \ n = 0 \\"
        r" \displaystyle \hspace{32pt} \mathbf{return} \ 1 \\"
        r" \displaystyle \hspace{16pt} \mathbf{else} \\"
        r" \displaystyle \hspace{32pt}"
        r" \mathbf{return} \ n \cdot"
        r" \mathrm{fact} \mathopen{}\left( n - 1 \mathclose{}\right) \\"
        r" \displaystyle \hspace{16pt} \mathbf{end \ if} \\"
        r" \displaystyle \hspace{0pt} \mathbf{end \ function}"
    )
    check_algorithm(fact, latex, generate_latex.Style.IPYTHON_ALGORITHMIC)


def test_collatz_jupyter() -> None:
    def collatz(n):
        iterations = 0
        while n > 1:
            if n % 2 == 0:
                n = n // 2
            else:
                n = 3 * n + 1
            iterations = iterations + 1
        return iterations

    latex = (
        r"\displaystyle \hspace{0pt} \mathbf{function} \ \mathrm{COLLATZ}(n) \\"
        r" \displaystyle \hspace{16pt} \mathrm{iterations} \gets 0 \\"
        r" \displaystyle \hspace{16pt} \mathbf{while} \ n > 1 \\"
        r" \displaystyle \hspace{32pt} \mathbf{if} \ n \mathbin{\%} 2 = 0 \\"
        r" \displaystyle \hspace{48pt} n \gets \left\lfloor\frac{n}{2}\right\rfloor \\"
        r" \displaystyle \hspace{32pt} \mathbf{else} \\"
        r" \displaystyle \hspace{48pt} n \gets 3 \cdot n + 1 \\"
        r" \displaystyle \hspace{32pt} \mathbf{end \ if} \\"
        r" \displaystyle \hspace{32pt}"
        r" \mathrm{iterations} \gets \mathrm{iterations} + 1 \\"
        r" \displaystyle \hspace{16pt} \mathbf{end \ while} \\"
        r" \displaystyle \hspace{16pt} \mathbf{return} \ \mathrm{iterations} \\"
        r" \displaystyle \hspace{0pt} \mathbf{end \ function}"
    )
    check_algorithm(collatz, latex, generate_latex.Style.IPYTHON_ALGORITHMIC)
