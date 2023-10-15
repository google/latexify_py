"""End-to-end test cases of algorithmic style."""

from __future__ import annotations

import textwrap

from integration_tests import integration_utils


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
    ipython_latex = (
        r"\begin{array}{l}"
        r" \mathbf{function} \ \mathrm{fact}(n) \\"
        r" \hspace{1em} \mathbf{if} \ n = 0 \\"
        r" \hspace{2em} \mathbf{return} \ 1 \\"
        r" \hspace{1em} \mathbf{else} \\"
        r" \hspace{2em}"
        r" \mathbf{return} \ n \cdot"
        r" \mathrm{fact} \mathopen{}\left( n - 1 \mathclose{}\right) \\"
        r" \hspace{1em} \mathbf{end \ if} \\"
        r" \mathbf{end \ function}"
        r" \end{array}"
    )
    integration_utils.check_algorithm(fact, latex, ipython_latex)


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
                        \State $n \gets 3 n + 1$
                    \EndIf
                    \State $\mathrm{iterations} \gets \mathrm{iterations} + 1$
                \EndWhile
                \State \Return $\mathrm{iterations}$
            \EndFunction
        \end{algorithmic}
        """
    ).strip()
    ipython_latex = (
        r"\begin{array}{l}"
        r" \mathbf{function} \ \mathrm{collatz}(n) \\"
        r" \hspace{1em} \mathrm{iterations} \gets 0 \\"
        r" \hspace{1em} \mathbf{while} \ n > 1 \\"
        r" \hspace{2em} \mathbf{if} \ n \mathbin{\%} 2 = 0 \\"
        r" \hspace{3em} n \gets \left\lfloor\frac{n}{2}\right\rfloor \\"
        r" \hspace{2em} \mathbf{else} \\"
        r" \hspace{3em} n \gets 3 n + 1 \\"
        r" \hspace{2em} \mathbf{end \ if} \\"
        r" \hspace{2em}"
        r" \mathrm{iterations} \gets \mathrm{iterations} + 1 \\"
        r" \hspace{1em} \mathbf{end \ while} \\"
        r" \hspace{1em} \mathbf{return} \ \mathrm{iterations} \\"
        r" \mathbf{end \ function}"
        r" \end{array}"
    )
    integration_utils.check_algorithm(collatz, latex, ipython_latex)
