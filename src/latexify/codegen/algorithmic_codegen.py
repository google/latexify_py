"""Codegen for single algorithms."""

from __future__ import annotations

import ast
import contextlib
from collections.abc import Generator

from latexify import exceptions
from latexify.codegen import expression_codegen, identifier_converter


class AlgorithmicCodegen(ast.NodeVisitor):
    """Codegen for single algorithms.

    This codegen works for Module with single FunctionDef node to generate a single
    LaTeX expression of the given algorithm.
    """

    _SPACES_PER_INDENT = 4

    _identifier_converter: identifier_converter.IdentifierConverter
    _indent_level: int

    def __init__(
        self, *, use_math_symbols: bool = False, use_set_symbols: bool = False
    ) -> None:
        """Initializer.

        Args:
            use_math_symbols: Whether to convert identifiers with a math symbol surface
                (e.g., "alpha") to the LaTeX symbol (e.g., "\\alpha").
            use_set_symbols: Whether to use set symbols or not.
        """
        self._expression_codegen = expression_codegen.ExpressionCodegen(
            use_math_symbols=use_math_symbols, use_set_symbols=use_set_symbols
        )
        self._identifier_converter = identifier_converter.IdentifierConverter(
            use_math_symbols=use_math_symbols
        )
        self._indent_level = 0

    def generic_visit(self, node: ast.AST) -> str:
        raise exceptions.LatexifyNotSupportedError(
            f"Unsupported AST: {type(node).__name__}"
        )

    def visit_Assign(self, node: ast.Assign) -> str:
        """Visit an Assign node."""
        operands: list[str] = [
            self._expression_codegen.visit(target) for target in node.targets
        ]
        operands.append(self._expression_codegen.visit(node.value))
        operands_latex = r" \gets ".join(operands)
        return self._add_indent(rf"\State ${operands_latex}$")

    def visit_Expr(self, node: ast.Expr) -> str:
        """Visit an Expr node."""
        return self._add_indent(
            rf"\State ${self._expression_codegen.visit(node.value)}$"
        )

    def visit_FunctionDef(self, node: ast.FunctionDef) -> str:
        """Visit a FunctionDef node."""
        # Arguments
        arg_strs = [
            self._identifier_converter.convert(arg.arg)[0] for arg in node.args.args
        ]

        latex = self._add_indent("\\begin{algorithmic}\n")
        with self._increment_level():
            latex += self._add_indent(
                f"\\Function{{{node.name}}}{{${', '.join(arg_strs)}$}}\n"
            )

            with self._increment_level():
                # Body
                body_strs: list[str] = [self.visit(stmt) for stmt in node.body]
            body_latex = "\n".join(body_strs)

            latex += f"{body_latex}\n"
            latex += self._add_indent("\\EndFunction\n")
        return latex + self._add_indent(r"\end{algorithmic}")

    # TODO(ZibingZhang): support \ELSIF
    def visit_If(self, node: ast.If) -> str:
        """Visit an If node."""
        cond_latex = self._expression_codegen.visit(node.test)
        with self._increment_level():
            body_latex = "\n".join(self.visit(stmt) for stmt in node.body)

        latex = self._add_indent(f"\\If{{${cond_latex}$}}\n{body_latex}")

        if node.orelse:
            latex += "\n" + self._add_indent(r"\Else") + "\n"
            with self._increment_level():
                latex += "\n".join(self.visit(stmt) for stmt in node.orelse)

        return latex + "\n" + self._add_indent(r"\EndIf")

    def visit_Module(self, node: ast.Module) -> str:
        """Visit a Module node."""
        return self.visit(node.body[0])

    def visit_Return(self, node: ast.Return) -> str:
        """Visit a Return node."""
        return (
            self._add_indent(
                rf"\State \Return ${self._expression_codegen.visit(node.value)}$"
            )
            if node.value is not None
            else self._add_indent(r"\State \Return")
        )

    def visit_While(self, node: ast.While) -> str:
        """Visit a While node."""
        if node.orelse:
            raise exceptions.LatexifyNotSupportedError(
                "While statement with the else clause is not supported"
            )

        cond_latex = self._expression_codegen.visit(node.test)
        with self._increment_level():
            body_latex = "\n".join(self.visit(stmt) for stmt in node.body)
        return (
            self._add_indent(f"\\While{{${cond_latex}$}}\n")
            + f"{body_latex}\n"
            + self._add_indent(r"\EndWhile")
        )

    @contextlib.contextmanager
    def _increment_level(self) -> Generator[None, None, None]:
        """Context manager controlling indent level."""
        self._indent_level += 1
        yield
        self._indent_level -= 1

    def _add_indent(self, line: str) -> str:
        """Adds whitespace before the line.

        Args:
            line: The line to add whitespace to.
        """
        return self._indent_level * self._SPACES_PER_INDENT * " " + line
