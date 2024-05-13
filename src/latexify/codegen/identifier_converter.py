"""Utility to convert identifiers."""

from __future__ import annotations

from latexify.codegen import expression_rules


class IdentifierConverter:
    r"""Converts Python identifiers to appropriate LaTeX expression.

    This converter applies following rules:
        - `foo` --> `\foo`, if `use_math_symbols == True` and the given identifier
          matches a supported math symbol name.
        - `x` --> `x`, if the given identifier is exactly 1 character (except `_`)
        - `foo_bar` --> `\mathrm{foo\_bar}`, otherwise.
    """

    _use_math_symbols: bool
    _use_mathrm: bool
    _escape_underscores: bool

    def __init__(
        self,
        *,
        use_math_symbols: bool,
        use_mathrm: bool = True,
        escape_underscores: bool = True,
    ) -> None:
        r"""Initializer.

        Args:
            use_math_symbols: Whether to convert identifiers with math symbol names to
                appropriate LaTeX command.
            use_mathrm: Whether to wrap the resulting expression by \mathrm, if
                applicable.
            escape_underscores: Whether to prefix any underscores in identifiers with '\\',
                disable to allow subscripts in generated latex
        """
        self._use_math_symbols = use_math_symbols
        self._use_mathrm = use_mathrm
        self._escape_underscores = escape_underscores

    def convert(self, name: str) -> tuple[str, bool]:
        """Converts Python identifier to LaTeX expression.

        Args:
            name: Identifier name.

        Returns:
            Tuple of following values:
                - latex: Corresponding LaTeX expression.
                - is_single_character: Whether `latex` can be treated as a single
                    character or not.
        Raises:
            LatexifyError: Resulting latex is not valid. This most likely occurs where the
            symbol starts or ends with an underscore, and escape_underscores=False.
        """
        if not self._escape_underscores and "_" in name:
            # Check if we are going to generate an invalid Latex string. Better to raise an
            # exception here than have the resulting Latex fail to compile/display
            if "__" in name:
                raise ValueError(
                    f'Identifier "{name}" has a double underscore will result in '
                    "invalid Latex when underscores are not escaped"
                )
            if name.startswith("_"):
                raise ValueError(
                    f'Identifier "{name}" starts with an underscore will result in '
                    "invalid Latex when underscores are not escaped"
                )
            if name.endswith("_"):
                raise ValueError(
                    f'Identifier "{name}" ends with an underscore will result in '
                    "invalid Latex when underscores are not escaped"
                )
            elems = [
                IdentifierConverter(
                    use_math_symbols=self._use_math_symbols,
                    use_mathrm=False,
                    escape_underscores=True,
                ).convert(n)[0]
                for n in name.split("_")
            ]
            if name.count("_") == 1:
                # One underscore, no need to wrap subsequent subscripts in braces
                name = "_".join(elems)
            else:
                # Multi-layer subscripts require wrapping each subscript in nesting
                # braces
                name = "_{".join(elems) + "}" * (len(elems) - 1)

        if self._use_math_symbols and name in expression_rules.MATH_SYMBOLS:
            return "\\" + name, True

        if len(name) == 1 and name != "_":
            return name, True

        escaped = name.replace("_", r"\_") if self._escape_underscores else name
        wrapped = rf"\mathrm{{{escaped}}}" if self._use_mathrm else escaped

        return wrapped, False
