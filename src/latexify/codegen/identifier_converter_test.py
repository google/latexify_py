"""Tests for latexify.codegen.identifier_converter."""

from __future__ import annotations

import pytest

from latexify.codegen import identifier_converter


@pytest.mark.parametrize(
    "name,use_math_symbols,use_mathrm,escape_underscores,expected",
    [
        ("a", False, True, True, ("a", True)),
        ("_", False, True, True, (r"\mathrm{\_}", False)),
        ("aa", False, True, True, (r"\mathrm{aa}", False)),
        ("a1", False, True, True, (r"\mathrm{a1}", False)),
        ("a_", False, True, True, (r"\mathrm{a\_}", False)),
        ("_a", False, True, True, (r"\mathrm{\_a}", False)),
        ("_1", False, True, True, (r"\mathrm{\_1}", False)),
        ("__", False, True, True, (r"\mathrm{\_\_}", False)),
        ("a_a", False, True, True, (r"\mathrm{a\_a}", False)),
        ("a__", False, True, True, (r"\mathrm{a\_\_}", False)),
        ("a_1", False, True, True, (r"\mathrm{a\_1}", False)),
        ("alpha", False, True, True, (r"\mathrm{alpha}", False)),
        ("alpha", True, True, True, (r"\alpha", True)),
        ("alphabet", True, True, True, (r"\mathrm{alphabet}", False)),
        ("foo", False, True, True, (r"\mathrm{foo}", False)),
        ("foo", True, True, True, (r"\mathrm{foo}", False)),
        ("foo", True, False, True, (r"foo", False)),
        ("aa", False, True, False, (r"\mathrm{aa}", False)),
        ("a_a", False, True, False, (r"\mathrm{a_a}", False)),
        ("a_1", False, True, False, (r"\mathrm{a_1}", False)),
        ("alpha", True, False, False, (r"\alpha", True)),
        ("alpha_1", True, False, False, (r"\alpha_1", False)),
        ("x_alpha", True, False, False, (r"x_\alpha", False)),
        ("x_alpha_beta", True, False, False, (r"x_{\alpha_{\beta}}", False)),
        ("alpha_beta", True, False, False, (r"\alpha_\beta", False)),
    ],
)
def test_identifier_converter(
    name: str,
    use_math_symbols: bool,
    use_mathrm: bool,
    escape_underscores: bool,
    expected: tuple[str, bool],
) -> None:
    assert (
        identifier_converter.IdentifierConverter(
            use_math_symbols=use_math_symbols,
            use_mathrm=use_mathrm,
            escape_underscores=escape_underscores,
        ).convert(name)
        == expected
    )


@pytest.mark.parametrize(
    "name,use_math_symbols,use_mathrm,escape_underscores",
    [
        ("_", False, True, False),
        ("a_", False, True, False),
        ("_a", False, True, False),
        ("_1", False, True, False),
        ("__", False, True, False),
        ("a__", False, True, False),
        ("alpha_", True, False, False),
        ("_alpha", True, False, False),
        ("x__alpha", True, False, False),
    ],
)
def test_identifier_converter_failure(
    name: str,
    use_math_symbols: bool,
    use_mathrm: bool,
    escape_underscores: bool,
) -> None:
    with pytest.raises(ValueError):
        identifier_converter.IdentifierConverter(
            use_math_symbols=use_math_symbols,
            use_mathrm=use_mathrm,
            escape_underscores=escape_underscores,
        ).convert(name)
