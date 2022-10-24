# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Test IO of with_latex."""

import math
import pytest

from latexify import get_latex, with_latex


def solve(a, b, c):
    return (-b + math.sqrt(b**2 - 4 * a * c)) / (2 * a)


solve_latex = (
    r"\mathrm{solve}(a, b, c) \triangleq " r"\frac{-b + \sqrt{b^{2} - 4ac}}{2a}"
)


def sinc(x):
    # pylint: disable=no-else-return
    if x == 0:
        return 1
    else:
        return math.sin(x) / x


sinc_latex = (
    r"\mathrm{sinc}(x) \triangleq \left\{ \begin{array}{ll} 1, & \mathrm{if} \ "
    r"{x = 0} \\ \frac{\sin{\left({x}\right)}}{x}, & \mathrm{otherwise} \end{array}"
    r" \right."
)


def xtimesbeta(x, beta):
    return x * beta


xtimesbeta_latex = r"\mathrm{xtimesbeta}(x, {\beta}) \triangleq x{\beta}"
xtimesbeta_latex_no_symbols = r"\mathrm{xtimesbeta}(x, beta) \triangleq xbeta"


def sum_with_limit(n):
    return sum(i**2 for i in range(n))


sum_with_limit_latex = (
    r"\mathrm{sum_with_limit}(n) \triangleq \sum_{i=0}^{n-1} \left({i^{2}}\right)"
)


def sum_with_limit_two_args(a, n):
    return sum(i**2 for i in range(a, n))


sum_with_limit_two_args_latex = (
    r"\mathrm{sum_with_limit_two_args}(a, n) "
    r"\triangleq \sum_{i=a}^{n-1} \left({i^{2}}\right)"
)


@pytest.mark.parametrize(
    "func, expected_latex, use_math_symbols",
    [
        (solve, solve_latex, None),
        (sinc, sinc_latex, None),
        (xtimesbeta, xtimesbeta_latex, True),
        (xtimesbeta, xtimesbeta_latex_no_symbols, False),
        (sum_with_limit, sum_with_limit_latex, None),
        (sum_with_limit_two_args, sum_with_limit_two_args_latex, None),
    ],
)
def test_with_latex_to_str(func, expected_latex, use_math_symbols):
    """Test with_latex to str."""
    if use_math_symbols is None:
        latexified_function = with_latex(func)
    else:
        latexified_function = with_latex(use_math_symbols=use_math_symbols)(func)
    assert str(latexified_function) == expected_latex
    expected_repr = r"$$ \displaystyle %s $$" % expected_latex
    assert latexified_function._repr_latex_() == expected_repr


def test_nested_function():
    def nested(x):
        return 3 * x

    assert get_latex(nested) == r"\mathrm{nested}(x) \triangleq 3x"


def test_double_nested_function():
    def nested(x):
        def inner(y):
            return x * y

        return inner

    assert get_latex(nested(3)) == r"\mathrm{inner}(y) \triangleq xy"


def test_use_raw_function_name():
    def foo_bar():
        return 42

    assert str(with_latex(foo_bar)) == r"\mathrm{foo_bar}() \triangleq 42"
    assert (
        str(with_latex(foo_bar, use_raw_function_name=True))
        == r"\mathrm{foo\_bar}() \triangleq 42"
    )
    assert (
        str(with_latex(use_raw_function_name=True)(foo_bar))
        == r"\mathrm{foo\_bar}() \triangleq 42"
    )


def test_reduce_assignments():
    def f(x):
        a = x + x
        return 3 * a

    assert str(with_latex(f)) == r"a \triangleq x + x \\ \mathrm{f}(x) \triangleq 3a"

    latex_with_option = r"\mathrm{f}(x) \triangleq 3\left( x + x \right)"
    assert str(with_latex(f, reduce_assignments=True)) == latex_with_option
    assert str(with_latex(reduce_assignments=True)(f)) == latex_with_option


def test_reduce_assignments_double():
    def f(x):
        a = x**2
        b = a + a
        return 3 * b

    assert str(with_latex(f)) == (
        r"a \triangleq x^{2} \\ b \triangleq a + a \\ \mathrm{f}(x) \triangleq 3b"
    )

    latex_with_option = (
        r"\mathrm{f}(x) \triangleq "
        r"3\left( \left( x^{2} \right) + \left( x^{2} \right) \right)"
    )
    assert str(with_latex(f, reduce_assignments=True)) == latex_with_option
    assert str(with_latex(reduce_assignments=True)(f)) == latex_with_option
