"""Codegen for single algorithms."""
import ast

from latexify import exceptions
from latexify.codegen import codegen_utils, expression_codegen


class AlgorithmicCodegen(ast.NodeVisitor):
    """Codegen for single algorithms."""

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

    def generic_visit(self, node: ast.AST) -> str:
        raise exceptions.LatexifyNotSupportedError(
            f"Unsupported AST: {type(node).__name__}"
        )

    def visit_Assign(self, node: ast.Assign) -> str:
        operands: list[str] = [
            self._expression_codegen.visit(target) for target in node.targets
        ]
        operands.append(self._expression_codegen.visit(node.value))
        operands_latex = r" \gets ".join(operands)
        return rf"\State ${operands_latex}$"

    def visit_FunctionDef(self, node: ast.FunctionDef) -> str:
        body_strs: list[str] = [self.visit(stmt) for stmt in node.body]
        return rf"\begin{{algorithmic}} {' '.join(body_strs)} \end{{algorithmic}}"

    def visit_If(self, node: ast.If) -> str:
        cond_latex = self._expression_codegen.visit(node.test)
        body_latex = " ".join(self.visit(stmt) for stmt in node.body)

        latex = rf"\If{{${cond_latex}$}} {body_latex}"

        if node.orelse:
            latex += r" \Else "
            latex += " ".join(self.visit(stmt) for stmt in node.orelse)

        return latex + r" \EndIf"

    def visit_Module(self, node: ast.Module) -> str:
        return self.visit(node.body[0])

    def visit_Return(self, node: ast.Return) -> str:
        return (
            rf"\State \Return ${self._expression_codegen.visit(node.value)}$"
            if node.value is not None
            else codegen_utils.convert_constant(None)
        )

    def visit_While(self, node: ast.While) -> str:
        cond_latex = self._expression_codegen.visit(node.test)
        body_latex = " ".join(self.visit(stmt) for stmt in node.body)

        latex = rf"\While{{${cond_latex}$}} {body_latex}"

        if node.orelse:
            latex += r" \Else "
            latex += " ".join(self.visit(stmt) for stmt in node.orelse)

        return latex + r" \EndWhile"
