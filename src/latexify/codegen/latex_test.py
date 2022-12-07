"""Tests for latexify.codegen.latex."""

from __future__ import annotations

# Ignores [22-imports] for convenience.
from latexify.codegen.latex import Latex


def test_eq() -> None:
    assert Latex("foo") == Latex("foo")
    assert Latex("foo") != "foo"
    assert Latex("foo") != Latex("bar")


def test_str() -> None:
    assert str(Latex("foo")) == "foo"


def test_add() -> None:
    assert Latex("foo") + "bar" == Latex("foobar")
    assert "foo" + Latex("bar") == Latex("foobar")
    assert Latex("foo") + Latex("bar") == Latex("foobar")


def test_opt() -> None:
    assert Latex.opt("foo") == Latex("[foo]")
    assert Latex.opt(Latex("foo")) == Latex("[foo]")


def test_arg() -> None:
    assert Latex.arg("foo") == Latex("{foo}")
    assert Latex.arg(Latex("foo")) == Latex("{foo}")


def test_paren() -> None:
    assert Latex.paren("foo") == Latex(r"\mathopen{}\left( foo \mathclose{}\right)")
    assert Latex.paren(Latex("foo")) == Latex(
        r"\mathopen{}\left( foo \mathclose{}\right)"
    )


def test_curly() -> None:
    assert Latex.curly("foo") == Latex(r"\mathopen{}\left\{ foo \mathclose{}\right\}")
    assert Latex.curly(Latex("foo")) == Latex(
        r"\mathopen{}\left\{ foo \mathclose{}\right\}"
    )


def test_square() -> None:
    assert Latex.square("foo") == Latex(r"\mathopen{}\left[ foo \mathclose{}\right]")
    assert Latex.square(Latex("foo")) == Latex(
        r"\mathopen{}\left[ foo \mathclose{}\right]"
    )


def test_command() -> None:
    assert Latex.command("a") == Latex(r"\a")
    assert Latex.command("a", options=[]) == Latex(r"\a")
    assert Latex.command("a", options=["b"]) == Latex(r"\a[b]")
    assert Latex.command("a", options=[Latex("b")]) == Latex(r"\a[b]")
    assert Latex.command("a", options=["b", "c"]) == Latex(r"\a[b][c]")
    assert Latex.command("a", args=[]) == Latex(r"\a")
    assert Latex.command("a", args=["b"]) == Latex(r"\a{b}")
    assert Latex.command("a", args=[Latex("b")]) == Latex(r"\a{b}")
    assert Latex.command("a", args=["b", "c"]) == Latex(r"\a{b}{c}")
    assert Latex.command("a", options=["b"], args=["c"]) == Latex(r"\a[b]{c}")


def test_environment() -> None:
    assert Latex.environment("a") == Latex(r"\begin{a} \end{a}")
    assert Latex.environment("a", options=[]) == Latex(r"\begin{a} \end{a}")
    assert Latex.environment("a", options=["b"]) == Latex(r"\begin{a}[b] \end{a}")
    assert Latex.environment("a", options=[Latex("b")]) == Latex(
        r"\begin{a}[b] \end{a}"
    )
    assert Latex.environment("a", options=["b", "c"]) == Latex(
        r"\begin{a}[b][c] \end{a}"
    )
    assert Latex.environment("a", args=[]) == Latex(r"\begin{a} \end{a}")
    assert Latex.environment("a", args=["b"]) == Latex(r"\begin{a}{b} \end{a}")
    assert Latex.environment("a", args=[Latex("b")]) == Latex(r"\begin{a}{b} \end{a}")
    assert Latex.environment("a", args=["b", "c"]) == Latex(r"\begin{a}{b}{c} \end{a}")
    assert Latex.environment("a", content="b") == Latex(r"\begin{a} b \end{a}")
    assert Latex.environment("a", content=Latex("b")) == Latex(r"\begin{a} b \end{a}")
    assert Latex.environment("a", options=["b"], args=["c"]) == Latex(
        r"\begin{a}[b]{c} \end{a}"
    )
    assert Latex.environment("a", options=["b"], content="c") == Latex(
        r"\begin{a}[b] c \end{a}"
    )
    assert Latex.environment("a", args=["b"], content="c") == Latex(
        r"\begin{a}{b} c \end{a}"
    )
    assert Latex.environment("a", options=["b"], args=["c"], content="d") == Latex(
        r"\begin{a}[b]{c} d \end{a}"
    )


def test_join() -> None:
    assert Latex.join(":", []) == Latex("")
    assert Latex.join(":", ["foo"]) == Latex("foo")
    assert Latex.join(":", [Latex("foo")]) == Latex("foo")
    assert Latex.join(":", [Latex("foo"), "bar"]) == Latex("foo:bar")
    assert Latex.join(":", ["foo", Latex("bar")]) == Latex("foo:bar")
    assert Latex.join(":", [Latex("foo"), Latex("bar")]) == Latex("foo:bar")
    assert Latex.join(":", ()) == Latex("")
    assert Latex.join(":", ("foo",)) == Latex("foo")
    assert Latex.join(":", (Latex("foo"),)) == Latex("foo")
    assert Latex.join(":", (Latex("foo"), "bar")) == Latex("foo:bar")
    assert Latex.join(":", ("foo", Latex("bar"))) == Latex("foo:bar")
    assert Latex.join(":", (Latex("foo"), Latex("bar"))) == Latex("foo:bar")
    assert Latex.join(":", (str(x) for x in range(3))) == Latex("0:1:2")
    assert Latex.join(":", (Latex(str(x)) for x in range(3))) == Latex("0:1:2")
