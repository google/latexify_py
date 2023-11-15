"""Codegen rules for single expressions."""

from __future__ import annotations

import ast
import dataclasses

# Precedences of operators for BoolOp, BinOp, UnaryOp, and Compare nodes.
# Note that this value affects only the appearance of surrounding parentheses for each
# expression, and does not affect the AST itself.
# See also:
# https://docs.python.org/3/reference/expressions.html#operator-precedence
_PRECEDENCES: dict[type[ast.AST], int] = {
    ast.Pow: 120,
    ast.UAdd: 110,
    ast.USub: 110,
    ast.Invert: 110,
    ast.Mult: 100,
    ast.MatMult: 100,
    ast.Div: 100,
    ast.FloorDiv: 100,
    ast.Mod: 100,
    ast.Add: 90,
    ast.Sub: 90,
    ast.LShift: 80,
    ast.RShift: 80,
    ast.BitAnd: 70,
    ast.BitXor: 60,
    ast.BitOr: 50,
    ast.In: 40,
    ast.NotIn: 40,
    ast.Is: 40,
    ast.IsNot: 40,
    ast.Lt: 40,
    ast.LtE: 40,
    ast.Gt: 40,
    ast.GtE: 40,
    ast.NotEq: 40,
    ast.Eq: 40,
    # NOTE(odashi):
    # We assume that the `not` operator has the same precedence with other unary
    # operators `+`, `-` and `~`, because the LaTeX counterpart $\lnot$ looks to have a
    # high precedence.
    # ast.Not: 30,
    ast.Not: 110,
    ast.And: 20,
    ast.Or: 10,
}

# NOTE(odashi):
# Function invocation is treated as a unary operator with a higher precedence.
# This ensures that the argument with a unary operator is wrapped:
#     exp(x) --> \exp x
#     exp(-x) --> \exp (-x)
#     -exp(x) --> - \exp x
_CALL_PRECEDENCE = _PRECEDENCES[ast.UAdd] + 1

_INF_PRECEDENCE = 1_000_000


def get_precedence(node: ast.AST) -> int:
    """Obtains the precedence of the subtree.

    Args:
        node: Subtree to investigate.

    Returns:
        If `node` is a subtree with some operator, returns the precedence of the
        operator. Otherwise, returns a number larger enough from other precedences.
    """
    if isinstance(node, ast.Call):
        return _CALL_PRECEDENCE

    if isinstance(node, (ast.BinOp, ast.UnaryOp, ast.BoolOp)):
        return _PRECEDENCES[type(node.op)]

    if isinstance(node, ast.Compare):
        # Compare operators have the same precedence. It is enough to check only the
        # first operator.
        return _PRECEDENCES[type(node.ops[0])]

    return _INF_PRECEDENCE


@dataclasses.dataclass(frozen=True)
class BinOperandRule:
    """Syntax rules for operands of BinOp."""

    # Whether to require wrapping operands by parentheses according to the precedence.
    wrap: bool = True

    # Whether to require wrapping operands by parentheses if the operand has the same
    # precedence with this operator.
    # This is used to control the behavior of non-associative operators.
    force: bool = False


@dataclasses.dataclass(frozen=True)
class BinOpRule:
    """Syntax rules for BinOp."""

    # Left/middle/right syntaxes to wrap operands.
    latex_left: str
    latex_middle: str
    latex_right: str

    # Operand rules.
    operand_left: BinOperandRule = dataclasses.field(default_factory=BinOperandRule)
    operand_right: BinOperandRule = dataclasses.field(default_factory=BinOperandRule)

    # Whether to assume the resulting syntax is wrapped by some bracket operators.
    # If True, the parent operator can avoid wrapping this operator by parentheses.
    is_wrapped: bool = False


BIN_OP_RULES: dict[type[ast.operator], BinOpRule] = {
    ast.Pow: BinOpRule(
        "",
        "^{",
        "}",
        operand_left=BinOperandRule(force=True),
        operand_right=BinOperandRule(wrap=False),
    ),
    ast.Mult: BinOpRule("", r" \cdot ", ""),
    ast.MatMult: BinOpRule("", r" \cdot ", ""),
    ast.Div: BinOpRule(
        r"\frac{",
        "}{",
        "}",
        operand_left=BinOperandRule(wrap=False),
        operand_right=BinOperandRule(wrap=False),
    ),
    ast.FloorDiv: BinOpRule(
        r"\left\lfloor\frac{",
        "}{",
        r"}\right\rfloor",
        operand_left=BinOperandRule(wrap=False),
        operand_right=BinOperandRule(wrap=False),
        is_wrapped=True,
    ),
    ast.Mod: BinOpRule(
        "", r" \mathbin{\%} ", "", operand_right=BinOperandRule(force=True)
    ),
    ast.Add: BinOpRule("", " + ", ""),
    ast.Sub: BinOpRule("", " - ", "", operand_right=BinOperandRule(force=True)),
    ast.LShift: BinOpRule("", r" \ll ", "", operand_right=BinOperandRule(force=True)),
    ast.RShift: BinOpRule("", r" \gg ", "", operand_right=BinOperandRule(force=True)),
    ast.BitAnd: BinOpRule("", r" \mathbin{\&} ", ""),
    ast.BitXor: BinOpRule("", r" \oplus ", ""),
    ast.BitOr: BinOpRule("", r" \mathbin{|} ", ""),
}

# Typeset for BinOp of sets.
SET_BIN_OP_RULES: dict[type[ast.operator], BinOpRule] = {
    **BIN_OP_RULES,
    ast.Sub: BinOpRule(
        "", r" \setminus ", "", operand_right=BinOperandRule(force=True)
    ),
    ast.BitAnd: BinOpRule("", r" \cap ", ""),
    ast.BitXor: BinOpRule("", r" \mathbin{\triangle} ", ""),
    ast.BitOr: BinOpRule("", r" \cup ", ""),
}

UNARY_OPS: dict[type[ast.unaryop], str] = {
    ast.Invert: r"\mathord{\sim} ",
    ast.UAdd: "+",  # Explicitly adds the $+$ operator.
    ast.USub: "-",
    ast.Not: r"\lnot ",
}

COMPARE_OPS: dict[type[ast.cmpop], str] = {
    ast.Eq: "=",
    ast.Gt: ">",
    ast.GtE: r"\ge",
    ast.In: r"\in",
    ast.Is: r"\equiv",
    ast.IsNot: r"\not\equiv",
    ast.Lt: "<",
    ast.LtE: r"\le",
    ast.NotEq: r"\ne",
    ast.NotIn: r"\notin",
}

# Typeset for Compare of sets.
SET_COMPARE_OPS: dict[type[ast.cmpop], str] = {
    **COMPARE_OPS,
    ast.Gt: r"\supset",
    ast.GtE: r"\supseteq",
    ast.Lt: r"\subset",
    ast.LtE: r"\subseteq",
}

BOOL_OPS: dict[type[ast.boolop], str] = {
    ast.And: r"\land",
    ast.Or: r"\lor",
}


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
    "abs": FunctionRule(r"\mathopen{}\left|", r"\mathclose{}\right|", is_wrapped=True),
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
    "log10": FunctionRule(r"\log_{10}", is_unary=True),
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

MATH_SYMBOLS = {
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
    "hbar",
    "infty",
    "iota",
    "kappa",
    "lambda",
    "mu",
    "nabla",
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
