import math

from integration_tests import utils


def test_expand_atan2_function() -> None:
    def solve(x, y):
        return math.atan2(y, x)

    latex = r"\mathrm{solve}(x, y) = \arctan{\left({\frac{y}{x}}\right)}"
    utils.check_function(solve, latex, expand_functions={"atan2"})


def test_expand_atan2_nested_function() -> None:
    def solve(x, y):
        return math.atan2(math.exp(y), math.exp(x))

    latex = r"\mathrm{solve}(x, y) = \arctan{\left({\frac{e^{y}}{e^{x}}}\right)}"
    utils.check_function(solve, latex, expand_functions={"atan2", "exp"})


def test_expand_exp_function() -> None:
    def solve(x):
        return math.exp(x)

    latex = r"\mathrm{solve}(x) = e^{x}"
    utils.check_function(solve, latex, expand_functions={"exp"})


def test_expand_exp_nested_function() -> None:
    def solve(x):
        return math.exp(math.exp(x))

    latex = r"\mathrm{solve}(x) = e^{e^{x}}"
    utils.check_function(solve, latex, expand_functions={"exp"})


def test_expand_exp2_function() -> None:
    def solve(x):
        return math.exp2(x)

    latex = r"\mathrm{solve}(x) = {2}^{x}"
    utils.check_function(solve, latex, expand_functions={"exp2"})


def test_expand_exp2_nested_function() -> None:
    def solve(x):
        return math.exp2(math.exp2(x))

    latex = r"\mathrm{solve}(x) = {2}^{{2}^{x}}"
    utils.check_function(solve, latex, expand_functions={"exp2"})


def test_expand_expm1_function() -> None:
    def solve(x):
        return math.expm1(x)

    latex = r"\mathrm{solve}(x) = \exp{\left({x}\right)} - {1}"
    utils.check_function(solve, latex, expand_functions={"expm1"})


def test_expand_expm1_nested_function() -> None:
    def solve(x, y, z):
        return math.expm1(math.pow(y, z))

    latex = r"\mathrm{solve}(x, y, z) = e^{y^{z}} - {1}"
    utils.check_function(solve, latex, expand_functions={"expm1", "exp", "pow"})


def test_expand_hypot_function_without_attribute_access() -> None:
    from math import hypot

    def solve(x, y, z):
        return hypot(x, y, z)

    latex = r"\mathrm{solve}(x, y, z) = \sqrt{x^{{2}} + y^{{2}} + z^{{2}}}"
    utils.check_function(solve, latex, expand_functions={"hypot"})


def test_expand_hypot_function() -> None:
    def solve(x, y, z):
        return math.hypot(x, y, z)

    latex = r"\mathrm{solve}(x, y, z) = \sqrt{x^{{2}} + y^{{2}} + z^{{2}}}"
    utils.check_function(solve, latex, expand_functions={"hypot"})


def test_expand_hypot_nested_function() -> None:
    def solve(a, b, x, y):
        return math.hypot(math.hypot(a, b), x, y)

    latex = (
        r"\mathrm{solve}(a, b, x, y) = "
        r"\sqrt{"
        r"\sqrt{a^{{2}} + b^{{2}}}^{{2}} + "
        r"x^{{2}} + y^{{2}}}"
    )
    utils.check_function(solve, latex, expand_functions={"hypot"})


def test_expand_log1p_function() -> None:
    def solve(x):
        return math.log1p(x)

    latex = r"\mathrm{solve}(x) = \log{\left({{1} + x}\right)}"
    utils.check_function(solve, latex, expand_functions={"log1p"})


def test_expand_log1p_nested_function() -> None:
    def solve(x):
        return math.log1p(math.exp(x))

    latex = r"\mathrm{solve}(x) = \log{\left({{1} + e^{x}}\right)}"
    utils.check_function(solve, latex, expand_functions={"log1p", "exp"})


def test_expand_pow_nested_function() -> None:
    def solve(w, x, y, z):
        return math.pow(math.pow(w, x), math.pow(y, z))

    latex = (
        r"\mathrm{solve}(w, x, y, z) = "
        r"\mathopen{}\left( w^{x} \mathclose{}\right)^{y^{z}}"
    )
    utils.check_function(solve, latex, expand_functions={"pow"})


def test_expand_pow_function() -> None:
    def solve(x, y):
        return math.pow(x, y)

    latex = r"\mathrm{solve}(x, y) = x^{y}"
    utils.check_function(solve, latex, expand_functions={"pow"})
