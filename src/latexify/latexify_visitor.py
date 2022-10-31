"""Latexify core AST visitor."""

from __future__ import annotations

import ast
from typing import Any, ClassVar

from latexify import constants
from latexify import math_symbols
from latexify import node_visitor_base
from latexify import exceptions


class LatexifyVisitor(node_visitor_base.NodeVisitorBase):
    """Latexify AST visitor."""

    _math_symbol_converter: math_symbols.MathSymbolConverter
    _use_raw_function_name: bool
    _reduce_assignments: bool

    # TODO(odashi): This variable can be function-level. Remove it from the object.
    _assign_var: dict[str, str]

    def __init__(
        self,
        *,
        reduce_assignments: bool = True,
        use_math_symbols: bool = False,
        use_raw_function_name: bool = False,
    ):
        """Initializer.

        Args:
            reduce_assignments: If True, assignment statements are used to synthesize
                the final expression.
            use_math_symbols: Whether to convert identifiers with a math symbol surface
                (e.g., "alpha") to the LaTeX symbol (e.g., "\\alpha").
            use_raw_function_name: Whether to keep underscores "_" in the function name,
                or convert it to subscript.
        """
        self._math_symbol_converter = math_symbols.MathSymbolConverter(
            enabled=use_math_symbols
        )
        self._use_raw_function_name = use_raw_function_name
        self._reduce_assignments = reduce_assignments

        self.assign_var = {}

    def generic_visit(self, node, action) -> str:
        raise exceptions.LatexifyNotSupportedError(
            f"Unsupported AST: {type(node).__name__}"
        )

    def visit_Module(self, node, action):  # pylint: disable=invalid-name
        return self.visit(node.body[0], "multi_lines")

    def visit_FunctionDef(self, node, action):  # pylint: disable=invalid-name
        name_str = str(node.name)
        if self._use_raw_function_name:
            name_str = name_str.replace(r"_", r"\_")
        name_str = r"\mathrm{" + name_str + "}"

        arg_strs = [
            self._math_symbol_converter.convert(str(arg.arg)) for arg in node.args.args
        ]

        body_str = ""
        assign_vars = []
        for el in node.body:
            if isinstance(el, ast.FunctionDef):
                if self._reduce_assignments:
                    body_str = self.visit(el, "in_line")
                    self.assign_var[el.name] = rf"\left( {body_str} \right)"
                else:
                    body_str = self.visit(el, "multi_lines")
                    assign_vars.append(body_str + r" \\ ")
            else:
                body_str = self.visit(el)
                if not self._reduce_assignments and isinstance(el, ast.Assign):
                    assign_vars.append(body_str)
                elif isinstance(el, ast.Return):
                    break
        if body_str == "":
            raise exceptions.LatexifySyntaxError("`return` missing")

        return name_str, arg_strs, assign_vars, body_str

    def visit_FunctionDef_multi_lines(self, node):
        name_str, arg_strs, assign_vars, body_str = self.visit_FunctionDef(node, None)
        return (
            "".join(assign_vars)
            + name_str
            + "("
            + ", ".join(arg_strs)
            + r") \triangleq "
            + body_str
        )

    def visit_FunctionDef_in_line(self, node):
        name_str, arg_strs, assign_vars, body_str = self.visit_FunctionDef(node, None)
        return "".join(assign_vars) + body_str

    def visit_Assign(self, node, action):
        var = self.visit(node.value)
        if self._reduce_assignments:
            self.assign_var[node.targets[0].id] = rf"\left( {var} \right)"
            return None
        else:
            return rf"{node.targets[0].id} \triangleq {var} \\ "

    def visit_Return(self, node, action):  # pylint: disable=invalid-name
        return self.visit(node.value)

    def visit_Tuple(self, node, action):  # pylint: disable=invalid-name
        elts = [self.visit(i) for i in node.elts]
        return r"\left( " + r"\space,\space ".join(elts) + r"\right) "

    def visit_List(self, node, action):  # pylint: disable=invalid-name
        elts = [self.visit(i) for i in node.elts]
        return r"\left[ " + r"\space,\space ".join(elts) + r"\right] "

    def visit_Set(self, node, action):  # pylint: disable=invalid-name
        elts = [self.visit(i) for i in node.elts]
        return r"\left\{ " + r"\space,\space ".join(elts) + r"\right\} "

    def visit_Call(self, node, action):  # pylint: disable=invalid-name
        """Visit a call node."""

        def _decorated_lstr_and_arg(node, callee_str, lstr):
            """Decorates lstr and get its associated arguments"""
            if callee_str == "sum" and isinstance(node.args[0], ast.GeneratorExp):
                generator_info = self.visit(node.args[0], "set_bounds")
                arg_str, comprehension = generator_info
                var_comp, args_comp = comprehension
                if len(args_comp) == 1:
                    arg1, arg2 = "0", args_comp[0]
                else:
                    arg1, arg2 = args_comp
                # the second arg in range func is exclusive
                try:
                    arg2 = str(int(arg2) - 1)
                except ValueError:
                    arg2 += "-1"

                decorator = r"_{{{}={}}}^{{{}}}".format(var_comp, arg1, arg2)
                lstr = r"\sum" + decorator + r" \left({"

            else:
                arg_strs = [self.visit(arg) for arg in node.args]
                arg_str = ", ".join(arg_strs)

            return lstr, arg_str

        callee_str = self.visit(node.func)
        if self._reduce_assignments and (
            getattr(node.func, "id", None) in self.assign_var.keys()
            or getattr(node.func, "attr", None) in self.assign_var.keys()
        ):
            return callee_str
        else:
            for prefix in constants.PREFIXES:
                if callee_str.startswith(f"{prefix}."):
                    callee_str = callee_str[len(prefix) + 1 :]
                    break

            lstr, rstr = constants.BUILTIN_CALLEES.get(callee_str, (None, None))
            if lstr is None:
                lstr = r"\mathrm{" + callee_str + r"}\left("
                rstr = r"\right)"

            lstr, arg_str = _decorated_lstr_and_arg(node, callee_str, lstr)
            return lstr + arg_str + rstr

    def visit_Attribute(self, node, action):  # pylint: disable=invalid-name
        vstr = self.visit(node.value)
        astr = str(node.attr)
        return vstr + "." + astr

    def visit_Name(self, node, action):  # pylint: disable=invalid-name
        if self._reduce_assignments and node.id in self.assign_var.keys():
            return self.assign_var[node.id]

        return self._math_symbol_converter.convert(str(node.id))

    def convert_constant(self, value: Any) -> str:
        """Helper to convert constant values to LaTeX.

        Args:
            value: A constant value.

        Returns:
            The LaTeX representation of `value`.
        """
        if value is None or isinstance(value, bool):
            return r"\mathrm{" + str(value) + "}"
        if isinstance(value, (int, float, complex)):
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
    def visit_Constant(self, node: ast.Constant, action) -> str:
        return self.convert_constant(node.value)

    # Until Python 3.7
    def visit_Num(self, node: ast.Num, action) -> str:
        return self.convert_constant(node.n)

    # Until Python 3.7
    def visit_Str(self, node: ast.Str, action) -> str:
        return self.convert_constant(node.s)

    # Until Python 3.7
    def visit_Bytes(self, node: ast.Bytes, action) -> str:
        return self.convert_constant(node.s)

    # Until Python 3.7
    def visit_NameConstant(self, node: ast.NameConstant, action) -> str:
        return self.convert_constant(node.value)

    # Until Python 3.7
    def visit_Ellipsis(self, node: ast.Ellipsis, action) -> str:
        return self.convert_constant(...)

    def visit_UnaryOp(self, node, action):  # pylint: disable=invalid-name
        """Visit a unary op node."""

        def _wrap(child):
            latex = self.visit(child)
            if isinstance(child, ast.BinOp) and isinstance(
                child.op, (ast.Add, ast.Sub)
            ):
                return r"\left(" + latex + r"\right)"
            return latex

        reprs = {
            ast.UAdd: (lambda: _wrap(node.operand)),
            ast.USub: (lambda: "-" + _wrap(node.operand)),
            ast.Not: (lambda: r"\lnot\left(" + _wrap(node.operand) + r"\right)"),
        }

        if type(node.op) in reprs:
            return reprs[type(node.op)]()
        return r"\mathrm{unknown\_uniop}(" + self.visit(node.operand) + ")"

    def visit_BinOp(self, node, action):  # pylint: disable=invalid-name
        """Visit a binary op node."""
        priority = constants.BIN_OP_PRIORITY

        def _unwrap(child):
            return self.visit(child)

        def _wrap(child):
            latex = _unwrap(child)
            if isinstance(child, ast.BinOp):
                cp = priority[type(child.op)] if type(child.op) in priority else 100
                pp = priority[type(node.op)] if type(node.op) in priority else 100
                if cp < pp:
                    return "(" + latex + ")"
            return latex

        lhs = node.left
        rhs = node.right
        reprs = {
            ast.Add: (lambda: _wrap(lhs) + " + " + _wrap(rhs)),
            ast.Sub: (lambda: _wrap(lhs) + " - " + _wrap(rhs)),
            ast.Mult: (lambda: _wrap(lhs) + _wrap(rhs)),
            ast.MatMult: (lambda: _wrap(lhs) + _wrap(rhs)),
            ast.Div: (lambda: r"\frac{" + _unwrap(lhs) + "}{" + _unwrap(rhs) + "}"),
            ast.FloorDiv: (
                lambda: r"\left\lfloor\frac{"
                + _unwrap(lhs)
                + "}{"
                + _unwrap(rhs)
                + r"}\right\rfloor"
            ),
            ast.Mod: (lambda: _wrap(lhs) + r" \bmod " + _wrap(rhs)),
            ast.Pow: (lambda: _wrap(lhs) + "^{" + _unwrap(rhs) + "}"),
        }

        if type(node.op) in reprs:
            return reprs[type(node.op)]()
        return r"\mathrm{unknown\_binop}(" + _unwrap(lhs) + ", " + _unwrap(rhs) + ")"

    _compare_ops: ClassVar[dict[type[ast.cmpop], str]] = {
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

    def visit_Compare(self, node: ast.Compare, action):  # pylint: disable=invalid-name
        """Visit a compare node."""
        lhs = self.visit(node.left)
        ops = [self._compare_ops[type(x)] for x in node.ops]
        rhs = [self.visit(x) for x in node.comparators]
        ops_rhs = [f" {o} {r}" for o, r in zip(ops, rhs)]
        return "{" + lhs + "".join(ops_rhs) + "}"

    _bool_ops: ClassVar[dict[type[ast.boolop], str]] = {
        ast.And: r"\land",
        ast.Or: r"\lor",
    }

    def visit_BoolOp(self, node: ast.BoolOp, action):  # pylint: disable=invalid-name
        """Visit a BoolOp node."""
        values = [rf"\left( {self.visit(x)} \right)" for x in node.values]
        op = f" {self._bool_ops[type(node.op)]} "
        return "{" + op.join(values) + "}"

    def visit_If(self, node, action):  # pylint: disable=invalid-name
        """Visit an if node."""
        latex = r"\left\{ \begin{array}{ll} "

        while isinstance(node, ast.If):
            cond_latex = self.visit(node.test)
            true_latex = self.visit(node.body[0])
            latex += true_latex + r", & \mathrm{if} \ " + cond_latex + r" \\ "
            node = node.orelse[0]

        latex += self.visit(node)
        return latex + r", & \mathrm{otherwise} \end{array} \right."

    def visit_GeneratorExp_set_bounds(self, node):  # pylint: disable=invalid-name
        output = self.visit(node.elt)
        comprehensions = [
            self.visit(generator, "set_bounds") for generator in node.generators
        ]
        if len(comprehensions) == 1:
            return output, comprehensions[0]
        raise exceptions.LatexifyNotSupportedError(
            "visit_GeneratorExp_sum() supports a single for clause"
            "but {} were given".format(len(comprehensions))
        )

    def visit_comprehension_set_bounds(self, node):  # pylint: disable=invalid-name
        """Visit a comprehension node, which represents a for clause"""
        var = self.visit(node.target)
        if isinstance(node.iter, ast.Call):
            callee_str = self.visit(node.iter.func)
        if callee_str == "range":
            args = [self.visit(arg) for arg in node.iter.args]
            if len(args) in (1, 2):
                return var, args
        raise exceptions.LatexifyNotSupportedError(
            "Comprehension for sum only supports range func " "with 1 or 2 args"
        )
