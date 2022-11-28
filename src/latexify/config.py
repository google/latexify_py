"""Definition of the Config class."""

from __future__ import annotations

import dataclasses
from typing import Any


@dataclasses.dataclass(frozen=True)
class Config:
    """Configurations to control the behavior of latexify.

    Attributes:
        expand_functions: If set, the names of the functions to expand.
        identifiers: If set, the mapping to replace identifier names in the
            function. Keys are the original names of the identifiers,
            and corresponding values are the replacements.
            Both keys and values have to represent valid Python identifiers:
            ^[A-Za-z_][A-Za-z0-9_]*$
        prefixes: Prefixes of identifiers to trim. E.g., if "foo.bar" in prefixes, all
            identifiers with the form "foo.bar.suffix" will be replaced to "suffix"
        reduce_assignments: If True, assignment statements are used to synthesize
            the final expression.
        use_math_symbols: Whether to convert identifiers with a math symbol surface
            (e.g., "alpha") to the LaTeX symbol (e.g., "\\alpha").
        use_set_symbols: Whether to use set symbols or not.
        use_signature: Whether to add the function signature before the expression
            or not.
    """

    expand_functions: set[str] | None
    identifiers: dict[str, str] | None
    prefixes: set[str] | None
    reduce_assignments: bool
    use_math_symbols: bool
    use_set_symbols: bool
    use_signature: bool

    def merge(self, *, config: Config | None = None, **kwargs) -> Config:
        """Merge configuration based on old configuration and field values.

        Args:
            config: If None, the merged one will merge defaults and field values,
                instead of merging old configuration and field values.
            **kwargs: Members to modify. This value precedes both self and config.

        Returns:
            A new Config object
        """

        def merge_field(name: str) -> Any:
            # Precedence: kwargs -> config -> self
            arg = kwargs.get(name)
            if arg is None:
                if config is not None:
                    arg = getattr(config, name)
                else:
                    arg = getattr(self, name)
            return arg

        return Config(**{f.name: merge_field(f.name) for f in dataclasses.fields(self)})

    @staticmethod
    def defaults() -> Config:
        """Generates a Config with default values.

        Returns:
            A new Config with default values
        """
        return Config(
            expand_functions=None,
            identifiers=None,
            prefixes=None,
            reduce_assignments=False,
            use_math_symbols=False,
            use_set_symbols=False,
            use_signature=True,
        )
