"""Utilities to manipulate math symbols."""

from __future__ import annotations

_MATH_SYMBOLS = {
    "aleph",
    "alpha",
    "beta",
    "beth",
    "chi",
    "daleth",
    "delta",
    "digamma",
    "epsilon",
    "eta",
    "gamma",
    "gimel",
    "iota",
    "kappa",
    "lambda",
    "mu",
    "nu",
    "omega",
    "phi",
    "pi",
    "psi",
    "rho",
    "sigma",
    "tau",
    "theta",
    "upsilon",
    "varepsilon",
    "varkappa",
    "varphi",
    "varpi",
    "varrho",
    "varsigma",
    "vartheta",
    "xi",
    "zeta",
    "Delta",
    "Gamma",
    "Lambda",
    "Omega",
    "Phi",
    "Pi",
    "Psi",
    "Sigma",
    "Theta",
    "Upsilon",
    "Xi",
}


class MathSymbolConverter:
    """Strategy to convert identifier name to LaTeX math symbols."""

    _enabled: bool

    def __init__(self, enabled: bool):
        """Initializer.

        Args:
            enabled: Whether to enable every conversion. If True, all conversion will be
                performed. If False, the given string is returned as-is.
        """
        self._enabled = enabled

    def convert(self, name: str) -> str:
        """Converts given identifier to the specified form.

        Args:
            name: Name of the identifier to be converted.

        Returns:
            Converted LaTeX string.
        """
        if not self._enabled:
            return name

        if name in _MATH_SYMBOLS:
            return "{\\" + name + "}"

        return name
