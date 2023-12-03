"""Tests for latexify.generate_latex."""

from __future__ import annotations

from latexify import generate_latex


def test_get_latex_identifiers() -> None:
    def myfn(myvar):
        return 3 * myvar

    identifiers = {"myfn": "f", "myvar": "x"}

    latex_without_flag = r"\mathrm{myfn}(\mathrm{myvar}) = 3 \mathrm{myvar}"
    latex_with_flag = r"f(x) = 3 x"

    assert generate_latex.get_latex(myfn) == latex_without_flag
    assert generate_latex.get_latex(myfn, identifiers=identifiers) == latex_with_flag


def test_get_latex_prefixes() -> None:
    abc = object()

    def f(x):
        return abc.d + x.y.z.e

    latex_without_flag = r"f(x) = \mathrm{abc}.d + x.y.z.e"
    latex_with_flag1 = r"f(x) = d + x.y.z.e"
    latex_with_flag2 = r"f(x) = \mathrm{abc}.d + y.z.e"
    latex_with_flag3 = r"f(x) = \mathrm{abc}.d + z.e"
    latex_with_flag4 = r"f(x) = d + e"

    assert generate_latex.get_latex(f) == latex_without_flag
    assert generate_latex.get_latex(f, prefixes=set()) == latex_without_flag
    assert generate_latex.get_latex(f, prefixes={"abc"}) == latex_with_flag1
    assert generate_latex.get_latex(f, prefixes={"x"}) == latex_with_flag2
    assert generate_latex.get_latex(f, prefixes={"x.y"}) == latex_with_flag3
    assert generate_latex.get_latex(f, prefixes={"abc", "x.y.z"}) == latex_with_flag4
    assert (
        generate_latex.get_latex(f, prefixes={"abc", "x", "x.y.z"}) == latex_with_flag4
    )


def test_get_latex_reduce_assignments() -> None:
    def f(x):
        y = 3 * x
        return y

    latex_without_flag = r"\begin{array}{l} y = 3 x \\ f(x) = y \end{array}"
    latex_with_flag = r"f(x) = 3 x"

    assert generate_latex.get_latex(f) == latex_without_flag
    assert generate_latex.get_latex(f, reduce_assignments=False) == latex_without_flag
    assert generate_latex.get_latex(f, reduce_assignments=True) == latex_with_flag


def test_get_latex_reduce_assignments_with_docstring() -> None:
    def f(x):
        """DocstringRemover is required."""
        y = 3 * x
        return y

    latex_without_flag = r"\begin{array}{l} y = 3 x \\ f(x) = y \end{array}"
    latex_with_flag = r"f(x) = 3 x"

    assert generate_latex.get_latex(f) == latex_without_flag
    assert generate_latex.get_latex(f, reduce_assignments=False) == latex_without_flag
    assert generate_latex.get_latex(f, reduce_assignments=True) == latex_with_flag


def test_get_latex_reduce_assignments_with_aug_assign() -> None:
    def f(x):
        y = 3
        y *= x
        return y

    latex_without_flag = r"\begin{array}{l} y = 3 \\ y = y x \\ f(x) = y \end{array}"
    latex_with_flag = r"f(x) = 3 x"

    assert generate_latex.get_latex(f) == latex_without_flag
    assert generate_latex.get_latex(f, reduce_assignments=False) == latex_without_flag
    assert generate_latex.get_latex(f, reduce_assignments=True) == latex_with_flag


def test_get_latex_use_math_symbols() -> None:
    def f(alpha):
        return alpha

    latex_without_flag = r"f(\mathrm{alpha}) = \mathrm{alpha}"
    latex_with_flag = r"f(\alpha) = \alpha"

    assert generate_latex.get_latex(f) == latex_without_flag
    assert generate_latex.get_latex(f, use_math_symbols=False) == latex_without_flag
    assert generate_latex.get_latex(f, use_math_symbols=True) == latex_with_flag


def test_get_latex_use_signature() -> None:
    def f(x):
        return x

    latex_without_flag = "x"
    latex_with_flag = r"f(x) = x"

    assert generate_latex.get_latex(f) == latex_with_flag
    assert generate_latex.get_latex(f, use_signature=False) == latex_without_flag
    assert generate_latex.get_latex(f, use_signature=True) == latex_with_flag


def test_get_latex_use_set_symbols() -> None:
    def f(x, y):
        return x & y

    latex_without_flag = r"f(x, y) = x \mathbin{\&} y"
    latex_with_flag = r"f(x, y) = x \cap y"

    assert generate_latex.get_latex(f) == latex_without_flag
    assert generate_latex.get_latex(f, use_set_symbols=False) == latex_without_flag
    assert generate_latex.get_latex(f, use_set_symbols=True) == latex_with_flag
