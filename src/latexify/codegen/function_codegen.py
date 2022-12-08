"""Codegen for single functions."""

from __future__ import annotations

import ast

from latexify import ast_utils, exceptions
from latexify.codegen import codegen_utils, expression_codegen, identifier_converter


class FunctionCodegen(ast.NodeVisitor):
    """Codegen for single functions.

    This codegen works for Module with single FunctionDef node to generate a single
    LaTeX expression of the given function.
    """

    _identifier_converter: identifier_converter.IdentifierConverter
    _use_signature: bool

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
        self._expression_codegen = expression_codegen.ExpressionCodegen(
            use_math_symbols=use_math_symbols, use_set_symbols=use_set_symbols
        )
        self._identifier_converter = identifier_converter.IdentifierConverter(
            use_math_symbols=use_math_symbols
        )
        self._use_signature = use_signature

    def generic_visit(self, node: ast.AST) -> str:
        if isinstance(node, ast.expr):
            return self._expression_codegen.visit(node)
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
            else codegen_utils.convert_constant(None)
        )

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
