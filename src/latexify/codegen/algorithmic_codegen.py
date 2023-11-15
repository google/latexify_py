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
            use_math_symbols=use_math_symbols,
            use_mathrm=False,
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

    def visit_For(self, node: ast.For) -> str:
        """Visit a For node."""
        if len(node.orelse) != 0:
            raise exceptions.LatexifyNotSupportedError(
                "For statement with the else clause is not supported"
            )

        target_latex = self._expression_codegen.visit(node.target)
        iter_latex = self._expression_codegen.visit(node.iter)
        with self._increment_level():
            body_latex = "\n".join(self.visit(stmt) for stmt in node.body)

        return (
            self._add_indent(f"\\For{{${target_latex} \\in {iter_latex}$}}\n")
            + f"{body_latex}\n"
            + self._add_indent("\\EndFor")
        )

    # TODO(ZibingZhang): support nested functions
    def visit_FunctionDef(self, node: ast.FunctionDef) -> str:
        """Visit a FunctionDef node."""
        name_latex = self._identifier_converter.convert(node.name)[0]

        # Arguments
        arg_strs = [
            self._identifier_converter.convert(arg.arg)[0] for arg in node.args.args
        ]

        latex = self._add_indent("\\begin{algorithmic}\n")
        with self._increment_level():
            latex += self._add_indent(
                f"\\Function{{{name_latex}}}{{${', '.join(arg_strs)}$}}\n"
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

        latex = self._add_indent(f"\\If{{${cond_latex}$}}\n" + body_latex)

        if node.orelse:
            latex += "\n" + self._add_indent("\\Else\n")
            with self._increment_level():
                latex += "\n".join(self.visit(stmt) for stmt in node.orelse)

        return f"{latex}\n" + self._add_indent(r"\EndIf")

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

    def visit_Pass(self, node: ast.Pass) -> str:
        """Visit a Pass node."""
        return self._add_indent(r"\State $\mathbf{pass}$")

    def visit_Break(self, node: ast.Break) -> str:
        """Visit a Break node."""
        return self._add_indent(r"\State $\mathbf{break}$")

    def visit_Continue(self, node: ast.Continue) -> str:
        """Visit a Continue node."""
        return self._add_indent(r"\State $\mathbf{continue}$")

    @contextlib.contextmanager
    def _increment_level(self) -> Generator[None, None, None]:
        """Context manager controlling indent level."""
        self._indent_level += 1
        yield
        self._indent_level -= 1

    def _add_indent(self, line: str) -> str:
        """Adds an indent before the line.

        Args:
            line: The line to add an indent to.
        """
        return self._indent_level * self._SPACES_PER_INDENT * " " + line


class IPythonAlgorithmicCodegen(ast.NodeVisitor):
    """Codegen for single algorithms targeting IPython.

    This codegen works for Module with single FunctionDef node to generate a single
    LaTeX expression of the given algorithm.
    """

    _EM_PER_INDENT = 1
    _LINE_BREAK = r" \\ "

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
        return self._add_indent(operands_latex)

    def visit_Expr(self, node: ast.Expr) -> str:
        """Visit an Expr node."""
        return self._add_indent(self._expression_codegen.visit(node.value))

    def visit_For(self, node: ast.For) -> str:
        """Visit a For node."""
        if len(node.orelse) != 0:
            raise exceptions.LatexifyNotSupportedError(
                "For statement with the else clause is not supported"
            )

        target_latex = self._expression_codegen.visit(node.target)
        iter_latex = self._expression_codegen.visit(node.iter)
        with self._increment_level():
            body_latex = self._LINE_BREAK.join(self.visit(stmt) for stmt in node.body)

        return (
            self._add_indent(r"\mathbf{for}")
            + rf" \ {target_latex} \in {iter_latex} \ \mathbf{{do}}{self._LINE_BREAK}"
            + f"{body_latex}{self._LINE_BREAK}"
            + self._add_indent(r"\mathbf{end \ for}")
        )

    # TODO(ZibingZhang): support nested functions
    def visit_FunctionDef(self, node: ast.FunctionDef) -> str:
        """Visit a FunctionDef node."""
        name_latex = self._identifier_converter.convert(node.name)[0]

        # Arguments
        args_latex = [
            self._identifier_converter.convert(arg.arg)[0] for arg in node.args.args
        ]
        # Body
        with self._increment_level():
            body_stmts_latex: list[str] = [self.visit(stmt) for stmt in node.body]
        body_latex = self._LINE_BREAK.join(body_stmts_latex)

        return (
            r"\begin{array}{l} "
            + self._add_indent(r"\mathbf{function}")
            + rf" \ {name_latex}({', '.join(args_latex)})"
            + f"{self._LINE_BREAK}{body_latex}{self._LINE_BREAK}"
            + self._add_indent(r"\mathbf{end \ function}")
            + r" \end{array}"
        )

    # TODO(ZibingZhang): support \ELSIF
    def visit_If(self, node: ast.If) -> str:
        """Visit an If node."""
        cond_latex = self._expression_codegen.visit(node.test)
        with self._increment_level():
            body_latex = self._LINE_BREAK.join(self.visit(stmt) for stmt in node.body)
        latex = self._add_indent(
            rf"\mathbf{{if}} \ {cond_latex}{self._LINE_BREAK}{body_latex}"
        )

        if node.orelse:
            latex += self._LINE_BREAK + self._add_indent(r"\mathbf{else} \\ ")
            with self._increment_level():
                latex += self._LINE_BREAK.join(self.visit(stmt) for stmt in node.orelse)

        return latex + self._LINE_BREAK + self._add_indent(r"\mathbf{end \ if}")

    def visit_Module(self, node: ast.Module) -> str:
        """Visit a Module node."""
        return self.visit(node.body[0])

    def visit_Return(self, node: ast.Return) -> str:
        """Visit a Return node."""
        return (
            self._add_indent(r"\mathbf{return} \ ")
            + self._expression_codegen.visit(node.value)
            if node.value is not None
            else self._add_indent(r"\mathbf{return}")
        )

    def visit_While(self, node: ast.While) -> str:
        """Visit a While node."""
        if node.orelse:
            raise exceptions.LatexifyNotSupportedError(
                "While statement with the else clause is not supported"
            )

        cond_latex = self._expression_codegen.visit(node.test)
        with self._increment_level():
            body_latex = self._LINE_BREAK.join(self.visit(stmt) for stmt in node.body)
        return (
            self._add_indent(r"\mathbf{while} \ ")
            + f"{cond_latex}{self._LINE_BREAK}{body_latex}{self._LINE_BREAK}"
            + self._add_indent(r"\mathbf{end \ while}")
        )

    def visit_Pass(self, node: ast.Pass) -> str:
        """Visit a Pass node."""
        return self._add_indent(r"\mathbf{pass}")

    def visit_Break(self, node: ast.Break) -> str:
        """Visit a Break node."""
        return self._add_indent(r"\mathbf{break}")

    def visit_Continue(self, node: ast.Continue) -> str:
        """Visit a Continue node."""
        return self._add_indent(r"\mathbf{continue}")

    @contextlib.contextmanager
    def _increment_level(self) -> Generator[None, None, None]:
        """Context manager controlling indent level."""
        self._indent_level += 1
        yield
        self._indent_level -= 1

    def _add_indent(self, line: str) -> str:
        """Adds an indent before the line.

        Args:
            line: The line to add an indent to.
        """
        return (
            rf"\hspace{{{self._indent_level * self._EM_PER_INDENT}em}} {line}"
            if self._indent_level > 0
            else line
        )
