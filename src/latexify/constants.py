"""Latexify module-level constants"""

from __future__ import annotations

PREFIXES = ["math", "numpy", "np"]

BUILTIN_FUNCS: dict[str, tuple[str, str]] = {
    "abs": (r"\left|{", r"}\right|"),
    "acos": (r"\arccos{\left({", r"}\right)}"),
    "acosh": (r"\mathrm{arccosh}{\left({", r"}\right)}"),
    "arccos": (r"\arccos{\left({", r"}\right)}"),
    "arccosh": (r"\mathrm{arccosh}{\left({", r"}\right)}"),
    "arcsin": (r"\arcsin{\left({", r"}\right)}"),
    "arcsinh": (r"\mathrm{arcsinh}{\left({", r"}\right)}"),
    "arctan": (r"\arctan{\left({", r"}\right)}"),
    "arctanh": (r"\mathrm{arctanh}{\left({", r"}\right)}"),
    "asin": (r"\arcsin{\left({", r"}\right)}"),
    "asinh": (r"\mathrm{arcsinh}{\left({", r"}\right)}"),
    "atan": (r"\arctan{\left({", r"}\right)}"),
    "atanh": (r"\mathrm{arctanh}{\left({", r"}\right)}"),
    "ceil": (r"\left\lceil{", r"}\right\rceil"),
    "cos": (r"\cos{\left({", r"}\right)}"),
    "cosh": (r"\cosh{\left({", r"}\right)}"),
    "exp": (r"\exp{\left({", r"}\right)}"),
    "fabs": (r"\left|{", r"}\right|"),
    "factorial": (r"\left({", r"}\right)!"),
    "floor": (r"\left\lfloor{", r"}\right\rfloor"),
    "fsum": (r"\sum\left({", r"}\right)"),
    "gamma": (r"\Gamma\left({", r"}\right)"),
    "log": (r"\log{\left({", r"}\right)}"),
    "log10": (r"\log_{10}{\left({", r"}\right)}"),
    "log2": (r"\log_{2}{\left({", r"}\right)}"),
    "prod": (r"\prod \left({", r"}\right)"),
    "sin": (r"\sin{\left({", r"}\right)}"),
    "sinh": (r"\sinh{\left({", r"}\right)}"),
    "sqrt": (r"\sqrt{", "}"),
    "tan": (r"\tan{\left({", r"}\right)}"),
    "tanh": (r"\tanh{\left({", r"}\right)}"),
    "sum": (r"\sum \left({", r"}\right)"),
}
