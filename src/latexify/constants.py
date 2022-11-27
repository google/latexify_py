"""Latexify module-level constants"""

from __future__ import annotations

import enum

PREFIXES = {"math", "numpy", "np"}


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


BUILTIN_FUNCS: dict[BuiltinFnName, tuple[str, str]] = {
    BuiltinFnName.ABS: (r"\left|{", r"}\right|"),
    BuiltinFnName.ACOS: (r"\arccos{\left({", r"}\right)}"),
    BuiltinFnName.ACOSH: (r"\mathrm{arccosh}{\left({", r"}\right)}"),
    BuiltinFnName.ARCCOS: (r"\arccos{\left({", r"}\right)}"),
    BuiltinFnName.ARCCOSH: (r"\mathrm{arccosh}{\left({", r"}\right)}"),
    BuiltinFnName.ARCSIN: (r"\arcsin{\left({", r"}\right)}"),
    BuiltinFnName.ARCSINH: (r"\mathrm{arcsinh}{\left({", r"}\right)}"),
    BuiltinFnName.ARCTAN: (r"\arctan{\left({", r"}\right)}"),
    BuiltinFnName.ARCTANH: (r"\mathrm{arctanh}{\left({", r"}\right)}"),
    BuiltinFnName.ASIN: (r"\arcsin{\left({", r"}\right)}"),
    BuiltinFnName.ASINH: (r"\mathrm{arcsinh}{\left({", r"}\right)}"),
    BuiltinFnName.ATAN: (r"\arctan{\left({", r"}\right)}"),
    BuiltinFnName.ATANH: (r"\mathrm{arctanh}{\left({", r"}\right)}"),
    BuiltinFnName.CEIL: (r"\left\lceil{", r"}\right\rceil"),
    BuiltinFnName.COS: (r"\cos{\left({", r"}\right)}"),
    BuiltinFnName.COSH: (r"\cosh{\left({", r"}\right)}"),
    BuiltinFnName.EXP: (r"\exp{\left({", r"}\right)}"),
    BuiltinFnName.FABS: (r"\left|{", r"}\right|"),
    BuiltinFnName.FACTORIAL: (r"\left({", r"}\right)!"),
    BuiltinFnName.FLOOR: (r"\left\lfloor{", r"}\right\rfloor"),
    BuiltinFnName.FSUM: (r"\sum\left({", r"}\right)"),
    BuiltinFnName.GAMMA: (r"\Gamma\left({", r"}\right)"),
    BuiltinFnName.LOG: (r"\log{\left({", r"}\right)}"),
    BuiltinFnName.LOG10: (r"\log_{10}{\left({", r"}\right)}"),
    BuiltinFnName.LOG2: (r"\log_{2}{\left({", r"}\right)}"),
    BuiltinFnName.PROD: (r"\prod \left({", r"}\right)"),
    BuiltinFnName.SIN: (r"\sin{\left({", r"}\right)}"),
    BuiltinFnName.SINH: (r"\sinh{\left({", r"}\right)}"),
    BuiltinFnName.SQRT: (r"\sqrt{", "}"),
    BuiltinFnName.TAN: (r"\tan{\left({", r"}\right)}"),
    BuiltinFnName.TANH: (r"\tanh{\left({", r"}\right)}"),
    BuiltinFnName.SUM: (r"\sum \left({", r"}\right)"),
}
