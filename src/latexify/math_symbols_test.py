"""Tests for latexify.math_symbols."""

from __future__ import annotations

import pytest

from latexify import math_symbols


@pytest.mark.parametrize(
    "name,converted,enabled",
    [
        ("foo", "foo", False),
        ("foo", "foo", True),
        ("alpha", "alpha", False),
        ("alpha", "{\\alpha}", True),
    ],
)
def test_math_symbol_converter_convert(name: str, converted: str, enabled: bool):
    assert math_symbols.MathSymbolConverter(enabled=enabled).convert(name) == converted
