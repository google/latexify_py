"""Latexify module-level constants"""

from __future__ import annotations

import dataclasses


@dataclasses.dataclass(frozen=True)
class FunctionRule:
    """Codegen rules for functions.

    Attributes:
        left: LaTeX expression concatenated to the left-hand side of the arguments.
        right: LaTeX expression concatenated to the right-hand side of the arguments.
        is_unary: Whether the function is treated as a unary operator or not.
        is_wrapped: Whether the resulting syntax is wrapped by brackets or not.
    """

    left: str
    right: str = ""
    is_unary: bool = False
    is_wrapped: bool = False


# name => left_syntax, right_syntax, is_wrapped
BUILTIN_FUNCS: dict[str, FunctionRule] = {
    "abs": FunctionRule(r"\mathropen{}\left|", r"\mathclose{}\right|", is_wrapped=True),
    "acos": FunctionRule(r"\arccos", is_unary=True),
    "acosh": FunctionRule(r"\mathrm{arccosh}", is_unary=True),
    "arccos": FunctionRule(r"\arccos", is_unary=True),
    "arccosh": FunctionRule(r"\mathrm{arccosh}", is_unary=True),
    "arcsin": FunctionRule(r"\arcsin", is_unary=True),
    "arcsinh": FunctionRule(r"\mathrm{arcsinh}", is_unary=True),
    "arctan": FunctionRule(r"\arctan", is_unary=True),
    "arctanh": FunctionRule(r"\mathrm{arctanh}", is_unary=True),
    "asin": FunctionRule(r"\arcsin", is_unary=True),
    "asinh": FunctionRule(r"\mathrm{arcsinh}", is_unary=True),
    "atan": FunctionRule(r"\arctan", is_unary=True),
    "atanh": FunctionRule(r"\mathrm{arctanh}", is_unary=True),
    "ceil": FunctionRule(
        r"\mathopen{}\left\lceil", r"\mathclose{}\right\rceil", is_wrapped=True
    ),
    "cos": FunctionRule(r"\cos", is_unary=True),
    "cosh": FunctionRule(r"\cosh", is_unary=True),
    "exp": FunctionRule(r"\exp", is_unary=True),
    "fabs": FunctionRule(r"\mathopen{}\left|", r"\mathclose{}\right|", is_wrapped=True),
    "factorial": FunctionRule("", "!", is_unary=True),
    "floor": FunctionRule(
        r"\mathopen{}\left\lfloor", r"\mathclose{}\right\rfloor", is_wrapped=True
    ),
    "fsum": FunctionRule(r"\sum", is_unary=True),
    "gamma": FunctionRule(r"\Gamma"),
    "log": FunctionRule(r"\log", is_unary=True),
    "log10": FunctionRule(r"\log_10", is_unary=True),
    "log2": FunctionRule(r"\log_2", is_unary=True),
    "prod": FunctionRule(r"\prod", is_unary=True),
    "sin": FunctionRule(r"\sin", is_unary=True),
    "sinh": FunctionRule(r"\sinh", is_unary=True),
    "sqrt": FunctionRule(r"\sqrt{", "}", is_wrapped=True),
    "sum": FunctionRule(r"\sum", is_unary=True),
    "tan": FunctionRule(r"\tan", is_unary=True),
    "tanh": FunctionRule(r"\tanh", is_unary=True),
}
