"""Codegen for single function."""

from __future__ import annotations

import ast
import dataclasses
from typing import Any

from latexify import analyzers
from latexify import constants
from latexify import math_symbols
from latexify import exceptions


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


def _get_precedence(node: ast.AST) -> int:
    """Obtains the precedence of the subtree.

    Args:
        node: Subtree to investigate.

    Returns:
        If `node` is a subtree with some operator, returns the precedence of the
        operator. Otherwise, returns a number larger enough from other precedences.
    """
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

_BOOL_OPS: dict[type[ast.boolop], str] = {
    ast.And: r"\land",
    ast.Or: r"\lor",
}


class FunctionCodegen(ast.NodeVisitor):
    """Codegen for single functions.

    This codegen works for Module with single FunctionDef node to generate a single
    LaTeX expression of the given function.
    """

    _math_symbol_converter: math_symbols.MathSymbolConverter
    _use_raw_function_name: bool
    _use_signature: bool

    def __init__(
        self,
        *,
        use_math_symbols: bool = False,
        use_raw_function_name: bool = False,
        use_signature: bool = True,
    ) -> None:
        """Initializer.

        Args:
            use_math_symbols: Whether to convert identifiers with a math symbol surface
                (e.g., "alpha") to the LaTeX symbol (e.g., "\\alpha").
            use_raw_function_name: Whether to keep underscores "_" in the function name,
                or convert it to subscript.
            use_signature: Whether to add the function signature before the expression
                or not.
        """
        self._math_symbol_converter = math_symbols.MathSymbolConverter(
            enabled=use_math_symbols
        )
        self._use_raw_function_name = use_raw_function_name
        self._use_signature = use_signature

    def generic_visit(self, node: ast.AST) -> str:
        raise exceptions.LatexifyNotSupportedError(
            f"Unsupported AST: {type(node).__name__}"
        )

    def visit_Module(self, node: ast.Module) -> str:
        return self.visit(node.body[0])

    def visit_FunctionDef(self, node: ast.FunctionDef) -> str:
        # Function name
        name_str = str(node.name)
        if self._use_raw_function_name:
            name_str = name_str.replace(r"_", r"\_")
        name_str = r"\mathrm{" + name_str + "}"

        # Arguments
        arg_strs = [
            self._math_symbol_converter.convert(str(arg.arg)) for arg in node.args.args
        ]

        body_strs: list[str] = []

        # Assignment statements (if any): x = ...
        for child in node.body[:-1]:
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
        return self.visit(node.value)

    def visit_Tuple(self, node: ast.Tuple) -> str:
        elts = [self.visit(i) for i in node.elts]
        return r"\left( " + r"\space,\space ".join(elts) + r"\right) "

    def visit_List(self, node: ast.List) -> str:
        elts = [self.visit(i) for i in node.elts]
        return r"\left[ " + r"\space,\space ".join(elts) + r"\right] "

    def visit_Set(self, node: ast.Set) -> str:
        elts = [self.visit(i) for i in node.elts]
        return r"\left\{ " + r"\space,\space ".join(elts) + r"\right\} "

    def visit_ListComp(self, node: ast.ListComp) -> str:
        generators = [self.visit(comp) for comp in node.generators]
        return (
            r"\left[ "
            + self.visit(node.elt)
            + r" \mid "
            + ", ".join(generators)
            + r" \right]"
        )

    def visit_SetComp(self, node: ast.SetComp) -> str:
        generators = [self.visit(comp) for comp in node.generators]
        return (
            r"\left\{ "
            + self.visit(node.elt)
            + r" \mid "
            + ", ".join(generators)
            + r" \right\}"
        )

    def visit_comprehension(self, node: ast.comprehension) -> str:
        target = rf"{self.visit(node.target)} \in {self.visit(node.iter)}"

        if not node.ifs:
            # Returns the source without parenthesis.
            return target

        conds = [target] + [self.visit(cond) for cond in node.ifs]
        wrapped = [r"\left( " + s + r" \right)" for s in conds]
        return r" \land ".join(wrapped)

    def visit_Call(self, node: ast.Call) -> str:
        """Visit a call node."""
        # Function signature (possibly an expression).
        func_str = self.visit(node.func)

        # Removes common prefixes: math.sqrt -> sqrt
        # TODO(odashi): This process can be implemented as a NodeTransformer.
        for prefix in constants.PREFIXES:
            if func_str.startswith(f"{prefix}."):
                func_str = func_str[len(prefix) + 1 :]
                break

        # Obtains wrapper syntax: sqrt -> "\sqrt{" and "}"
        lstr, rstr = constants.BUILTIN_FUNCS.get(
            func_str,
            (r"\mathrm{" + func_str + r"}\left(", r"\right)"),
        )

        if func_str in ("sum", "prod") and isinstance(node.args[0], ast.GeneratorExp):
            elt, scripts = self._get_sum_prod_info(node.args[0])
            scripts_str = [rf"\{func_str}_{{{lo}}}^{{{up}}}" for lo, up in scripts]
            return " ".join(scripts_str) + rf" \left({{{elt}}}\right)"

        arg_strs = [self.visit(arg) for arg in node.args]
        return lstr + ", ".join(arg_strs) + rstr

    def visit_Attribute(self, node: ast.Attribute) -> str:
        vstr = self.visit(node.value)
        astr = str(node.attr)
        return vstr + "." + astr

    def visit_Name(self, node: ast.Name) -> str:
        return self._math_symbol_converter.convert(str(node.id))

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
            return "{" + str(value) + "}"
        if isinstance(value, str):
            return r'\textrm{"' + value + '"}'
        if isinstance(value, bytes):
            return r"\textrm{" + str(value) + "}"
        if value is ...:
            return r"{\cdots}"
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

    def _wrap_operand(self, child: ast.expr, parent_prec: int) -> str:
        """Wraps the operand subtree with parentheses.

        Args:
            child: Operand subtree.
            parent_prec: Precedence of the parent operator.

        Returns:
            LaTeX form of `child`, with or without surrounding parentheses.
        """
        latex = self.visit(child)
        if _get_precedence(child) >= parent_prec:
            return latex
        return rf"\left( {latex} \right)"

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

        return rf"\left( {latex} \right)"

    def visit_BinOp(self, node: ast.BinOp) -> str:
        """Visit a BinOp node."""
        prec = _get_precedence(node)
        rule = _BIN_OP_RULES[type(node.op)]
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
        ops = [_COMPARE_OPS[type(x)] for x in node.ops]
        rhs = [self._wrap_operand(x, parent_prec) for x in node.comparators]
        ops_rhs = [f" {o} {r}" for o, r in zip(ops, rhs)]
        return "{" + lhs + "".join(ops_rhs) + "}"

    def visit_BoolOp(self, node: ast.BoolOp) -> str:
        """Visit a BoolOp node."""
        parent_prec = _get_precedence(node)
        values = [self._wrap_operand(x, parent_prec) for x in node.values]
        op = f" {_BOOL_OPS[type(node.op)]} "
        return "{" + op.join(values) + "}"

    def visit_If(self, node: ast.If) -> str:
        """Visit an if node."""
        latex = r"\left\{ \begin{array}{ll} "

        while isinstance(node, ast.If):
            if len(node.body) != 1 or len(node.orelse) != 1:
                raise exceptions.LatexifySyntaxError(
                    "Multiple statements are not supported in If nodes."
                )

            cond_latex = self.visit(node.test)
            true_latex = self.visit(node.body[0])
            latex += true_latex + r", & \mathrm{if} \ " + cond_latex + r" \\ "
            node = node.orelse[0]

        latex += self.visit(node)
        return latex + r", & \mathrm{otherwise} \end{array} \right."

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
            lower_rhs = f"{{{range_info.start_int}}}"

        if range_info.stop_int is None:
            upper = "{" + self.visit(range_info.stop) + " - 1}"
        else:
            upper = f"{{{range_info.stop_int - 1}}}"

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
        return self.visit(node.value)

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
        indices_str = "{" + ", ".join(indices) + "}"

        return f"{{{value}_{indices_str}}}"
