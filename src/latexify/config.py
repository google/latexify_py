"""Definition of the Config class."""

from __future__ import annotations

import dataclasses

from typing import Any


@dataclasses.dataclass(frozen=True)
class Config:
    """Configurations to control the behavior of latexify."""

    identifiers: dict[str, str] | None
    reduce_assignments: bool
    use_math_symbols: bool
    use_raw_function_name: bool
    use_signature: bool
    use_set_symbols: bool

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
            identifiers=None,
            reduce_assignments=False,
            use_math_symbols=False,
            use_raw_function_name=False,
            use_signature=True,
            use_set_symbols=False,
        )
