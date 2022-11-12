"""Tests for latexify.frontend."""

from __future__ import annotations

from latexify import frontend


def test_get_latex_identifiers() -> None:
    def myfn(myvar):
        return 3 * myvar

    identifiers = {"myfn": "f", "myvar": "x"}

    latex_without_flag = r"\mathrm{myfn}(myvar) = {3} myvar"
    latex_with_flag = r"\mathrm{f}(x) = {3} x"

    assert frontend.get_latex(myfn) == latex_without_flag
    assert frontend.get_latex(myfn, identifiers=identifiers) == latex_with_flag


def test_get_latex_reduce_assignments() -> None:
    def f(x):
        y = 3 * x
        return y

    latex_without_flag = r"\begin{array}{l} y = {3} x \\ \mathrm{f}(x) = y \end{array}"
    latex_with_flag = r"\mathrm{f}(x) = {3} x"

    assert frontend.get_latex(f) == latex_without_flag
    assert frontend.get_latex(f, reduce_assignments=False) == latex_without_flag
    assert frontend.get_latex(f, reduce_assignments=True) == latex_with_flag


def test_get_latex_use_math_symbols() -> None:
    def f(alpha):
        return alpha

    latex_without_flag = r"\mathrm{f}(alpha) = alpha"
    latex_with_flag = r"\mathrm{f}({\alpha}) = {\alpha}"

    assert frontend.get_latex(f) == latex_without_flag
    assert frontend.get_latex(f, use_math_symbols=False) == latex_without_flag
    assert frontend.get_latex(f, use_math_symbols=True) == latex_with_flag


def test_get_latex_use_raw_function_name() -> None:
    def foo_bar(x):
        return x

    latex_without_flag = r"\mathrm{foo_bar}(x) = x"
    latex_with_flag = r"\mathrm{foo\_bar}(x) = x"

    assert frontend.get_latex(foo_bar) == latex_without_flag
    assert (
        frontend.get_latex(foo_bar, use_raw_function_name=False) == latex_without_flag
    )
    assert frontend.get_latex(foo_bar, use_raw_function_name=True) == latex_with_flag


def test_get_latex_use_signature() -> None:
    def f(x):
        return x

    latex_without_flag = "x"
    latex_with_flag = r"\mathrm{f}(x) = x"

    assert frontend.get_latex(f) == latex_with_flag
    assert frontend.get_latex(f, use_signature=False) == latex_without_flag
    assert frontend.get_latex(f, use_signature=True) == latex_with_flag


def test_function() -> None:
    def f(x):
        return x

    latex_without_flag = "x"
    latex_with_flag = r"\mathrm{f}(x) = x"

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
    latex_with_flag = r"\mathrm{f}(x) = x"

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
