"""Codegen for single expressions."""

from __future__ import annotations

import ast
import re

from latexify import analyzers, ast_utils, exceptions
from latexify.codegen import codegen_utils, expression_rules, identifier_converter


class ExpressionCodegen(ast.NodeVisitor):
    """Codegen for single expressions."""

    _identifier_converter: identifier_converter.IdentifierConverter

    _bin_op_rules: dict[type[ast.operator], expression_rules.BinOpRule]
    _compare_ops: dict[type[ast.cmpop], str]

    def __init__(
        self, *, use_math_symbols: bool = False, use_set_symbols: bool = False
    ) -> None:
        """Initializer.

        Args:
            use_math_symbols: Whether to convert identifiers with a math symbol
                surface (e.g., "alpha") to the LaTeX symbol (e.g., "\\alpha").
            use_set_symbols: Whether to use set symbols or not.
        """
        self._identifier_converter = identifier_converter.IdentifierConverter(
            use_math_symbols=use_math_symbols
        )

        self._bin_op_rules = (
            expression_rules.SET_BIN_OP_RULES
            if use_set_symbols
            else expression_rules.BIN_OP_RULES
        )
        self._compare_ops = (
            expression_rules.SET_COMPARE_OPS
            if use_set_symbols
            else expression_rules.COMPARE_OPS
        )

    def generic_visit(self, node: ast.AST) -> str:
        raise exceptions.LatexifyNotSupportedError(
            f"Unsupported AST: {type(node).__name__}"
        )

    def visit_Tuple(self, node: ast.Tuple) -> str:
        """Visit a Tuple node."""
        elts = [self.visit(elt) for elt in node.elts]
        return r"\mathopen{}\left( " + r", ".join(elts) + r" \mathclose{}\right)"

    def visit_List(self, node: ast.List) -> str:
        """Visit a List node."""
        elts = [self.visit(elt) for elt in node.elts]
        return r"\mathopen{}\left[ " + r", ".join(elts) + r" \mathclose{}\right]"

    def visit_Set(self, node: ast.Set) -> str:
        """Visit a Set node."""
        elts = [self.visit(elt) for elt in node.elts]
        return r"\mathopen{}\left\{ " + r", ".join(elts) + r" \mathclose{}\right\}"

    def visit_ListComp(self, node: ast.ListComp) -> str:
        """Visit a ListComp node."""
        generators = [self.visit(comp) for comp in node.generators]
        return (
            r"\mathopen{}\left[ "
            + self.visit(node.elt)
            + r" \mid "
            + ", ".join(generators)
            + r" \mathclose{}\right]"
        )

    def visit_SetComp(self, node: ast.SetComp) -> str:
        """Visit a SetComp node."""
        generators = [self.visit(comp) for comp in node.generators]
        return (
            r"\mathopen{}\left\{ "
            + self.visit(node.elt)
            + r" \mid "
            + ", ".join(generators)
            + r" \mathclose{}\right\}"
        )

    def visit_comprehension(self, node: ast.comprehension) -> str:
        """Visit a comprehension node."""
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
        if not node.args or not isinstance(node.args[0], ast.GeneratorExp):
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

    def _generate_transpose(self, node: ast.Call) -> str | None:
        """Generates LaTeX for numpy.transpose.
        Args:
            node: ast.Call node containing the appropriate method invocation.
        Returns:
            Generated LaTeX, or None if the node has unsupported syntax.
        Raises:
            LatexifyError: Unsupported argument type given.
        """
        name = ast_utils.extract_function_name_or_none(node)
        assert name == "transpose"

        if len(node.args) != 1:
            return None

        func_arg = node.args[0]
        if isinstance(func_arg, ast.Name):
            return rf"\mathbf{{{func_arg.id}}}^\intercal"
        else:
            return None

    def _generate_determinant(self, node: ast.Call) -> str | None:
        """Generates LaTeX for numpy.linalg.det.
        Args:
            node: ast.Call node containing the appropriate method invocation.
        Returns:
            Generated LaTeX, or None if the node has unsupported syntax.
        Raises:
            LatexifyError: Unsupported argument type given.
        """
        name = ast_utils.extract_function_name_or_none(node)
        assert name == "det"

        if len(node.args) != 1:
            return None

        func_arg = node.args[0]
        if isinstance(func_arg, ast.Name):
            arg_id = rf"\mathbf{{{func_arg.id}}}"
            return rf"\det \mathopen{{}}\left( {arg_id} \mathclose{{}}\right)"
        elif isinstance(func_arg, ast.List):
            matrix = self._generate_matrix(node)
            return rf"\det \mathopen{{}}\left( {matrix} \mathclose{{}}\right)"

        return None

    def _generate_matrix_rank(self, node: ast.Call) -> str | None:
        """Generates LaTeX for numpy.linalg.matrix_rank.
        Args:
            node: ast.Call node containing the appropriate method invocation.
        Returns:
            Generated LaTeX, or None if the node has unsupported syntax.
        Raises:
            LatexifyError: Unsupported argument type given.
        """
        name = ast_utils.extract_function_name_or_none(node)
        assert name == "matrix_rank"

        if len(node.args) != 1:
            return None

        func_arg = node.args[0]
        if isinstance(func_arg, ast.Name):
            arg_id = rf"\mathbf{{{func_arg.id}}}"
            return (
                rf"\mathrm{{rank}} \mathopen{{}}\left( {arg_id} \mathclose{{}}\right)"
            )
        elif isinstance(func_arg, ast.List):
            matrix = self._generate_matrix(node)
            return (
                rf"\mathrm{{rank}} \mathopen{{}}\left( {matrix} \mathclose{{}}\right)"
            )

        return None

    def _generate_matrix_power(self, node: ast.Call) -> str | None:
        """Generates LaTeX for numpy.linalg.matrix_power.
        Args:
            node: ast.Call node containing the appropriate method invocation.
        Returns:
            Generated LaTeX, or None if the node has unsupported syntax.
        Raises:
            LatexifyError: Unsupported argument type given.
        """
        name = ast_utils.extract_function_name_or_none(node)
        assert name == "matrix_power"

        if len(node.args) != 2:
            return None

        func_arg = node.args[0]
        power_arg = node.args[1]
        if isinstance(power_arg, ast.Num):
            if isinstance(func_arg, ast.Name):
                return rf"\mathbf{{{func_arg.id}}}^{{{power_arg.n}}}"
            elif isinstance(func_arg, ast.List):
                matrix = self._generate_matrix(node)
                if matrix is not None:
                    return rf"{matrix}^{{{power_arg.n}}}"
        return None

    def _generate_inv(self, node: ast.Call) -> str | None:
        """Generates LaTeX for numpy.linalg.inv.
        Args:
            node: ast.Call node containing the appropriate method invocation.
        Returns:
            Generated LaTeX, or None if the node has unsupported syntax.
        Raises:
            LatexifyError: Unsupported argument type given.
        """
        name = ast_utils.extract_function_name_or_none(node)
        assert name == "inv"

        if len(node.args) != 1:
            return None

        func_arg = node.args[0]
        if isinstance(func_arg, ast.Name):
            return rf"\mathbf{{{func_arg.id}}}^{{-1}}"
        elif isinstance(func_arg, ast.List):
            return rf"{self._generate_matrix(node)}^{{-1}}"
        return None

    def _generate_pinv(self, node: ast.Call) -> str | None:
        """Generates LaTeX for numpy.linalg.pinv.
        Args:
            node: ast.Call node containing the appropriate method invocation.
        Returns:
            Generated LaTeX, or None if the node has unsupported syntax.
        Raises:
            LatexifyError: Unsupported argument type given.
        """
        name = ast_utils.extract_function_name_or_none(node)
        assert name == "pinv"

        if len(node.args) != 1:
            return None

        func_arg = node.args[0]
        if isinstance(func_arg, ast.Name):
            return rf"\mathbf{{{func_arg.id}}}^{{+}}"
        elif isinstance(func_arg, ast.List):
            return rf"{self._generate_matrix(node)}^{{+}}"
        return None

    def visit_Call(self, node: ast.Call) -> str:
        """Visit a Call node."""
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
        elif func_name == "transpose":
            special_latex = self._generate_transpose(node)
        elif func_name == "det":
            special_latex = self._generate_determinant(node)
        elif func_name == "matrix_rank":
            special_latex = self._generate_matrix_rank(node)
        elif func_name == "matrix_power":
            special_latex = self._generate_matrix_power(node)
        elif func_name == "inv":
            special_latex = self._generate_inv(node)
        elif func_name == "pinv":
            special_latex = self._generate_pinv(node)
        else:
            special_latex = None

        if special_latex is not None:
            return special_latex

        # Obtains the codegen rule.
        rule = (
            expression_rules.BUILTIN_FUNCS.get(func_name)
            if func_name is not None
            else None
        )

        if rule is None:
            rule = expression_rules.FunctionRule(self.visit(node.func))

        if rule.is_unary and len(node.args) == 1:
            # Unary function. Applies the same wrapping policy with the unary operators.
            precedence = expression_rules.get_precedence(node)
            arg = node.args[0]
            # NOTE(odashi):
            # Factorial "x!" is treated as a special case: it requires both inner/outer
            # parentheses for correct interpretation.
            force_wrap_factorial = isinstance(arg, ast.Call) and (
                func_name == "factorial"
                or ast_utils.extract_function_name_or_none(arg) == "factorial"
            )
            # Note(odashi):
            # Wrapping is also required if the argument is pow.
            # https://github.com/google/latexify_py/issues/189
            force_wrap_pow = isinstance(arg, ast.BinOp) and isinstance(arg.op, ast.Pow)
            arg_latex = self._wrap_operand(
                arg, precedence, force_wrap_factorial or force_wrap_pow
            )
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
        """Visit an Attribute node."""
        vstr = self.visit(node.value)
        astr = self._identifier_converter.convert(node.attr)[0]
        return vstr + "." + astr

    def visit_Name(self, node: ast.Name) -> str:
        """Visit a Name node."""
        return self._identifier_converter.convert(node.id)[0]

    # From Python 3.8
    def visit_Constant(self, node: ast.Constant) -> str:
        """Visit a Constant node."""
        return codegen_utils.convert_constant(node.value)

    # Until Python 3.7
    def visit_Num(self, node: ast.Num) -> str:
        """Visit a Num node."""
        return codegen_utils.convert_constant(node.n)

    # Until Python 3.7
    def visit_Str(self, node: ast.Str) -> str:
        """Visit a Str node."""
        return codegen_utils.convert_constant(node.s)

    # Until Python 3.7
    def visit_Bytes(self, node: ast.Bytes) -> str:
        """Visit a Bytes node."""
        return codegen_utils.convert_constant(node.s)

    # Until Python 3.7
    def visit_NameConstant(self, node: ast.NameConstant) -> str:
        """Visit a NameConstant node."""
        return codegen_utils.convert_constant(node.value)

    # Until Python 3.7
    def visit_Ellipsis(self, node: ast.Ellipsis) -> str:
        """Visit an Ellipsis node."""
        return codegen_utils.convert_constant(...)

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
        child_prec = expression_rules.get_precedence(child)

        if force_wrap or child_prec < parent_prec:
            return rf"\mathopen{{}}\left( {latex} \mathclose{{}}\right)"

        return latex

    def _wrap_binop_operand(
        self,
        child: ast.expr,
        parent_prec: int,
        operand_rule: expression_rules.BinOperandRule,
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
                expression_rules.BUILTIN_FUNCS.get(child_fn_name)
                if child_fn_name is not None
                else None
            )
            if rule is not None and rule.is_wrapped:
                return self.visit(child)

        if not isinstance(child, ast.BinOp):
            return self._wrap_operand(child, parent_prec)

        latex = self.visit(child)

        if expression_rules.BIN_OP_RULES[type(child.op)].is_wrapped:
            return latex

        child_prec = expression_rules.get_precedence(child)

        if child_prec > parent_prec or (
            child_prec == parent_prec and not operand_rule.force
        ):
            return latex

        return rf"\mathopen{{}}\left( {latex} \mathclose{{}}\right)"

    _l_bracket_pattern = re.compile(r"^\\mathopen.*")
    _r_bracket_pattern = re.compile(r".*\\mathclose[^ ]+$")
    _r_word_pattern = re.compile(r"\\mathrm\{[^ ]+\}$")

    def _should_remove_multiply_op(
        self, l_latex: str, r_latex: str, l_expr: ast.expr, r_expr: ast.expr
    ):
        """Determine whether the multiply operator should be removed or not.

        See also:
        https://github.com/google/latexify_py/issues/89#issuecomment-1344967636

        This is an ad-hoc implementation.
        This function doesn't fully implements the above requirements, but only
        essential ones necessary to release v0.3.
        """

        # NOTE(odashi): For compatibility with Python 3.7, we compare the generated
        # caracter type directly to determine the "numeric" type.

        if isinstance(l_expr, ast.Call):
            l_type = "f"
        elif self._r_bracket_pattern.match(l_latex):
            l_type = "b"
        elif self._r_word_pattern.match(l_latex):
            l_type = "w"
        elif l_latex[-1].isnumeric():
            l_type = "n"
        else:
            le = l_expr
            while True:
                if isinstance(le, ast.UnaryOp):
                    le = le.operand
                elif isinstance(le, ast.BinOp):
                    le = le.right
                elif isinstance(le, ast.Compare):
                    le = le.comparators[-1]
                elif isinstance(le, ast.BoolOp):
                    le = le.values[-1]
                else:
                    break
            l_type = "a" if isinstance(le, ast.Name) and len(le.id) == 1 else "m"

        if isinstance(r_expr, ast.Call):
            r_type = "f"
        elif self._l_bracket_pattern.match(r_latex):
            r_type = "b"
        elif r_latex.startswith("\\mathrm"):
            r_type = "w"
        elif r_latex[0].isnumeric():
            r_type = "n"
        else:
            re = r_expr
            while True:
                if isinstance(re, ast.UnaryOp):
                    if isinstance(re.op, ast.USub):
                        # NOTE(odashi): Unary "-" always require \cdot.
                        return False
                    re = re.operand
                elif isinstance(re, ast.BinOp):
                    re = re.left
                elif isinstance(re, ast.Compare):
                    re = re.left
                elif isinstance(re, ast.BoolOp):
                    re = re.values[0]
                else:
                    break
            r_type = "a" if isinstance(re, ast.Name) and len(re.id) == 1 else "m"

        if r_type == "n":
            return False
        if l_type in "bn":
            return True
        if l_type in "am" and r_type in "am":
            return True
        return False

    def visit_BinOp(self, node: ast.BinOp) -> str:
        """Visit a BinOp node."""
        prec = expression_rules.get_precedence(node)
        rule = self._bin_op_rules[type(node.op)]
        lhs = self._wrap_binop_operand(node.left, prec, rule.operand_left)
        rhs = self._wrap_binop_operand(node.right, prec, rule.operand_right)

        if type(node.op) in [ast.Mult, ast.MatMult]:
            if self._should_remove_multiply_op(lhs, rhs, node.left, node.right):
                return f"{rule.latex_left}{lhs} {rhs}{rule.latex_right}"

        return f"{rule.latex_left}{lhs}{rule.latex_middle}{rhs}{rule.latex_right}"

    def visit_UnaryOp(self, node: ast.UnaryOp) -> str:
        """Visit a UnaryOp node."""
        latex = self._wrap_operand(node.operand, expression_rules.get_precedence(node))
        return expression_rules.UNARY_OPS[type(node.op)] + latex

    def visit_Compare(self, node: ast.Compare) -> str:
        """Visit a Compare node."""
        parent_prec = expression_rules.get_precedence(node)
        lhs = self._wrap_operand(node.left, parent_prec)
        ops = [self._compare_ops[type(x)] for x in node.ops]
        rhs = [self._wrap_operand(x, parent_prec) for x in node.comparators]
        ops_rhs = [f" {o} {r}" for o, r in zip(ops, rhs)]
        return lhs + "".join(ops_rhs)

    def visit_BoolOp(self, node: ast.BoolOp) -> str:
        """Visit a BoolOp node."""
        parent_prec = expression_rules.get_precedence(node)
        values = [self._wrap_operand(x, parent_prec) for x in node.values]
        op = f" {expression_rules.BOOL_OPS[type(node.op)]} "
        return op.join(values)

    def visit_IfExp(self, node: ast.IfExp) -> str:
        """Visit an IfExp node"""
        latex = r"\left\{ \begin{array}{ll} "

        current_expr: ast.expr = node

        while isinstance(current_expr, ast.IfExp):
            cond_latex = self.visit(current_expr.test)
            true_latex = self.visit(current_expr.body)
            latex += true_latex + r", & \mathrm{if} \ " + cond_latex + r" \\ "
            current_expr = current_expr.orelse

        latex += self.visit(current_expr)
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
            lower_rhs = str(range_info.start_int)

        if range_info.stop_int is None:
            upper = self.visit(analyzers.reduce_stop_parameter(range_info.stop))
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
        """Visit an Index node."""
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
        """Visitor a Subscript node."""
        value, indices = self._convert_nested_subscripts(node)

        # TODO(odashi):
        # "[i][j][...]" may be a possible representation as well as "i, j. ..."
        indices_str = ", ".join(indices)

        return f"{value}_{{{indices_str}}}"
