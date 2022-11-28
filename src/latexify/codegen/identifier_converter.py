"""Utility to convert identifiers."""

from __future__ import annotations

from typing import final

from latexify import math_symbols


@final
class IdentifierConverter:
    r"""Converts Python identifiers to appropriate LaTeX expression.

    This converter applies following rules:
        - `foo` --> `\foo`, if `use_math_symbols == True` and the given identifier
          matches a supported math symbol name.
        - `x` --> `x`, if the given identifier is exactly 1 character (except `_`)
        - `foo_bar` --> `\mathrm{foo\_bar}`, otherwise.
    """

    _use_math_symbols: bool

    def __init__(self, *, use_math_symbols: bool) -> None:
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
