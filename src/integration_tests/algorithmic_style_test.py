"""End-to-end test cases of algorithmic style."""

from __future__ import annotations

import textwrap
from typing import Any, Callable

from latexify import frontend


def check_algorithm(
    fn: Callable[..., Any],
    latex: str,
    **kwargs,
) -> None:
    """Helper to check if the obtained function has the expected LaTeX form.

    Args:
        fn: Function to check.
        latex: LaTeX form of `fn`.
        **kwargs: Arguments passed to `frontend.get_latex`.
    """
    # Checks the syntax:
    #     def fn(...):
    #         ...
    #     latexified = get_latex(fn, style=ALGORITHM, **kwargs)
    latexified = frontend.get_latex(fn, style=frontend.Style.ALGORITHMIC, **kwargs)
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
    check_algorithm(fact, latex)


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
    check_algorithm(collatz, latex)
