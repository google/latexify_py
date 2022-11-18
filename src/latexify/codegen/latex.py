"""Definition of Latex."""

from __future__ import annotations

from collections.abc import Iterable


class Latex:
    """LaTeX expression string for ease of writing the codegen source."""

    _raw: str

    def __init__(self, raw: str) -> None:
        """Initializer.

        Args:
            raw: Direct string of the underlying expression.
        """
        self._raw = raw

    def __eq__(self, other: object) -> None:
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

    def wrap(self) -> Latex:
        """Wraps the expression by "{" and "}".

        This wrapping is used when the expression needs to be wrapped as an argument of
        other expressions.
        """
        return Latex("{" + self._raw + "}")

    def paren(self) -> Latex:
        """Adds surrounding parentheses: "(" and ")".

        Returns:
            A new Latex with surrounding brackets.
        """
        return Latex(r"\mathopen{}\left( " + self._raw + r" \mathclose{}\right)")

    def curly(self) -> Latex:
        """Adds surrounding curly brackets: "\\{" and "\\}".

        Returns:
            A new Latex with surrounding brackets.
        """
        return Latex(r"\mathopen{}\left\{ " + self._raw + r" \mathclose{}\right\}")

    def square(self) -> Latex:
        """Adds surrounding square brackets: "[" and "]".

        Returns:
            A new Latex with surrounding brackets.
        """
        return Latex(r"\mathopen{}\left[ " + self._raw + r" \mathclose{}\right]")

    def join(self, seq: Iterable[str | Latex]) -> Latex:
        """Joins given sequence.

        Args:
            seq: Iterable of expressions to be joined.

        Returns:
            A new Latex: "{seq[0]}{self}{seq[1]}{self}...{self}{seq[-1]}"
        """
        return Latex(self._raw.join(x._raw if isinstance(x, Latex) else x for x in seq))
