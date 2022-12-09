"""Codegen for single function."""

from __future__ import annotations

import ast
import dataclasses
import sys
from typing import Any

from latexify import analyzers, ast_utils, constants, exceptions
from latexify.codegen import identifier_converter

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


def _get_precedence(node: ast.AST) -> int:
    """Obtains the precedence of the subtree.

    Args:
        node: Subtree to investigate.

    Returns:
        If `node` is a subtree with some operator, returns the precedence of the
        operator. Otherwise, returns a number larger enough from other precedences.
    """
    if isinstance(node, ast.Call):
        return _CALL_PRECEDENCE

    if isinstance(node, (ast.BoolOp, ast.BinOp, ast.UnaryOp)):
        return _PRECEDENCES[type(node.op)]

    if isinstance(node, ast.Compare):
        # Compare operators have the same precedence. It is enough to check only the
        # first operator.
        return _PRECEDENCES[type(node.ops[0])]

    return 1_000_000


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


_BIN_OP_RULES: dict[type[ast.operator], BinOpRule] = {
    ast.Pow: BinOpRule(
        "",
        "^{",
        "}",
        operand_left=BinOperandRule(force=True),
        operand_right=BinOperandRule(wrap=False),
    ),
    ast.Mult: BinOpRule("", " ", ""),
    ast.MatMult: BinOpRule("", " ", ""),
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
_SET_BIN_OP_RULES: dict[type[ast.operator], BinOpRule] = {
    **_BIN_OP_RULES,
    ast.Sub: BinOpRule(
        "", r" \setminus ", "", operand_right=BinOperandRule(force=True)
    ),
    ast.BitAnd: BinOpRule("", r" \cap ", ""),
    ast.BitXor: BinOpRule("", r" \mathbin{\triangle} ", ""),
    ast.BitOr: BinOpRule("", r" \cup ", ""),
}

_UNARY_OPS: dict[type[ast.unaryop], str] = {
    ast.Invert: r"\mathord{\sim} ",
    ast.UAdd: "+",  # Explicitly adds the $+$ operator.
    ast.USub: "-",
    ast.Not: r"\lnot ",
}

_COMPARE_OPS: dict[type[ast.cmpop], str] = {
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
_SET_COMPARE_OPS: dict[type[ast.cmpop], str] = {
    **_COMPARE_OPS,
    ast.Gt: r"\supset",
    ast.GtE: r"\supseteq",
    ast.Lt: r"\subset",
    ast.LtE: r"\subseteq",
}

_BOOL_OPS: dict[type[ast.boolop], str] = {
    ast.And: r"\land",
    ast.Or: r"\lor",
}


class FunctionCodegen(ast.NodeVisitor):
    """Codegen for single functions.

    This codegen works for Module with single FunctionDef node to generate a single
    LaTeX expression of the given function.
    """

    _identifier_converter: identifier_converter.IdentifierConverter
    _use_signature: bool

    _bin_op_rules: dict[type[ast.operator], BinOpRule]
    _compare_ops: dict[type[ast.cmpop], str]

    def __init__(
        self,
        *,
        use_math_symbols: bool = False,
        use_signature: bool = True,
        use_set_symbols: bool = False,
    ) -> None:
        """Initializer.

        Args:
            use_math_symbols: Whether to convert identifiers with a math symbol surface
                (e.g., "alpha") to the LaTeX symbol (e.g., "\\alpha").
            use_signature: Whether to add the function signature before the expression
                or not.
            use_set_symbols: Whether to use set symbols or not.
        """
        self._identifier_converter = identifier_converter.IdentifierConverter(
            use_math_symbols=use_math_symbols
        )
        self._use_signature = use_signature

        self._bin_op_rules = _SET_BIN_OP_RULES if use_set_symbols else _BIN_OP_RULES
        self._compare_ops = _SET_COMPARE_OPS if use_set_symbols else _COMPARE_OPS

    def generic_visit(self, node: ast.AST) -> str:
        raise exceptions.LatexifyNotSupportedError(
            f"Unsupported AST: {type(node).__name__}"
        )

    def visit_Module(self, node: ast.Module) -> str:
        return self.visit(node.body[0])

    def visit_FunctionDef(self, node: ast.FunctionDef) -> str:
        # Function name
        name_str = self._identifier_converter.convert(node.name)[0]

        # Arguments
        arg_strs = [
            self._identifier_converter.convert(arg.arg)[0] for arg in node.args.args
        ]

        body_strs: list[str] = []

        # Assignment statements (if any): x = ...
        for child in node.body[:-1]:
            if isinstance(child, ast.Expr) and ast_utils.is_constant(child.value):
                continue

            if not isinstance(child, ast.Assign):
                raise exceptions.LatexifyNotSupportedError(
                    "Codegen supports only Assign nodes in multiline functions, "
                    f"but got: {type(child).__name__}"
                )
            body_strs.append(self.visit(child))

        return_stmt = node.body[-1]

        if not isinstance(return_stmt, (ast.Return, ast.If)):
            raise exceptions.LatexifySyntaxError(
                f"Unsupported last statement: {type(return_stmt).__name__}"
            )

        # Function signature: f(x, ...)
        signature_str = name_str + "(" + ", ".join(arg_strs) + ")"

        # Function definition: f(x, ...) \triangleq ...
        return_str = self.visit(return_stmt)
        if self._use_signature:
            return_str = signature_str + " = " + return_str

        if not body_strs:
            # Only the definition.
            return return_str

        # Definition with several assignments. Wrap all statements with array.
        body_strs.append(return_str)
        return r"\begin{array}{l} " + r" \\ ".join(body_strs) + r" \end{array}"

    def visit_Assign(self, node: ast.Assign) -> str:
        operands: list[str] = [self.visit(t) for t in node.targets]
        operands.append(self.visit(node.value))
        return " = ".join(operands)

    def visit_Return(self, node: ast.Return) -> str:
        return (
            self.visit(node.value)
            if node.value is not None
            else self._convert_constant(None)
        )

    def visit_Tuple(self, node: ast.Tuple) -> str:
        elts = [self.visit(i) for i in node.elts]
        return r"\mathopen{}\left( " + r", ".join(elts) + r" \mathclose{}\right)"

    def visit_List(self, node: ast.List) -> str:
        elts = [self.visit(i) for i in node.elts]
        return r"\mathopen{}\left[ " + r", ".join(elts) + r" \mathclose{}\right]"

    def visit_Set(self, node: ast.Set) -> str:
        elts = [self.visit(i) for i in node.elts]
        return r"\mathopen{}\left\{ " + r", ".join(elts) + r" \mathclose{}\right\}"

    def visit_ListComp(self, node: ast.ListComp) -> str:
        generators = [self.visit(comp) for comp in node.generators]
        return (
            r"\mathopen{}\left[ "
            + self.visit(node.elt)
            + r" \mid "
            + ", ".join(generators)
            + r" \mathclose{}\right]"
        )

    def visit_SetComp(self, node: ast.SetComp) -> str:
        generators = [self.visit(comp) for comp in node.generators]
        return (
            r"\mathopen{}\left\{ "
            + self.visit(node.elt)
            + r" \mid "
            + ", ".join(generators)
            + r" \mathclose{}\right\}"
        )

    def visit_comprehension(self, node: ast.comprehension) -> str:
        target = rf"{self.visit(node.target)} \in {self.visit(node.iter)}"

        if not node.ifs:
            # Returns the source without parenthesis.
            return target

        conds = [target] + [self.visit(cond) for cond in node.ifs]
        wrapped = [r"\mathopen{}\left( " + s + r" \mathclose{}\right)" for s in conds]
        return r" \land ".join(wrapped)

    def _generate_sum_prod(self, node: ast.Call) -> str | None:
        """Generates sum/prod expression.

        Args:
            node: ast.Call node containing the sum/prod invocation.

        Returns:
            Generated LaTeX, or None if the node has unsupported syntax.
        """
        if not isinstance(node.args[0], ast.GeneratorExp):
            return None

        name = ast_utils.extract_function_name_or_none(node)
        assert name in ("fsum", "sum", "prod")

        command = {
            "fsum": r"\sum",
            "sum": r"\sum",
            "prod": r"\prod",
        }[name]

        elt, scripts = self._get_sum_prod_info(node.args[0])
        scripts_str = [rf"{command}_{{{lo}}}^{{{up}}}" for lo, up in scripts]
        return (
            " ".join(scripts_str)
            + rf" \mathopen{{}}\left({{{elt}}}\mathclose{{}}\right)"
        )

    def _generate_matrix(self, node: ast.Call) -> str | None:
        """Generates matrix expression.

        Args:
            node: ast.Call node containing the ndarray invocation.

        Returns:
            Generated LaTeX, or None if the node has unsupported syntax.
        """

        def generate_matrix_from_array(data: list[list[str]]) -> str:
            """Helper to generate a bmatrix environment."""
            contents = r" \\ ".join(" & ".join(row) for row in data)
            return r"\begin{bmatrix} " + contents + r" \end{bmatrix}"

        arg = node.args[0]
        if not isinstance(arg, ast.List) or not arg.elts:
            # Not an array or no rows
            return None

        row0 = arg.elts[0]

        if not isinstance(row0, ast.List):
            # Maybe 1 x N array
            return generate_matrix_from_array([[self.visit(x) for x in arg.elts]])

        if not row0.elts:
            # No columns
            return None

        ncols = len(row0.elts)

        rows: list[list[str]] = []

        for row in arg.elts:
            if not isinstance(row, ast.List) or len(row.elts) != ncols:
                # Length mismatch
                return None

            rows.append([self.visit(x) for x in row.elts])

        return generate_matrix_from_array(rows)

    def _generate_zeros(self, node: ast.Call) -> str | None:
        """Generates LaTeX for numpy.zeros.

        Args:
            node: ast.Call node containing the appropriate method invocation.

        Returns:
            Generated LaTeX, or None if the node has unsupported syntax.
        """
        name = ast_utils.extract_function_name_or_none(node)
        assert name == "zeros"

        if len(node.args) != 1:
            return None

        # All args to np.zeros should be numeric.
        if isinstance(node.args[0], ast.Tuple):
            dims = [ast_utils.extract_int_or_none(x) for x in node.args[0].elts]
            if any(x is None for x in dims):
                return None
            if not dims:
                return "0"
            if len(dims) == 1:
                dims = [1, dims[0]]

            dims_latex = r" \times ".join(str(x) for x in dims)
        else:
            dim = ast_utils.extract_int_or_none(node.args[0])
            if not isinstance(dim, int):
                return None
            # 1 x N array of zeros
            dims_latex = rf"1 \times {dim}"

        return rf"\mathbf{{0}}^{{{dims_latex}}}"

    def _generate_identity(self, node: ast.Call) -> str | None:
        """Generates LaTeX for numpy.identity.

        Args:
            node: ast.Call node containing the appropriate method invocation.

        Returns:
            Generated LaTeX, or None if the node has unsupported syntax.
        """
        name = ast_utils.extract_function_name_or_none(node)
        assert name == "identity"

        if len(node.args) != 1:
            return None

        ndims = ast_utils.extract_int_or_none(node.args[0])
        if ndims is None:
            return None

        return rf"\mathbf{{I}}_{{{ndims}}}"

    def visit_Call(self, node: ast.Call) -> str:
        """Visit a call node."""
        func_name = ast_utils.extract_function_name_or_none(node)

        # Special treatments for some functions.
        # TODO(odashi): Move these functions to some separate utility.
        if func_name in ("fsum", "sum", "prod"):
            special_latex = self._generate_sum_prod(node)
        elif func_name in ("array", "ndarray"):
            special_latex = self._generate_matrix(node)
        elif func_name == "zeros":
            special_latex = self._generate_zeros(node)
        elif func_name == "identity":
            special_latex = self._generate_identity(node)
        else:
            special_latex = None

        if special_latex is not None:
            return special_latex

        # Obtains the codegen rule.
        rule = constants.BUILTIN_FUNCS.get(func_name) if func_name is not None else None

        if rule is None:
            rule = constants.FunctionRule(self.visit(node.func))

        if rule.is_unary and len(node.args) == 1:
            # Unary function. Applies the same wrapping policy with the unary operators.
            # NOTE(odashi):
            # Factorial "x!" is treated as a special case: it requires both inner/outer
            # parentheses for correct interpretation.
            precedence = _get_precedence(node)
            arg = node.args[0]
            force_wrap = isinstance(arg, ast.Call) and (
                func_name == "factorial"
                or ast_utils.extract_function_name_or_none(arg) == "factorial"
            )
            arg_latex = self._wrap_operand(arg, precedence, force_wrap)
            elements = [rule.left, arg_latex, rule.right]
        else:
            arg_latex = ", ".join(self.visit(arg) for arg in node.args)
            if rule.is_wrapped:
                elements = [rule.left, arg_latex, rule.right]
            else:
                elements = [
                    rule.left,
                    r"\mathopen{}\left(",
                    arg_latex,
                    r"\mathclose{}\right)",
                    rule.right,
                ]

        return " ".join(x for x in elements if x)

    def visit_Attribute(self, node: ast.Attribute) -> str:
        vstr = self.visit(node.value)
        astr = self._identifier_converter.convert(node.attr)[0]
        return vstr + "." + astr

    def visit_Name(self, node: ast.Name) -> str:
        return self._identifier_converter.convert(node.id)[0]

    def _convert_constant(self, value: Any) -> str:
        """Helper to convert constant values to LaTeX.

        Args:
            value: A constant value.

        Returns:
            The LaTeX representation of `value`.
        """
        if value is None or isinstance(value, bool):
            return r"\mathrm{" + str(value) + "}"
        if isinstance(value, (int, float, complex)):
            # TODO(odashi): Support other symbols for the imaginary unit than j.
            return str(value)
        if isinstance(value, str):
            return r'\textrm{"' + value + '"}'
        if isinstance(value, bytes):
            return r"\textrm{" + str(value) + "}"
        if value is ...:
            return r"\cdots"
        raise exceptions.LatexifyNotSupportedError(
            f"Unrecognized constant: {type(value).__name__}"
        )

    # From Python 3.8
    def visit_Constant(self, node: ast.Constant) -> str:
        return self._convert_constant(node.value)

    # Until Python 3.7
    def visit_Num(self, node: ast.Num) -> str:
        return self._convert_constant(node.n)

    # Until Python 3.7
    def visit_Str(self, node: ast.Str) -> str:
        return self._convert_constant(node.s)

    # Until Python 3.7
    def visit_Bytes(self, node: ast.Bytes) -> str:
        return self._convert_constant(node.s)

    # Until Python 3.7
    def visit_NameConstant(self, node: ast.NameConstant) -> str:
        return self._convert_constant(node.value)

    # Until Python 3.7
    def visit_Ellipsis(self, node: ast.Ellipsis) -> str:
        return self._convert_constant(...)

    def _wrap_operand(
        self, child: ast.expr, parent_prec: int, force_wrap: bool = False
    ) -> str:
        """Wraps the operand subtree with parentheses.

        Args:
            child: Operand subtree.
            parent_prec: Precedence of the parent operator.
            force_wrap: Whether to wrap the operand or not when the precedence is equal.

        Returns:
            LaTeX form of `child`, with or without surrounding parentheses.
        """
        latex = self.visit(child)
        child_prec = _get_precedence(child)

        if child_prec < parent_prec or force_wrap and child_prec == parent_prec:
            return rf"\mathopen{{}}\left( {latex} \mathclose{{}}\right)"

        return latex

    def _wrap_binop_operand(
        self,
        child: ast.expr,
        parent_prec: int,
        operand_rule: BinOperandRule,
    ) -> str:
        """Wraps the operand subtree of BinOp with parentheses.

        Args:
            child: Operand subtree.
            parent_prec: Precedence of the parent operator.
            operand_rule: Syntax rule of this operand.

        Returns:
            LaTeX form of the `child`, with or without surrounding parentheses.
        """
        if not operand_rule.wrap:
            return self.visit(child)

        if isinstance(child, ast.Call):
            child_fn_name = ast_utils.extract_function_name_or_none(child)
            rule = (
                constants.BUILTIN_FUNCS.get(child_fn_name)
                if child_fn_name is not None
                else None
            )
            if rule is not None and rule.is_wrapped:
                return self.visit(child)

        if not isinstance(child, ast.BinOp):
            return self._wrap_operand(child, parent_prec)

        latex = self.visit(child)

        if _BIN_OP_RULES[type(child.op)].is_wrapped:
            return latex

        child_prec = _get_precedence(child)

        if child_prec > parent_prec or (
            child_prec == parent_prec and not operand_rule.force
        ):
            return latex

        return rf"\mathopen{{}}\left( {latex} \mathclose{{}}\right)"

    def visit_BinOp(self, node: ast.BinOp) -> str:
        """Visit a BinOp node."""
        prec = _get_precedence(node)
        rule = self._bin_op_rules[type(node.op)]
        lhs = self._wrap_binop_operand(node.left, prec, rule.operand_left)
        rhs = self._wrap_binop_operand(node.right, prec, rule.operand_right)
        return f"{rule.latex_left}{lhs}{rule.latex_middle}{rhs}{rule.latex_right}"

    def visit_UnaryOp(self, node: ast.UnaryOp) -> str:
        """Visit a unary op node."""
        latex = self._wrap_operand(node.operand, _get_precedence(node))
        return _UNARY_OPS[type(node.op)] + latex

    def visit_Compare(self, node: ast.Compare) -> str:
        """Visit a compare node."""
        parent_prec = _get_precedence(node)
        lhs = self._wrap_operand(node.left, parent_prec)
        ops = [self._compare_ops[type(x)] for x in node.ops]
        rhs = [self._wrap_operand(x, parent_prec) for x in node.comparators]
        ops_rhs = [f" {o} {r}" for o, r in zip(ops, rhs)]
        return lhs + "".join(ops_rhs)

    def visit_BoolOp(self, node: ast.BoolOp) -> str:
        """Visit a BoolOp node."""
        parent_prec = _get_precedence(node)
        values = [self._wrap_operand(x, parent_prec) for x in node.values]
        op = f" {_BOOL_OPS[type(node.op)]} "
        return op.join(values)

    def visit_If(self, node: ast.If) -> str:
        """Visit an if node."""
        latex = r"\left\{ \begin{array}{ll} "

        current_stmt: ast.stmt = node

        while isinstance(current_stmt, ast.If):
            if len(current_stmt.body) != 1 or len(current_stmt.orelse) != 1:
                raise exceptions.LatexifySyntaxError(
                    "Multiple statements are not supported in If nodes."
                )

            cond_latex = self.visit(current_stmt.test)
            true_latex = self.visit(current_stmt.body[0])
            latex += true_latex + r", & \mathrm{if} \ " + cond_latex + r" \\ "
            current_stmt = current_stmt.orelse[0]

        latex += self.visit(current_stmt)
        return latex + r", & \mathrm{otherwise} \end{array} \right."

    def visit_IfExp(self, node: ast.IfExp) -> str:
        """Visit an ifexp node"""
        latex = r"\left\{ \begin{array}{ll} "

        current_expr: ast.expr = node

        while isinstance(current_expr, ast.IfExp):
            cond_latex = self.visit(current_expr.test)
            true_latex = self.visit(current_expr.body)
            latex += true_latex + r", & \mathrm{if} \ " + cond_latex + r" \\ "
            current_expr = current_expr.orelse

        latex += self.visit(current_expr)
        return latex + r", & \mathrm{otherwise} \end{array} \right."

    def visit_Match(self, node: ast.Match) -> str:
        """Visit a match node"""
        latex = r"\left\{ \begin{array}{ll}"
        subject_latex = self.visit(node.subject)
        for match_case in node.cases:
            if not (
                len(match_case.body) == 1 and isinstance(match_case.body[0], ast.Return)
            ):
                raise exceptions.LatexifyNotSupportedError(
                    "Match cases must have exactly 1 return statement."
                )
            true_latex = self.visit(match_case.body[0])
            cond_latex = self.visit(match_case.pattern)
            latex += (
                true_latex
                + r", & \mathrm{if} \ "
                + subject_latex
                + cond_latex
                + r" \\ "
            )

        latex += r"\end{array} \right."
        return latex

    def visit_MatchValue(self, node: ast.MatchValue) -> str:
        """Visit a MatchValue node"""
        latex = self.visit(node.value)
        return " = " + latex

    def _reduce_stop_parameter(self, node: ast.expr) -> ast.expr:
        """Adjusts the stop expression of the range.

        This function tries to convert the syntax as follows:
            * n + 1 --> n
            * n + 2 --> n + 1
            * n - (-1) --> n
            * n - 1 --> n - 2

        Args:
            node: The target expression.

        Returns:
            Converted expression.
        """
        if not (
            isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub))
        ):
            return ast.BinOp(left=node, op=ast.Sub(), right=ast_utils.make_constant(1))

        # Treatment for Python 3.7.
        rhs = (
            ast.Constant(value=node.right.n)
            if sys.version_info.minor < 8 and isinstance(node.right, ast.Num)
            else node.right
        )

        if not isinstance(rhs, ast.Constant):
            return ast.BinOp(left=node, op=ast.Sub(), right=ast_utils.make_constant(1))

        shift = 1 if isinstance(node.op, ast.Add) else -1

        return (
            node.left
            if rhs.value == shift
            else ast.BinOp(
                left=node.left, op=node.op, right=ast.Constant(value=rhs.value - shift)
            )
        )

    def _get_sum_prod_range(self, node: ast.comprehension) -> tuple[str, str] | None:
        """Helper to process range(...) for sum and prod functions.

        Args:
            node: comprehension node to be analyzed.

        Returns:
            Tuple of following strings:
                - lower_rhs
                - upper
            which are used in _get_sum_prod_info, or None if the analysis failed.
        """
        if not (
            isinstance(node.iter, ast.Call)
            and isinstance(node.iter.func, ast.Name)
            and node.iter.func.id == "range"
        ):
            return None

        try:
            range_info = analyzers.analyze_range(node.iter)
        except exceptions.LatexifyError:
            return None

        if (
            # Only accepts ascending order with step size 1.
            range_info.step_int != 1
            or (
                range_info.start_int is not None
                and range_info.stop_int is not None
                and range_info.start_int >= range_info.stop_int
            )
        ):
            return None

        if range_info.start_int is None:
            lower_rhs = self.visit(range_info.start)
        else:
            lower_rhs = str(range_info.start_int)

        if range_info.stop_int is None:
            upper = self.visit(self._reduce_stop_parameter(range_info.stop))
        else:
            upper = str(range_info.stop_int - 1)

        return lower_rhs, upper

    def _get_sum_prod_info(
        self, node: ast.GeneratorExp
    ) -> tuple[str, list[tuple[str, str]]]:
        r"""Process GeneratorExp for sum and prod functions.

        Args:
            node: GeneratorExp node to be analyzed.

        Returns:
            Tuple of following strings:
                - elt
                - scripts
            which are used to represent sum/prod operators as follows:
                \sum_{scripts[0][0]}^{scripts[0][1]}
                    \sum_{scripts[1][0]}^{scripts[1][1]}
                    ...
                    {elt}

        Raises:
            LateixfyError: Unsupported AST is given.
        """
        elt = self.visit(node.elt)

        scripts: list[tuple[str, str]] = []

        for comp in node.generators:
            range_args = self._get_sum_prod_range(comp)

            if range_args is not None and not comp.ifs:
                target = self.visit(comp.target)
                lower_rhs, upper = range_args
                lower = f"{target} = {lower_rhs}"
            else:
                lower = self.visit(comp)  # Use a usual comprehension form.
                upper = ""

            scripts.append((lower, upper))

        return elt, scripts

    # Until 3.8
    def visit_Index(self, node: ast.Index) -> str:
        """Visitor for the Index nodes."""
        return self.visit(node.value)  # type: ignore[attr-defined]

    def _convert_nested_subscripts(self, node: ast.Subscript) -> tuple[str, list[str]]:
        """Helper function to convert nested subscription.

        This function converts x[i][j][...] to "x" and ["i", "j", ...]

        Args:
            node: ast.Subscript node to be converted.

        Returns:
            Tuple of following strings:
                - The root value of the subscription.
                - Sequence of incices.
        """
        if isinstance(node.value, ast.Subscript):
            value, indices = self._convert_nested_subscripts(node.value)
        else:
            value = self.visit(node.value)
            indices = []

        indices.append(self.visit(node.slice))
        return value, indices

    def visit_Subscript(self, node: ast.Subscript) -> str:
        """Visitor of the Subscript nodes."""
        value, indices = self._convert_nested_subscripts(node)

        # TODO(odashi):
        # "[i][j][...]" may be a possible representation as well as "i, j. ..."
        indices_str = ", ".join(indices)

        return f"{value}_{{{indices_str}}}"
