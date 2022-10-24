"""Transformer to replace user symbols."""

from __future__ import annotations

import ast
import re
import sys
from typing import ClassVar


class IdentifierReplacer(ast.NodeTransformer):
    """NodeTransformer to replace identifier names.

    This class defines a rule to replace identifiers in AST with specified names.

    Example:
        def foo(bar):
            return baz

        IdentifierReplacer({"foo": "x", "bar": "y", "baz": "z"}) will modify the AST of
        the function above to below:

        def x(y):
            return z
    """

    _IDENTIFIER_PATTERN: ClassVar[re.Pattern] = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

    def __init__(self, mapping: dict[str, str]):
        """Initializer.

        Args:
            mapping: User defined mapping of names. Keys are the original names of the
                identifiers, and corresponding values are the replacements.
                Both keys and values have to represent valid Python identifiers:
                ^[A-Za-z_][A-Za-z0-9_]*$
        """
        self._mapping = mapping

        for k, v in self._mapping.items():
            if not self._IDENTIFIER_PATTERN.match(k):
                raise ValueError(f"'{k}' is not an identifier name.")
            if not self._IDENTIFIER_PATTERN.match(v):
                raise ValueError(f"'{v}' is not an identifier name.")

    def _replace_args(self, args: list[ast.arg]) -> list[ast.arg]:
        """Helper function to replace arg names."""
        return [ast.arg(arg=self._mapping.get(a.arg, a.arg)) for a in args]

    def _visit_children(self, children: list[ast.AST]) -> list[ast.AST]:
        """Helper function to visit all children."""
        return [self.visit(child) for child in children]

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        """Visitor of FunctionDef."""
        if sys.version_info.minor < 8:
            args = ast.arguments(
                args=self._replace_args(node.args.args),
                kwonlyargs=self._replace_args(node.args.kwonlyargs),
                kw_defaults=self._visit_children(node.args.kw_defaults),
                defaults=self._visit_children(node.args.defaults),
            )
        else:
            args = ast.arguments(
                posonlyargs=self._replace_args(node.args.posonlyargs),  # from 3.8
                args=self._replace_args(node.args.args),
                kwonlyargs=self._replace_args(node.args.kwonlyargs),
                kw_defaults=self._visit_children(node.args.kw_defaults),
                defaults=self._visit_children(node.args.defaults),
            )

        return ast.FunctionDef(
            name=self._mapping.get(node.name, node.name),
            args=args,
            body=self._visit_children(node.body),
            decorator_list=self._visit_children(node.decorator_list),
        )

    def visit_Name(self, node: ast.Name) -> ast.Name:
        """Visitor of Name."""
        return ast.Name(
            id=self._mapping.get(node.id, node.id),
            ctx=node.ctx,
        )
