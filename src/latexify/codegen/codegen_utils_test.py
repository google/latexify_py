"""Tests for latexify.codegen.codegen_utils."""

from __future__ import annotations

from typing import Any

import pytest

from latexify import exceptions
from latexify.codegen.codegen_utils import convert_constant


@pytest.mark.parametrize(
    "constant,latex",
    [
        (None, r"\mathrm{None}"),
        (True, r"\mathrm{True}"),
        (False, r"\mathrm{False}"),
        (123, "123"),
        (456.789, "456.789"),
        (-3 + 4j, "(-3+4j)"),
        ("string", r'\textrm{"string"}'),
        (..., r"\cdots"),
    ],
)
def test_convert_constant(constant: Any, latex: str) -> None:
    assert convert_constant(constant) == latex


def test_convert_constant_unsupported_constant() -> None:
    with pytest.raises(
        exceptions.LatexifyNotSupportedError, match="^Unrecognized constant: "
    ):
        convert_constant({})
