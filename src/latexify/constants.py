"""Latexify module-level constants"""

from __future__ import annotations

import dataclasses
import enum


class BuiltinFnName(str, enum.Enum):
    """Built-in function name."""

    ABS = "abs"
    ACOS = "acos"
    ACOSH = "acosh"
    ARCCOS = "arccos"
    ARCCOSH = "arcosh"
    ARCSIN = "arcsin"
    ARCSINH = "arcsihn"
    ARCTAN = "arctan"
    ARCTANH = "arctanh"
    ASIN = "asin"
    ASINH = "asinh"
    ATAN = "atan"
    ATANH = "atanh"
    CEIL = "ceil"
    COS = "cos"
    COSH = "cosh"
    EXP = "exp"
    FABS = "fabs"
    FACTORIAL = "factorial"
    FLOOR = "floor"
    FSUM = "fsum"
    GAMMA = "gamma"
    LOG = "log"
    LOG10 = "log10"
    LOG2 = "log2"
    PROD = "prod"
    SIN = "sin"
    SINH = "sinh"
    SQRT = "sqrt"
    TAN = "tan"
    TANH = "tanh"
    SUM = "sum"


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
BUILTIN_FUNCS: dict[BuiltinFnName, FunctionRule] = {
    BuiltinFnName.ABS: FunctionRule(
        r"\mathropen{}\left|", r"\mathclose{}\right|", is_wrapped=True
    ),
    BuiltinFnName.ACOS: FunctionRule(r"\arccos", is_unary=True),
    BuiltinFnName.ACOSH: FunctionRule(r"\mathrm{arccosh}", is_unary=True),
    BuiltinFnName.ARCCOS: FunctionRule(r"\arccos", is_unary=True),
    BuiltinFnName.ARCCOSH: FunctionRule(r"\mathrm{arccosh}", is_unary=True),
    BuiltinFnName.ARCSIN: FunctionRule(r"\arcsin", is_unary=True),
    BuiltinFnName.ARCSINH: FunctionRule(r"\mathrm{arcsinh}", is_unary=True),
    BuiltinFnName.ARCTAN: FunctionRule(r"\arctan", is_unary=True),
    BuiltinFnName.ARCTANH: FunctionRule(r"\mathrm{arctanh}", is_unary=True),
    BuiltinFnName.ASIN: FunctionRule(r"\arcsin", is_unary=True),
    BuiltinFnName.ASINH: FunctionRule(r"\mathrm{arcsinh}", is_unary=True),
    BuiltinFnName.ATAN: FunctionRule(r"\arctan", is_unary=True),
    BuiltinFnName.ATANH: FunctionRule(r"\mathrm{arctanh}", is_unary=True),
    BuiltinFnName.CEIL: FunctionRule(
        r"\mathopen{}\left\lceil", r"\mathclose{}\right\rceil", is_wrapped=True
    ),
    BuiltinFnName.COS: FunctionRule(r"\cos", is_unary=True),
    BuiltinFnName.COSH: FunctionRule(r"\cosh", is_unary=True),
    BuiltinFnName.EXP: FunctionRule(r"\exp", is_unary=True),
    BuiltinFnName.FABS: FunctionRule(
        r"\mathopen{}\left|", r"\mathclose{}\right|", is_wrapped=True
    ),
    BuiltinFnName.FACTORIAL: FunctionRule("", "!", is_unary=True),
    BuiltinFnName.FLOOR: FunctionRule(
        r"\mathopen{}\left\lfloor", r"\mathclose{}\right\rfloor", is_wrapped=True
    ),
    BuiltinFnName.FSUM: FunctionRule(r"\sum", is_unary=True),
    BuiltinFnName.GAMMA: FunctionRule(r"\Gamma"),
    BuiltinFnName.LOG: FunctionRule(r"\log", is_unary=True),
    BuiltinFnName.LOG10: FunctionRule(r"\log_{10}", is_unary=True),
    BuiltinFnName.LOG2: FunctionRule(r"\log_{2}", is_unary=True),
    BuiltinFnName.PROD: FunctionRule(r"\prod", is_unary=True),
    BuiltinFnName.SIN: FunctionRule(r"\sin", is_unary=True),
    BuiltinFnName.SINH: FunctionRule(r"\sinh", is_unary=True),
    BuiltinFnName.SQRT: FunctionRule(r"\sqrt{", "}", is_wrapped=True),
    BuiltinFnName.SUM: FunctionRule(r"\sum", is_unary=True),
    BuiltinFnName.TAN: FunctionRule(r"\tan", is_unary=True),
    BuiltinFnName.TANH: FunctionRule(r"\tanh", is_unary=True),
}
