"""Tests for latexify.codegen.identifier_converter."""

import pytest

from latexify.codegen import identifier_converter


@pytest.mark.parametrize(
    "name,use_math_symbols,expected",
    [
        ("a", False, ("a", True)),
        ("_", False, (r"\mathrm{\_}", False)),
        ("aa", False, (r"\mathrm{aa}", False)),
        ("a1", False, (r"\mathrm{a1}", False)),
        ("a_", False, (r"\mathrm{a\_}", False)),
        ("_a", False, (r"\mathrm{\_a}", False)),
        ("_1", False, (r"\mathrm{\_1}", False)),
        ("__", False, (r"\mathrm{\_\_}", False)),
        ("a_a", False, (r"\mathrm{a\_a}", False)),
        ("a__", False, (r"\mathrm{a\_\_}", False)),
        ("a_1", False, (r"\mathrm{a\_1}", False)),
        ("alpha", False, (r"\mathrm{alpha}", False)),
        ("alpha", True, (r"\alpha", True)),
    ],
)
def test_identifier_converter(
    name: str, use_math_symbols: bool, expected: tuple[str, bool]
) -> None:
    assert (
        identifier_converter.IdentifierConverter(
            use_math_symbols=use_math_symbols
        ).convert(name)
        == expected
    )
