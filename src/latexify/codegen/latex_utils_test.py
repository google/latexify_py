"""Tests for latex_utils.fy.codegen.latex_utils.utils."""

from __future__ import annotations

from latexify.codegen import latex_utils


def test_opt() -> None:
    assert latex_utils.opt("foo") == "[foo]"
    assert latex_utils.opt("foo") == "[foo]"


def test_arg() -> None:
    assert latex_utils.arg("foo") == "{foo}"
    assert latex_utils.arg("foo") == "{foo}"


def test_paren() -> None:
    assert latex_utils.paren("foo") == r"\mathopen{}\left( foo \mathclose{}\right)"
    assert latex_utils.paren("foo") == r"\mathopen{}\left( foo \mathclose{}\right)"


def test_curly() -> None:
    assert latex_utils.curly("foo") == r"\mathopen{}\left\{ foo \mathclose{}\right\}"
    assert latex_utils.curly("foo") == r"\mathopen{}\left\{ foo \mathclose{}\right\}"


def test_square() -> None:
    assert latex_utils.square("foo") == r"\mathopen{}\left[ foo \mathclose{}\right]"
    assert latex_utils.square("foo") == r"\mathopen{}\left[ foo \mathclose{}\right]"


def test_command() -> None:
    assert latex_utils.command("a") == r"\a"
    assert latex_utils.command("a", options=[]) == r"\a"
    assert latex_utils.command("a", options=["b"]) == r"\a[b]"
    assert latex_utils.command("a", options=["b"]) == r"\a[b]"
    assert latex_utils.command("a", options=["b", "c"]) == r"\a[b][c]"
    assert latex_utils.command("a", args=[]) == r"\a"
    assert latex_utils.command("a", args=["b"]) == r"\a{b}"
    assert latex_utils.command("a", args=["b"]) == r"\a{b}"
    assert latex_utils.command("a", args=["b", "c"]) == r"\a{b}{c}"
    assert latex_utils.command("a", options=["b"], args=["c"]) == r"\a[b]{c}"


def test_environment() -> None:
    assert latex_utils.environment("a") == r"\begin{a} \end{a}"
    assert latex_utils.environment("a", options=[]) == r"\begin{a} \end{a}"
    assert latex_utils.environment("a", options=["b"]) == r"\begin{a}[b] \end{a}"
    assert latex_utils.environment("a", options=["b"]) == r"\begin{a}[b] \end{a}"
    assert (
        latex_utils.environment("a", options=["b", "c"]) == r"\begin{a}[b][c] \end{a}"
    )
    assert latex_utils.environment("a", args=[]) == r"\begin{a} \end{a}"
    assert latex_utils.environment("a", args=["b"]) == r"\begin{a}{b} \end{a}"
    assert latex_utils.environment("a", args=["b"]) == r"\begin{a}{b} \end{a}"
    assert latex_utils.environment("a", args=["b", "c"]) == r"\begin{a}{b}{c} \end{a}"
    assert latex_utils.environment("a", content="b") == r"\begin{a} b \end{a}"
    assert latex_utils.environment("a", content="b") == r"\begin{a} b \end{a}"
    assert (
        latex_utils.environment("a", options=["b"], args=["c"])
        == r"\begin{a}[b]{c} \end{a}"
    )
    assert (
        latex_utils.environment("a", options=["b"], content="c")
        == r"\begin{a}[b] c \end{a}"
    )
    assert (
        latex_utils.environment("a", args=["b"], content="c")
        == r"\begin{a}{b} c \end{a}"
    )
    assert (
        latex_utils.environment("a", options=["b"], args=["c"], content="d")
        == r"\begin{a}[b]{c} d \end{a}"
    )


def test_join() -> None:
    assert latex_utils.join(":", []) == ""
    assert latex_utils.join(":", ["foo"]) == "foo"
    assert latex_utils.join(":", ["foo"]) == "foo"
    assert latex_utils.join(":", ["foo", "bar"]) == "foo:bar"
    assert latex_utils.join(":", ["foo", "bar"]) == "foo:bar"
    assert latex_utils.join(":", ["foo", "bar"]) == "foo:bar"
    assert latex_utils.join(":", ()) == ""
    assert latex_utils.join(":", ("foo",)) == "foo"
    assert latex_utils.join(":", ("foo",)) == "foo"
    assert latex_utils.join(":", ("foo", "bar")) == "foo:bar"
    assert latex_utils.join(":", ("foo", "bar")) == "foo:bar"
    assert latex_utils.join(":", ("foo", "bar")) == "foo:bar"
    assert latex_utils.join(":", (str(x) for x in range(3))) == "0:1:2"
    assert latex_utils.join(":", (str(x) for x in range(3))) == "0:1:2"
