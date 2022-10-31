"""Tests for latexify.frontend."""

from __future__ import annotations

from latexify import frontend


def test_identifiers() -> None:
    def very_long_name_function(very_long_name_variable):
        return 3 * very_long_name_variable

    identifiers = {
        "very_long_name_function": "f",
        "very_long_name_variable": "x",
    }

    assert frontend.get_latex(very_long_name_function, identifiers=identifiers) == (
        r"\mathrm{f}(x) \triangleq {3}x"
    )
