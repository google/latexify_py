"""Utilities for formatting common LaTeX code patterns."""

from __future__ import annotations

from collections.abc import Iterable


def opt(src: str) -> str:
    """Wraps the expression by "[" and "]".

    This wrapping is used when the expression needs to be wrapped as an optional
    argument of the environment.

    Args:
        src: Original expression.

    Returns:
        A new expression with surrounding brackets.
    """
    return "[" + src + "]"


def arg(src: str) -> str:
    """Wraps the expression by "{" and "}".

    This wrapping is used when the expression needs to be wrapped as an argument of
    other expressions.

    Args:
        src: Original expression.

    Returns:
        A new expression with surrounding brackets.
    """
    return "{" + src + "}"


def paren(src: str) -> str:
    """Adds surrounding parentheses: "(" and ")".

    Args:
        src: Original expression.

    Returns:
        A new expression with surrounding brackets.
    """
    return r"\mathopen{}\left( " + src + r" \mathclose{}\right)"


def curly(src: str) -> str:
    """Adds surrounding curly brackets: "\\{" and "\\}".

    Args:
        src: Original expression.

    Returns:
        A new expression with surrounding brackets.
    """
    return r"\mathopen{}\left\{ " + src + r" \mathclose{}\right\}"


def square(src: str) -> str:
    """Adds surrounding square brackets: "[" and "]".

    Args:
        src: Original expression.

    Returns:
        A new expression with surrounding brackets.
    """
    return r"\mathopen{}\left[ " + src + r" \mathclose{}\right]"


def command(
    name: str,
    *,
    options: list[str] | None = None,
    args: list[str] | None = None,
) -> str:
    """Makes a Latex command expression.

    Args:
        name: Name of the command.
        options: List of optional arguments.
        args: List of arguments.

    Returns:
        A new expression.
    """
    elms = [rf"\{name}"]
    if options is not None:
        elms += [opt(x) for x in options]
    if args is not None:
        elms += [arg(x) for x in args]

    return join("", elms)


def environment(
    name: str,
    *,
    options: list[str] | None = None,
    args: list[str] | None = None,
    separator: str = " ",
    content: str | None = None,
) -> str:
    """Makes a Latex environment expression.

    Args:
        name: Name of the environment.
        options: List of optional arguments.
        args: List of arguments.
        separator: Expression of the separator padding the content.
        content: Inner content of the environment.

    Returns:
        A new expression.
    """
    begin_elms = [rf"\begin{{{name}}}"]
    if options is not None:
        begin_elms += [opt(x) for x in options]
    if args is not None:
        begin_elms += [arg(x) for x in args]

    env_elms = [join("", begin_elms)]
    if content is not None:
        env_elms.append(content)
    env_elms.append(rf"\end{{{name}}}")

    return join(separator, env_elms)


def join(separator: str, elements: Iterable[str]) -> str:
    """Joins given sequence.

    Args:
        separator: Expression of the separator between each element.
        elements: Iterable of expressions to be joined.

    Returns:
        A new Latex: "{e[0]}{s}{e[1]}{s}...{s}{e[-1]}"
        where s == separator, and e == elements.
    """
    return separator.join(elt for elt in elements)
