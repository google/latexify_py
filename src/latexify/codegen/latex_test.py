"""Tests for latexify.codegen.latex."""

from __future__ import annotations

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


def test_wrap() -> None:
    assert Latex("foo").wrap() == Latex("{foo}")


def test_paren() -> None:
    assert Latex("foo").paren() == Latex(r"\mathopen{}\left( foo \mathclose{}\right)")


def test_curly() -> None:
    assert Latex("foo").curly() == Latex(r"\mathopen{}\left\{ foo \mathclose{}\right\}")


def test_square() -> None:
    assert Latex("foo").square() == Latex(r"\mathopen{}\left[ foo \mathclose{}\right]")


def test_join() -> None:
    assert Latex(":").join([]) == Latex("")
    assert Latex(":").join(["foo"]) == Latex("foo")
    assert Latex(":").join([Latex("foo")]) == Latex("foo")
    assert Latex(":").join([Latex("foo"), "bar"]) == Latex("foo:bar")
    assert Latex(":").join(["foo", Latex("bar")]) == Latex("foo:bar")
    assert Latex(":").join([Latex("foo"), Latex("bar")]) == Latex("foo:bar")
    assert Latex(":").join(()) == Latex("")
    assert Latex(":").join(("foo",)) == Latex("foo")
    assert Latex(":").join((Latex("foo"),)) == Latex("foo")
    assert Latex(":").join((Latex("foo"), "bar")) == Latex("foo:bar")
    assert Latex(":").join(("foo", Latex("bar"))) == Latex("foo:bar")
    assert Latex(":").join((Latex("foo"), Latex("bar"))) == Latex("foo:bar")
    assert Latex(":").join(str(x) for x in range(3)) == Latex("0:1:2")
    assert Latex(":").join(Latex(str(x)) for x in range(3)) == Latex("0:1:2")
