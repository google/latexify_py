"""Tests for latexify.codegen.identifier_converter."""

from __future__ import annotations

import pytest

from latexify.codegen import identifier_converter


@pytest.mark.parametrize(
    "name,use_math_symbols,use_mathrm,expected",
    [
        ("a", False, True, ("a", True)),
        ("_", False, True, (r"\mathrm{\_}", False)),
        ("aa", False, True, (r"\mathrm{aa}", False)),
        ("a1", False, True, (r"\mathrm{a1}", False)),
        ("a_", False, True, (r"\mathrm{a\_}", False)),
        ("_a", False, True, (r"\mathrm{\_a}", False)),
        ("_1", False, True, (r"\mathrm{\_1}", False)),
        ("__", False, True, (r"\mathrm{\_\_}", False)),
        ("a_a", False, True, (r"\mathrm{a\_a}", False)),
        ("a__", False, True, (r"\mathrm{a\_\_}", False)),
        ("a_1", False, True, (r"\mathrm{a\_1}", False)),
        ("alpha", False, True, (r"\mathrm{alpha}", False)),
        ("alpha", True, True, (r"\alpha", True)),
        ("foo", False, True, (r"\mathrm{foo}", False)),
        ("foo", True, True, (r"\mathrm{foo}", False)),
        ("foo", True, False, (r"foo", False)),
    ],
)
def test_identifier_converter(
    name: str, use_math_symbols: bool, use_mathrm: bool, expected: tuple[str, bool]
) -> None:
    assert (
        identifier_converter.IdentifierConverter(
            use_math_symbols=use_math_symbols, use_mathrm=use_mathrm
        ).convert(name)
        == expected
    )
