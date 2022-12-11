"""Codegen for single algorithms."""

from __future__ import annotations

import ast

from latexify import exceptions
from latexify.codegen import expression_codegen, identifier_converter


class AlgorithmicCodegen(ast.NodeVisitor):
    """Codegen for single algorithms.

    This codegen works for Module with single FunctionDef node to generate a single
    LaTeX expression of the given algorithm.
    """

    _identifier_converter: identifier_converter.IdentifierConverter

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
        return rf"\State ${operands_latex}$"

    def visit_Expr(self, node: ast.Expr) -> str:
        """Visit an Expr node."""
        return rf"\State ${self._expression_codegen.visit(node.value)}$"

    def visit_FunctionDef(self, node: ast.FunctionDef) -> str:
        """Visit a FunctionDef node."""
        # Arguments
        arg_strs = [
            self._identifier_converter.convert(arg.arg)[0] for arg in node.args.args
        ]
        # Body
        body_strs: list[str] = [self.visit(stmt) for stmt in node.body]

        return (
            rf"\begin{{algorithmic}}"
            rf" \Function{{{node.name}}}{{${', '.join(arg_strs)}$}}"
            f" {' '.join(body_strs)}"
            r" \EndFunction"
            rf" \end{{algorithmic}}"
        )

    # TODO(ZibingZhang): support \ELSIF
    def visit_If(self, node: ast.If) -> str:
        """Visit an If node."""
        cond_latex = self._expression_codegen.visit(node.test)
        body_latex = " ".join(self.visit(stmt) for stmt in node.body)
        latex = rf"\If{{${cond_latex}$}} {body_latex}"

        if node.orelse:
            latex += r" \Else "
            latex += " ".join(self.visit(stmt) for stmt in node.orelse)

        return latex + r" \EndIf"

    def visit_Module(self, node: ast.Module) -> str:
        """Visit a Module node."""
        return self.visit(node.body[0])

    def visit_Return(self, node: ast.Return) -> str:
        """Visit a Return node."""
        return (
            rf"\State \Return ${self._expression_codegen.visit(node.value)}$"
            if node.value is not None
            else r"\State \Return"
        )

    def visit_While(self, node: ast.While) -> str:
        """Visit a While node."""
        if node.orelse:
            raise exceptions.LatexifyNotSupportedError(
                "While statement with the else clause is not supported"
            )

        cond_latex = self._expression_codegen.visit(node.test)
        body_latex = " ".join(self.visit(stmt) for stmt in node.body)
        return rf"\While{{${cond_latex}$}} {body_latex} \EndWhile"


class AlgorithmicJupyterCodegen(ast.NodeVisitor):
    """Codegen for single algorithms, targeting the Jupyter Notebook environment.

    This codegen works for Module with single FunctionDef node to generate a single
    LaTeX expression of the given algorithm.
    """

    _PT_PER_INDENT = 16
    _identifier_converter: identifier_converter.IdentifierConverter
    _indent: int

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
        self._indent = 0

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
        return rf"{self._prefix()} {operands_latex}"

    def visit_Expr(self, node: ast.Expr) -> str:
        """Visit an Expr node."""
        return rf"{self._prefix()} {self._expression_codegen.visit(node.value)}"

    def visit_FunctionDef(self, node: ast.FunctionDef) -> str:
        """Visit a FunctionDef node."""
        # Arguments
        arg_strs = [
            self._identifier_converter.convert(arg.arg)[0] for arg in node.args.args
        ]
        # Body
        self._indent += 1
        body_strs: list[str] = [self.visit(stmt) for stmt in node.body]
        self._indent -= 1
        body = r" \\ ".join(body_strs)

        return (
            rf"{self._prefix()} \mathbf{{function}}"
            rf" \ \mathrm{{{node.name.upper()}}}({', '.join(arg_strs)}): \\"
            rf" {body} \\"
            rf" {self._prefix()} \mathbf{{end \ function}}"
        )

    # TODO(ZibingZhang): support \ELSIF
    def visit_If(self, node: ast.If) -> str:
        """Visit an If node."""
        cond_latex = self._expression_codegen.visit(node.test)
        self._indent += 1
        body_latex = r" \\ ".join(self.visit(stmt) for stmt in node.body)
        self._indent -= 1
        latex = rf"{self._prefix()}\mathbf{{if}} \ {cond_latex} \\ {body_latex}"

        if node.orelse:
            latex += rf" \\ {self._prefix()}\mathbf{{else}} \\ "
            self._indent += 1
            latex += r" \\ ".join(self.visit(stmt) for stmt in node.orelse)
            self._indent -= 1

        return latex + rf" \\ {self._prefix()} \mathbf{{end \ if}}"

    def visit_Module(self, node: ast.Module) -> str:
        """Visit a Module node."""
        return self.visit(node.body[0])

    def visit_Return(self, node: ast.Return) -> str:
        """Visit a Return node."""
        return (
            rf"{self._prefix()} \mathbf{{return}}"
            rf" \ {self._expression_codegen.visit(node.value)}"
            if node.value is not None
            else rf"{self._prefix()} \mathbf{{return}}"
        )

    def visit_While(self, node: ast.While) -> str:
        """Visit a While node."""
        if node.orelse:
            raise exceptions.LatexifyNotSupportedError(
                "While statement with the else clause is not supported"
            )

        cond_latex = self._expression_codegen.visit(node.test)
        self._indent += 1
        body_latex = r" \\ ".join(self.visit(stmt) for stmt in node.body)
        self._indent -= 1
        return (
            rf"{self._prefix()} \mathbf{{while}} \ {cond_latex} \\ "
            rf"{body_latex} \\ "
            rf"{self._prefix()} \mathbf{{end \ while}}"
        )

    def _prefix(self) -> str:
        return rf"\displaystyle \hspace{{{self._indent * self._PT_PER_INDENT}pt}}"
