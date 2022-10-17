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
    r"x=0 \\ \frac{\sin{\left({x}\right)}}{x}, & \mathrm{otherwise} \end{array}"
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


func_and_latex_str_list = [
    (solve, solve_latex, None),
    (sinc, sinc_latex, None),
    (xtimesbeta, xtimesbeta_latex, True),
    (xtimesbeta, xtimesbeta_latex_no_symbols, False),
    (sum_with_limit, sum_with_limit_latex, None),
    (sum_with_limit_two_args, sum_with_limit_two_args_latex, None),
]


@pytest.mark.parametrize("func, expected_latex, math_symbol", func_and_latex_str_list)
def test_with_latex_to_str(func, expected_latex, math_symbol):
    """Test with_latex to str."""
    # pylint: disable=protected-access
    if math_symbol is None:
        latexified_function = with_latex(func)
    else:
        latexified_function = with_latex(math_symbol=math_symbol)(func)
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


def test_assign_feature():
    @with_latex
    def f(x):
        return abs(x) * math.exp(math.sqrt(x))

    @with_latex
    def g(x):
        a = abs(x)
        b = math.exp(math.sqrt(x))
        return a * b

    @with_latex(reduce_assignments=False)
    def h(x):
        a = abs(x)
        b = math.exp(math.sqrt(x))
        return a * b

    assert str(f) == r"\mathrm{f}(x) \triangleq \left|{x}\right|\exp{\left({\sqrt{x}}\right)}"
    assert str(g) == r"\mathrm{g}(x) \triangleq \left( \left|{x}\right| \right)\left( \exp{\left({\sqrt{x}}\right)} \right)"
    assert str(h) == r"a \triangleq \left|{x}\right| \\ b \triangleq \exp{\left({\sqrt{x}}\right)} \\ \mathrm{h}(x) \triangleq ab"

    @with_latex(reduce_assignments=True)
    def f(x):
        a = math.sqrt(math.exp(x))
        return abs(x) * math.log10(a)

    assert str(f) == r"\mathrm{f}(x) \triangleq \left|{x}\right|\log_{10}{\left({\left( \sqrt{\exp{\left({x}\right)}} \right)}\right)}"

    @with_latex(reduce_assignments=False)
    def f(x):
        a = math.sqrt(math.exp(x))
        return abs(x) * math.log10(a)

    assert str(f) == r"a \triangleq \sqrt{\exp{\left({x}\right)}} \\ \mathrm{f}(x) \triangleq \left|{x}\right|\log_{10}{\left({a}\right)}"
