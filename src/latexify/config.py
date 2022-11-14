from __future__ import annotations
import dataclasses

from typing import Any


@dataclasses.dataclass(frozen=True)
class Config:
    identifiers: dict[str, str] | None
    expanded_functions: set[str] | None
    reduce_assignments: bool
    use_math_symbols: bool
    use_raw_function_name: bool
    use_signature: bool
    use_set_symbols: bool

    def merge(self, *, config: Config | None = None, **kwargs) -> Config:
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

    def expand_function(self, fun: str | list[str]) -> None:
        if type(function) == str:
            self.expanded_function.add(fun)
        elif type(function) == list:
            self.expand_function.update(fun)

    @staticmethod
    def defaults() -> Config:
        return Config(
            identifiers=None,
            expanded_functions=set(),
            reduce_assignments=False,
            use_math_symbols=False,
            use_raw_function_name=False,
            use_signature=True,
            use_set_symbols=False,
        )
