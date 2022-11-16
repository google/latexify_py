"""End-to-end test cases of function."""

from __future__ import annotations

from collections.abc import Callable
import math
from typing import Any

from latexify import frontend


def _check_function(
    fn: Callable[..., Any],
    latex: str,
    **kwargs,
) -> None:
    """Helper to check if the obtained function has the expected LaTeX form.

    Args:
        fn: Function to check.
        latex: LaTeX form of `fn`.
        **kwargs: Arguments passed to `frontend.function`.
    """
    # Checks the syntax:
    #     @function
    #     def fn(...):
    #         ...
    if not kwargs:
        latexified = frontend.function(fn)
        assert str(latexified) == latex
        assert latexified._repr_latex_() == rf"$$ \displaystyle {latex} $$"

    # Checks the syntax:
    #     @function(**kwargs)
    #     def fn(...):
    #         ...
    latexified = frontend.function(**kwargs)(fn)
    assert str(latexified) == latex
    assert latexified._repr_latex_() == rf"$$ \displaystyle {latex} $$"

    # Checks the syntax:
    #     def fn(...):
    #         ...
    #     latexified = function(fn, **kwargs)
    latexified = frontend.function(fn, **kwargs)
    assert str(latexified) == latex
    assert latexified._repr_latex_() == rf"$$ \displaystyle {latex} $$"


def test_quadratic_solution() -> None:
    def solve(a, b, c):
        return (-b + math.sqrt(b**2 - 4 * a * c)) / (2 * a)

    latex = r"\mathrm{solve}(a, b, c) = \frac{-b + \sqrt{b^{{2}} - {4} a c}}{{2} a}"
    _check_function(solve, latex)


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
    _check_function(sinc, latex)


def test_x_times_beta() -> None:
    def xtimesbeta(x, beta):
        return x * beta

    latex_without_symbols = r"\mathrm{xtimesbeta}(x, beta) = x beta"
    _check_function(xtimesbeta, latex_without_symbols)
    _check_function(xtimesbeta, latex_without_symbols, use_math_symbols=False)

    latex_with_symbols = r"\mathrm{xtimesbeta}(x, {\beta}) = x {\beta}"
    _check_function(xtimesbeta, latex_with_symbols, use_math_symbols=True)


def test_sum_with_limit_1arg() -> None:
    def sum_with_limit(n):
        return sum(i**2 for i in range(n))

    latex = (
        r"\mathrm{sum_with_limit}(n) = \sum_{i = {0}}^{{n - 1}}"
        r" \mathopen{}\left({i^{{2}}}\mathclose{}\right)"
    )
    _check_function(sum_with_limit, latex)


def test_sum_with_limit_2args() -> None:
    def sum_with_limit(a, n):
        return sum(i**2 for i in range(a, n))

    latex = (
        r"\mathrm{sum_with_limit}(a, n) = \sum_{i = a}^{{n - 1}} "
        r"\mathopen{}\left({i^{{2}}}\mathclose{}\right)"
    )
    _check_function(sum_with_limit, latex)


def test_sum_with_reducible_limit() -> None:
    def sum_with_limit(n):
        return sum(i for i in range(n + 1))

    latex = r"\mathrm{sum_with_limit}(n) = \sum_{i = {0}}^{{n}} \left({i}\right)"
    _check_function(sum_with_limit, latex)


def test_sum_with_irreducible_limit() -> None:
    def sum_with_limit(n):
        return sum(i for i in range(n * 3))

    latex = (
        r"\mathrm{sum_with_limit}(n) = \sum_{i = {0}}^{{n {3} - 1}} \left({i}\right)"
    )
    _check_function(sum_with_limit, latex)


def test_prod_with_limit_1arg() -> None:
    def prod_with_limit(n):
        return math.prod(i**2 for i in range(n))

    latex = (
        r"\mathrm{prod_with_limit}(n) = "
        r"\prod_{i = {0}}^{{n - 1}} \mathopen{}\left({i^{{2}}}\mathclose{}\right)"
    )
    _check_function(prod_with_limit, latex)


def test_prod_with_limit_2args() -> None:
    def prod_with_limit(a, n):
        return math.prod(i**2 for i in range(a, n))

    latex = (
        r"\mathrm{prod_with_limit}(a, n) = "
        r"\prod_{i = a}^{{n - 1}} \mathopen{}\left({i^{{2}}}\mathclose{}\right)"
    )
    _check_function(prod_with_limit, latex)


def test_prod_with_reducible_limits() -> None:
    def prod_with_limit(n):
        return math.prod(i for i in range(n - 1))

    latex = (
        r"\mathrm{prod_with_limit}(n) = "
        r"\prod_{i = {0}}^{{n - {2}}} \left({i}\right)"
    )
    _check_function(prod_with_limit, latex)


def test_prod_with_irreducible_limit() -> None:
    def prod_with_limit(n):
        return math.prod(i for i in range(n * 3))

    latex = (
        r"\mathrm{prod_with_limit}(n) = "
        r"\prod_{i = {0}}^{{n {3} - 1}} \left({i}\right)"
    )
    _check_function(prod_with_limit, latex)


def test_nested_function() -> None:
    def nested(x):
        return 3 * x

    _check_function(nested, r"\mathrm{nested}(x) = {3} x")


def test_double_nested_function() -> None:
    def nested(x):
        def inner(y):
            return x * y

        return inner

    _check_function(nested(3), r"\mathrm{inner}(y) = x y")


def test_use_raw_function_name() -> None:
    def foo_bar():
        return 42

    _check_function(foo_bar, r"\mathrm{foo_bar}() = {42}")
    _check_function(
        foo_bar,
        r"\mathrm{foo_bar}() = {42}",
        use_raw_function_name=False,
    )
    _check_function(
        foo_bar,
        r"\mathrm{foo\_bar}() = {42}",
        use_raw_function_name=True,
    )


def test_reduce_assignments() -> None:
    def f(x):
        a = x + x
        return 3 * a

    _check_function(
        f,
        r"\begin{array}{l} a = x + x \\ \mathrm{f}(x) = {3} a \end{array}",
    )
    _check_function(
        f,
        r"\mathrm{f}(x) = {3} \mathopen{}\left( x + x \mathclose{}\right)",
        reduce_assignments=True,
    )


def test_reduce_assignments_double() -> None:
    def f(x):
        a = x**2
        b = a + a
        return 3 * b

    latex_without_option = (
        r"\begin{array}{l} "
        r"a = x^{{2}} \\ "
        r"b = a + a \\ "
        r"\mathrm{f}(x) = {3} b "
        r"\end{array}"
    )

    _check_function(f, latex_without_option)
    _check_function(f, latex_without_option, reduce_assignments=False)
    _check_function(
        f,
        r"\mathrm{f}(x) = {3} \mathopen{}\left( x^{{2}} + x^{{2}} \mathclose{}\right)",
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

    _check_function(
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


def test_sub_bracket() -> None:
    def solve(a, b):
        return ((a + b) - b) / (a - b) - (a + b) - (a - b) - (a * b)

    latex = (
        r"\mathrm{solve}(a, b) = "
        r"\frac{a + b - b}{a - b} - \mathopen{}\left( "
        r"a + b \mathclose{}\right) - \mathopen{}\left( "
        r"a - b \mathclose{}\right) - a b"
    )
    _check_function(solve, latex)
