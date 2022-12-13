"""Definition of Latex."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Union

LatexLike = Union[str, "Latex"]


class Latex:
    """LaTeX expression string for ease of writing the codegen source."""

    _raw: str

    def __init__(self, raw: str) -> None:
        """Initializer.

        Args:
            raw: Direct string of the underlying expression.
        """
        self._raw = raw

    def __eq__(self, other: object) -> bool:
        """Checks equality.

        Args:
            other: Other object to check equality.

        Returns:
            True if other is Latex and the underlying expression is the same as self,
            False otherwise.
        """
        return isinstance(other, Latex) and other._raw == self._raw

    def __str__(self) -> str:
        """Returns the underlying expression.

        Returns:
            The underlying expression.
        """
        return self._raw

    def __add__(self, other: object) -> Latex:
        """Concatenates two expressions.

        Args:
            other: The expression to be concatenated to the right side of self.

        Returns:
            A new expression: "{self}{other}"
        """
        if isinstance(other, str):
            return Latex(self._raw + other)
        if isinstance(other, Latex):
            return Latex(self._raw + other._raw)
        raise ValueError("Unsupported operation.")

    def __radd__(self, other: object) -> Latex:
        """Concatenates two expressions.

        Args:
            other: The expression to be concatenated to the left side of self.

        Returns:
            A new expression: "{other}{self}"
        """
        if isinstance(other, str):
            return Latex(other + self._raw)
        if isinstance(other, Latex):
            return Latex(other._raw + self._raw)
        raise ValueError("Unsupported operation.")

    @staticmethod
    def opt(src: LatexLike) -> Latex:
        """Wraps the expression by "[" and "]".

        This wrapping is used when the expression needs to be wrapped as an optional
        argument of the environment.

        Args:
            src: Original expression.

        Returns:
            A new expression with surrounding brackets.
        """
        return Latex("[" + str(src) + "]")

    @staticmethod
    def arg(src: LatexLike) -> Latex:
        """Wraps the expression by "{" and "}".

        This wrapping is used when the expression needs to be wrapped as an argument of
        other expressions.

        Args:
            src: Original expression.

        Returns:
            A new expression with surrounding brackets.
        """
        return Latex("{" + str(src) + "}")

    @staticmethod
    def paren(src: LatexLike) -> Latex:
        """Adds surrounding parentheses: "(" and ")".

        Args:
            src: Original expression.

        Returns:
            A new expression with surrounding brackets.
        """
        return Latex(r"\mathopen{}\left( " + str(src) + r" \mathclose{}\right)")

    @staticmethod
    def curly(src: LatexLike) -> Latex:
        """Adds surrounding curly brackets: "\\{" and "\\}".

        Args:
            src: Original expression.

        Returns:
            A new expression with surrounding brackets.
        """
        return Latex(r"\mathopen{}\left\{ " + str(src) + r" \mathclose{}\right\}")

    @staticmethod
    def square(src: LatexLike) -> Latex:
        """Adds surrounding square brackets: "[" and "]".

        Args:
            src: Original expression.

        Returns:
            A new expression with surrounding brackets.
        """
        return Latex(r"\mathopen{}\left[ " + str(src) + r" \mathclose{}\right]")

    @staticmethod
    def command(
        name: str,
        *,
        options: list[LatexLike] | None = None,
        args: list[LatexLike] | None = None,
    ) -> Latex:
        """Makes a Latex command expression.

        Args:
            name: Name of the command.
            options: List of optional arguments.
            args: List of arguments.

        Returns:
            A new expression.
        """
        elms: list[LatexLike] = [rf"\{name}"]
        if options is not None:
            elms += [Latex.opt(x) for x in options]
        if args is not None:
            elms += [Latex.arg(x) for x in args]

        return Latex.join("", elms)

    @staticmethod
    def environment(
        name: str,
        *,
        options: list[LatexLike] | None = None,
        args: list[LatexLike] | None = None,
        content: LatexLike | None = None,
    ) -> Latex:
        """Makes a Latex environment expression.

        Args:
            name: Name of the environment.
            options: List of optional arguments.
            args: List of arguments.
            content: Inner content of the environment.

        Returns:
            A new expression.
        """
        begin_elms: list[LatexLike] = [rf"\begin{{{name}}}"]
        if options is not None:
            begin_elms += [Latex.opt(x) for x in options]
        if args is not None:
            begin_elms += [Latex.arg(x) for x in args]

        env_elms: list[LatexLike] = [Latex.join("", begin_elms)]
        if content is not None:
            env_elms.append(content)
        env_elms.append(rf"\end{{{name}}}")

        return Latex.join(" ", env_elms)

    @staticmethod
    def join(separator: LatexLike, elements: Iterable[LatexLike]) -> Latex:
        """Joins given sequence.

        Args:
            separator: Expression of the separator between each element.
            elements: Iterable of expressions to be joined.

        Returns:
            A new Latex: "{e[0]}{s}{e[1]}{s}...{s}{e[-1]}"
            where s == separator, and e == elements.
        """
        return Latex(str(separator).join(str(x) for x in elements))
