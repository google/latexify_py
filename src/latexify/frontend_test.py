"""Tests for latexify.frontend."""

from __future__ import annotations

from latexify import frontend


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
