"""Utility to convert identifiers."""


from latexify import math_symbols


class IdentifierConverter:
    """Converts Python identifiers to appropriate LaTeX expression."""

    _use_math_symbols: bool

    def __init__(self, use_math_symbols: bool) -> None:
        """Initializer.

        Args:
            use_math_symbols: Whether to convert identifiers with math symbol names to
                appropriate LaTeX command.
        """
        self._use_math_symbols = use_math_symbols

    def convert(self, name: str) -> tuple[str, bool]:
        """Converts Python identifier to LaTeX expression.

        Args:
            name: Identifier name.

        Returns:
            Tuple of following values:
                - latex: Corresponding LaTeX expression.
                - is_single_character: Whether `latex` can be treated as a single
                    character or not.
        """
        if self._use_math_symbols and name in math_symbols._MATH_SYMBOLS:
            return "\\" + name, True

        if len(name) == 1 and name != "_":
            return name, True

        return r"\mathrm{" + name.replace("_", r"\_") + "}", False
