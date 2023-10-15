"""End-to-end test cases of function."""

from __future__ import annotations

import math

from integration_tests import integration_utils


def test_quadratic_solution() -> None:
    def solve(a, b, c):
        return (-b + math.sqrt(b**2 - 4 * a * c)) / (2 * a)

    latex = r"\mathrm{solve}(a, b, c) =" r" \frac{-b + \sqrt{ b^{2} - 4 a c }}{2 a}"
    integration_utils.check_function(solve, latex)


def test_sinc() -> None:
    def sinc(x):
        if x == 0:
            return 1
        else:
            return math.sin(x) / x

    latex = (
        r"\mathrm{sinc}(x) ="
        r" \left\{ \begin{array}{ll}"
        r" 1, & \mathrm{if} \ x = 0 \\"
        r" \frac{\sin x}{x}, & \mathrm{otherwise}"
        r" \end{array} \right."
    )
    integration_utils.check_function(sinc, latex)


def test_x_times_beta() -> None:
    def xtimesbeta(x, beta):
        return x * beta

    latex_without_symbols = (
        r"\mathrm{xtimesbeta}(x, \mathrm{beta}) = x \cdot \mathrm{beta}"
    )
    integration_utils.check_function(xtimesbeta, latex_without_symbols)
    integration_utils.check_function(
        xtimesbeta, latex_without_symbols, use_math_symbols=False
    )

    latex_with_symbols = r"\mathrm{xtimesbeta}(x, \beta) = x \beta"
    integration_utils.check_function(
        xtimesbeta, latex_with_symbols, use_math_symbols=True
    )


def test_sum_with_limit_1arg() -> None:
    def sum_with_limit(n):
        return sum(i**2 for i in range(n))

    latex = (
        r"\mathrm{sum\_with\_limit}(n) = \sum_{i = 0}^{n - 1}"
        r" \mathopen{}\left({i^{2}}\mathclose{}\right)"
    )
    integration_utils.check_function(sum_with_limit, latex)


def test_sum_with_limit_2args() -> None:
    def sum_with_limit(a, n):
        return sum(i**2 for i in range(a, n))

    latex = (
        r"\mathrm{sum\_with\_limit}(a, n) = \sum_{i = a}^{n - 1}"
        r" \mathopen{}\left({i^{2}}\mathclose{}\right)"
    )
    integration_utils.check_function(sum_with_limit, latex)


def test_sum_with_reducible_limit() -> None:
    def sum_with_limit(n):
        return sum(i for i in range(n + 1))

    latex = (
        r"\mathrm{sum\_with\_limit}(n) = \sum_{i = 0}^{n}"
        r" \mathopen{}\left({i}\mathclose{}\right)"
    )
    integration_utils.check_function(sum_with_limit, latex)


def test_sum_with_irreducible_limit() -> None:
    def sum_with_limit(n):
        return sum(i for i in range(n * 3))

    latex = (
        r"\mathrm{sum\_with\_limit}(n) = \sum_{i = 0}^{n \cdot 3 - 1}"
        r" \mathopen{}\left({i}\mathclose{}\right)"
    )
    integration_utils.check_function(sum_with_limit, latex)


def test_prod_with_limit_1arg() -> None:
    def prod_with_limit(n):
        return math.prod(i**2 for i in range(n))

    latex = (
        r"\mathrm{prod\_with\_limit}(n) ="
        r" \prod_{i = 0}^{n - 1} \mathopen{}\left({i^{2}}\mathclose{}\right)"
    )
    integration_utils.check_function(prod_with_limit, latex)


def test_prod_with_limit_2args() -> None:
    def prod_with_limit(a, n):
        return math.prod(i**2 for i in range(a, n))

    latex = (
        r"\mathrm{prod\_with\_limit}(a, n) ="
        r" \prod_{i = a}^{n - 1} \mathopen{}\left({i^{2}}\mathclose{}\right)"
    )
    integration_utils.check_function(prod_with_limit, latex)


def test_prod_with_reducible_limits() -> None:
    def prod_with_limit(n):
        return math.prod(i for i in range(n - 1))

    latex = (
        r"\mathrm{prod\_with\_limit}(n) ="
        r" \prod_{i = 0}^{n - 2} \mathopen{}\left({i}\mathclose{}\right)"
    )
    integration_utils.check_function(prod_with_limit, latex)


def test_prod_with_irreducible_limit() -> None:
    def prod_with_limit(n):
        return math.prod(i for i in range(n * 3))

    latex = (
        r"\mathrm{prod\_with\_limit}(n) = "
        r"\prod_{i = 0}^{n \cdot 3 - 1} \mathopen{}\left({i}\mathclose{}\right)"
    )
    integration_utils.check_function(prod_with_limit, latex)


def test_nested_function() -> None:
    def nested(x):
        return 3 * x

    integration_utils.check_function(nested, r"\mathrm{nested}(x) = 3 x")


def test_double_nested_function() -> None:
    def nested(x):
        def inner(y):
            return x * y

        return inner

    integration_utils.check_function(nested(3), r"\mathrm{inner}(y) = x y")


def test_reduce_assignments() -> None:
    def f(x):
        a = x + x
        return 3 * a

    integration_utils.check_function(
        f,
        r"\begin{array}{l} a = x + x \\ f(x) = 3 a \end{array}",
    )
    integration_utils.check_function(
        f,
        r"f(x) = 3 \mathopen{}\left( x + x \mathclose{}\right)",
        reduce_assignments=True,
    )


def test_reduce_assignments_double() -> None:
    def f(x):
        a = x**2
        b = a + a
        return 3 * b

    latex_without_option = (
        r"\begin{array}{l}"
        r" a = x^{2} \\"
        r" b = a + a \\"
        r" f(x) = 3 b"
        r" \end{array}"
    )

    integration_utils.check_function(f, latex_without_option)
    integration_utils.check_function(f, latex_without_option, reduce_assignments=False)
    integration_utils.check_function(
        f,
        r"f(x) = 3 \mathopen{}\left( x^{2} + x^{2} \mathclose{}\right)",
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

    integration_utils.check_function(
        sigmoid,
        (
            r"\mathrm{sigmoid}(x) = \left\{ \begin{array}{ll}"
            r" \frac{1}{1 + \exp \mathopen{}\left( -x \mathclose{}\right)}, &"
            r" \mathrm{if} \ x > 0 \\"
            r" \frac{\exp x}{\exp x + 1}, &"
            r" \mathrm{otherwise}"
            r" \end{array} \right."
        ),
        reduce_assignments=True,
    )


def test_sub_bracket() -> None:
    def solve(a, b):
        return ((a + b) - b) / (a - b) - (a + b) - (a - b) - (a * b)

    latex = (
        r"\mathrm{solve}(a, b) ="
        r" \frac{a + b - b}{a - b} - \mathopen{}\left("
        r" a + b \mathclose{}\right) - \mathopen{}\left("
        r" a - b \mathclose{}\right) - a b"
    )
    integration_utils.check_function(solve, latex)


def test_docstring_allowed() -> None:
    def solve(x):
        """The identity function."""
        return x

    latex = r"\mathrm{solve}(x) = x"
    integration_utils.check_function(solve, latex)


def test_multiple_constants_allowed() -> None:
    def solve(x):
        """The identity function."""
        123
        True
        return x

    latex = r"\mathrm{solve}(x) = x"
    integration_utils.check_function(solve, latex)
