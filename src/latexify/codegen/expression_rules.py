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
    "acosh": FunctionRule(r"\mathrm{arcosh}", is_unary=True),
    "arccos": FunctionRule(r"\arccos", is_unary=True),
    "arccot": FunctionRule(r"\mathrm{arccot}", is_unary=True),
    "arccsc": FunctionRule(r"\mathrm{arccsc}", is_unary=True),
    "arcosh": FunctionRule(r"\mathrm{arcosh}", is_unary=True),
    "arcoth": FunctionRule(r"\mathrm{arcoth}", is_unary=True),
    "arcsec": FunctionRule(r"\mathrm{arcsec}", is_unary=True),
    "arcsch": FunctionRule(r"\mathrm{arcsch}", is_unary=True),
    "arcsin": FunctionRule(r"\arcsin", is_unary=True),
    "arctan": FunctionRule(r"\arctan", is_unary=True),
    "arsech": FunctionRule(r"\mathrm{arsech}", is_unary=True),
    "arsinh": FunctionRule(r"\mathrm{arsinh}", is_unary=True),
    "artanh": FunctionRule(r"\mathrm{artanh}", is_unary=True),
    "asin": FunctionRule(r"\arcsin", is_unary=True),
    "asinh": FunctionRule(r"\mathrm{arsinh}", is_unary=True),
    "atan": FunctionRule(r"\arctan", is_unary=True),
    "atanh": FunctionRule(r"\mathrm{artanh}", is_unary=True),
    "ceil": FunctionRule(
        r"\mathopen{}\left\lceil", r"\mathclose{}\right\rceil", is_wrapped=True
    ),
    "cos": FunctionRule(r"\cos", is_unary=True),
    "cosh": FunctionRule(r"\cosh", is_unary=True),
    "cot": FunctionRule(r"\cot", is_unary=True),
    "coth": FunctionRule(r"\coth", is_unary=True),
    "csc": FunctionRule(r"\csc", is_unary=True),
    "csch": FunctionRule(r"\mathrm{csch}", is_unary=True),
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
    "sec": FunctionRule(r"\sec", is_unary=True),
    "sech": FunctionRule(r"\mathrm{sech}", is_unary=True),
    "sin": FunctionRule(r"\sin", is_unary=True),
    "sinh": FunctionRule(r"\sinh", is_unary=True),
    "sqrt": FunctionRule(r"\sqrt{", "}", is_wrapped=True),
    "sum": FunctionRule(r"\sum", is_unary=True),
    "tan": FunctionRule(r"\tan", is_unary=True),
    "tanh": FunctionRule(r"\tanh", is_unary=True),
}
