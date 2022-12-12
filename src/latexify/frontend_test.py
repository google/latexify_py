"""Tests for latexify.frontend."""

from __future__ import annotations

from latexify import frontend


def test_get_latex_identifiers() -> None:
    def myfn(myvar):
        return 3 * myvar

    identifiers = {"myfn": "f", "myvar": "x"}

    latex_without_flag = r"\mathrm{myfn}(\mathrm{myvar}) = 3 \mathrm{myvar}"
    latex_with_flag = r"f(x) = 3 x"

    assert frontend.get_latex(myfn) == latex_without_flag
    assert frontend.get_latex(myfn, identifiers=identifiers) == latex_with_flag


def test_get_latex_prefixes() -> None:
    abc = object()

    def f(x):
        return abc.d + x.y.z.e

    latex_without_flag = r"f(x) = \mathrm{abc}.d + x.y.z.e"
    latex_with_flag1 = r"f(x) = d + x.y.z.e"
    latex_with_flag2 = r"f(x) = \mathrm{abc}.d + y.z.e"
    latex_with_flag3 = r"f(x) = \mathrm{abc}.d + z.e"
    latex_with_flag4 = r"f(x) = d + e"

    assert frontend.get_latex(f) == latex_without_flag
    assert frontend.get_latex(f, prefixes=set()) == latex_without_flag
    assert frontend.get_latex(f, prefixes={"abc"}) == latex_with_flag1
    assert frontend.get_latex(f, prefixes={"x"}) == latex_with_flag2
    assert frontend.get_latex(f, prefixes={"x.y"}) == latex_with_flag3
    assert frontend.get_latex(f, prefixes={"abc", "x.y.z"}) == latex_with_flag4
    assert frontend.get_latex(f, prefixes={"abc", "x", "x.y.z"}) == latex_with_flag4


def test_get_latex_reduce_assignments() -> None:
    def f(x):
        y = 3 * x
        return y

    latex_without_flag = r"\begin{array}{l} y = 3 x \\ f(x) = y \end{array}"
    latex_with_flag = r"f(x) = 3 x"

    assert frontend.get_latex(f) == latex_without_flag
    assert frontend.get_latex(f, reduce_assignments=False) == latex_without_flag
    assert frontend.get_latex(f, reduce_assignments=True) == latex_with_flag


def test_get_latex_use_math_symbols() -> None:
    def f(alpha):
        return alpha

    latex_without_flag = r"f(\mathrm{alpha}) = \mathrm{alpha}"
    latex_with_flag = r"f(\alpha) = \alpha"

    assert frontend.get_latex(f) == latex_without_flag
    assert frontend.get_latex(f, use_math_symbols=False) == latex_without_flag
    assert frontend.get_latex(f, use_math_symbols=True) == latex_with_flag


def test_get_latex_use_signature() -> None:
    def f(x):
        return x

    latex_without_flag = "x"
    latex_with_flag = r"f(x) = x"

    assert frontend.get_latex(f) == latex_with_flag
    assert frontend.get_latex(f, use_signature=False) == latex_without_flag
    assert frontend.get_latex(f, use_signature=True) == latex_with_flag


def test_get_latex_use_set_symbols() -> None:
    def f(x, y):
        return x & y

    latex_without_flag = r"f(x, y) = x \mathbin{\&} y"
    latex_with_flag = r"f(x, y) = x \cap y"

    assert frontend.get_latex(f) == latex_without_flag
    assert frontend.get_latex(f, use_set_symbols=False) == latex_without_flag
    assert frontend.get_latex(f, use_set_symbols=True) == latex_with_flag


def test_function() -> None:
    def f(x):
        return x

    latex_without_flag = "x"
    latex_with_flag = r"f(x) = x"

    # Checks the syntax:
    #     @function
    #     def fn(...):
    #         ...
    latexified = frontend.function(f)
    assert str(latexified) == latex_with_flag
    assert latexified._repr_latex_() == rf"$$ \displaystyle {latex_with_flag} $$"

    # Checks the syntax:
    #     @function(**kwargs)
    #     def fn(...):
    #         ...
    latexified = frontend.function(use_signature=False)(f)
    assert str(latexified) == latex_without_flag
    assert latexified._repr_latex_() == rf"$$ \displaystyle {latex_without_flag} $$"

    # Checks the syntax:
    #     def fn(...):
    #         ...
    #     latexified = function(fn, **kwargs)
    latexified = frontend.function(f, use_signature=False)
    assert str(latexified) == latex_without_flag
    assert latexified._repr_latex_() == rf"$$ \displaystyle {latex_without_flag} $$"


def test_expression() -> None:
    def f(x):
        return x

    latex_without_flag = "x"
    latex_with_flag = r"f(x) = x"

    # Checks the syntax:
    #     @expression
    #     def fn(...):
    #         ...
    latexified = frontend.expression(f)
    assert str(latexified) == latex_without_flag
    assert latexified._repr_latex_() == rf"$$ \displaystyle {latex_without_flag} $$"

    # Checks the syntax:
    #     @expression(**kwargs)
    #     def fn(...):
    #         ...
    latexified = frontend.expression(use_signature=True)(f)
    assert str(latexified) == latex_with_flag
    assert latexified._repr_latex_() == rf"$$ \displaystyle {latex_with_flag} $$"

    # Checks the syntax:
    #     def fn(...):
    #         ...
    #     latexified = expression(fn, **kwargs)
    latexified = frontend.expression(f, use_signature=True)
    assert str(latexified) == latex_with_flag
    assert latexified._repr_latex_() == rf"$$ \displaystyle {latex_with_flag} $$"
