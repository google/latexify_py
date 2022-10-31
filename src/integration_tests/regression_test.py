"""End-to-end test cases of with_latex."""

from __future__ import annotations

from collections.abc import Callable
import math
from typing import Any

from latexify import frontend


def _check_with_latex(
    fn: Callable[..., Any],
    latex: str,
    **kwargs,
) -> None:
    """Helper to check if the obtained function has the expected LaTeX form.

    Args:
        fn: Function to check.
        latex: LaTeX form of `fn`.
        **kwargs: Arguments passed to `frontend.with_latex`.
    """
    # Checks the syntax:
    #     @with_latex
    #     def fn(...):
    #         ...
    if not kwargs:
        latexified = frontend.with_latex(fn)
        assert str(latexified) == latex
        assert latexified._repr_latex_() == rf"$$ \displaystyle {latex} $$"

    # Checks the syntax:
    #     @with_latex(**kwargs)
    #     def fn(...):
    #         ...
    latexified = frontend.with_latex(fn, **kwargs)
    assert str(latexified) == latex
    assert latexified._repr_latex_() == rf"$$ \displaystyle {latex} $$"

    # Checks the syntax:
    #     def fn(...):
    #         ...
    #     latexified = with_latex(fn, **kwargs)
    latexified = frontend.with_latex(fn, **kwargs)
    assert str(latexified) == latex
    assert latexified._repr_latex_() == rf"$$ \displaystyle {latex} $$"


def test_quadratic_solution() -> None:
    def solve(a, b, c):
        return (-b + math.sqrt(b**2 - 4 * a * c)) / (2 * a)

    latex = r"\mathrm{solve}(a, b, c) = \frac{-b + \sqrt{b^{{2}} - {4}ac}}{{2}a}"
    _check_with_latex(solve, latex)


def test_sinc() -> None:
    def sinc(x):
        if x == 0:
            return 1
        else:
            return math.sin(x) / x

    latex = (
        r"\mathrm{sinc}(x) = "
        r"\left\{ \begin{array}{ll} "
        r"{1}, & \mathrm{if} \ "
        r"{x = {0}} \\ \frac{\sin{\left({x}\right)}}{x}, & \mathrm{otherwise} "
        r"\end{array} \right."
    )
    _check_with_latex(sinc, latex)


def test_x_times_beta() -> None:
    def xtimesbeta(x, beta):
        return x * beta

    latex_without_symbols = r"\mathrm{xtimesbeta}(x, beta) = xbeta"
    _check_with_latex(xtimesbeta, latex_without_symbols)
    _check_with_latex(xtimesbeta, latex_without_symbols, use_math_symbols=False)

    latex_with_symbols = r"\mathrm{xtimesbeta}(x, {\beta}) = x{\beta}"
    _check_with_latex(xtimesbeta, latex_with_symbols, use_math_symbols=True)


def test_sum_with_limit_1arg() -> None:
    def sum_with_limit(n):
        return sum(i**2 for i in range(n))

    latex = (
        r"\mathrm{sum_with_limit}(n) = \sum_{i = 0}^{{n - 1}} \left({i^{{2}}}\right)"
    )
    _check_with_latex(sum_with_limit, latex)


def test_sum_with_limit_2args() -> None:
    def sum_with_limit(a, n):
        return sum(i**2 for i in range(a, n))

    latex = (
        r"\mathrm{sum_with_limit}(a, n) = \sum_{i = a}^{{n - 1}} \left({i^{{2}}}\right)"
    )
    _check_with_latex(sum_with_limit, latex)


def test_prod_with_limit_1arg() -> None:
    def prod_with_limit(n):
        return math.prod(i**2 for i in range(n))

    latex = (
        r"\mathrm{prod_with_limit}(n) = \prod_{i = 0}^{{n - 1}} \left({i^{{2}}}\right)"
    )
    _check_with_latex(prod_with_limit, latex)


def test_prod_with_limit_2args() -> None:
    def prod_with_limit(a, n):
        return math.prod(i**2 for i in range(a, n))

    latex = (
        r"\mathrm{prod_with_limit}(a, n) = "
        r"\prod_{i = a}^{{n - 1}} \left({i^{{2}}}\right)"
    )
    _check_with_latex(prod_with_limit, latex)


def test_nested_function() -> None:
    def nested(x):
        return 3 * x

    _check_with_latex(nested, r"\mathrm{nested}(x) = {3}x")


def test_double_nested_function() -> None:
    def nested(x):
        def inner(y):
            return x * y

        return inner

    _check_with_latex(nested(3), r"\mathrm{inner}(y) = xy")


def test_use_raw_function_name() -> None:
    def foo_bar():
        return 42

    _check_with_latex(foo_bar, r"\mathrm{foo_bar}() = {42}")
    _check_with_latex(
        foo_bar,
        r"\mathrm{foo_bar}() = {42}",
        use_raw_function_name=False,
    )
    _check_with_latex(
        foo_bar,
        r"\mathrm{foo\_bar}() = {42}",
        use_raw_function_name=True,
    )


def test_reduce_assignments() -> None:
    def f(x):
        a = x + x
        return 3 * a

    _check_with_latex(
        f,
        r"\begin{array}{l} a = x + x \\ \mathrm{f}(x) = {3}a \end{array}",
    )
    _check_with_latex(f, r"\mathrm{f}(x) = {3}(x + x)", reduce_assignments=True)


def test_reduce_assignments_double() -> None:
    def f(x):
        a = x**2
        b = a + a
        return 3 * b

    latex_without_option = (
        r"\begin{array}{l} "
        r"a = x^{{2}} \\ "
        r"b = a + a \\ "
        r"\mathrm{f}(x) = {3}b "
        r"\end{array}"
    )

    _check_with_latex(f, latex_without_option)
    _check_with_latex(f, latex_without_option, reduce_assignments=False)
    _check_with_latex(
        f,
        r"\mathrm{f}(x) = {3}(x^{{2}} + x^{{2}})",
        reduce_assignments=True,
    )


def test_reduce_assignments_with_if() -> None:
    def sigmoid(x):
        p = 1 / (1 + math.exp(-x))
        n = math.exp(x) / (math.exp(x) + 1)
        if x > 0:
            return p
        else:
            return n

    _check_with_latex(
        sigmoid,
        (
            r"\mathrm{sigmoid}(x) = \left\{ \begin{array}{ll} "
            r"\frac{{1}}{{1} + \exp{\left({-x}\right)}}, & "
            r"\mathrm{if} \ {x > {0}} \\ "
            r"\frac{\exp{\left({x}\right)}}{\exp{\left({x}\right)} + {1}}, & "
            r"\mathrm{otherwise} "
            r"\end{array} \right."
        ),
        reduce_assignments=True,
    )
