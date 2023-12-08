"""Transformer to replace user symbols."""

from __future__ import annotations

import ast
import keyword
import sys
from typing import cast


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
            if not str.isidentifier(k) or keyword.iskeyword(k):
                raise ValueError(f"'{k}' is not an identifier name.")
            if not str.isidentifier(v) or keyword.iskeyword(v):
                raise ValueError(f"'{v}' is not an identifier name.")

    def _replace_args(self, args: list[ast.arg]) -> list[ast.arg]:
        """Helper function to replace arg names."""
        return [ast.arg(arg=self._mapping.get(a.arg, a.arg)) for a in args]

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        """Visit a FunctionDef node."""
        visited = cast(ast.FunctionDef, super().generic_visit(node))

        if sys.version_info.minor < 8:
            args = ast.arguments(
                args=self._replace_args(visited.args.args),
                kwonlyargs=self._replace_args(visited.args.kwonlyargs),
                kw_defaults=visited.args.kw_defaults,
                defaults=visited.args.defaults,
            )
        else:
            args = ast.arguments(
                posonlyargs=self._replace_args(visited.args.posonlyargs),  # from 3.8
                args=self._replace_args(visited.args.args),
                kwonlyargs=self._replace_args(visited.args.kwonlyargs),
                kw_defaults=visited.args.kw_defaults,
                defaults=visited.args.defaults,
            )

        return ast.FunctionDef(
            name=self._mapping.get(visited.name, visited.name),
            args=args,
            body=visited.body,
            decorator_list=visited.decorator_list,
        )

    def visit_Name(self, node: ast.Name) -> ast.Name:
        """Visit a Name node."""
        return ast.Name(
            id=self._mapping.get(node.id, node.id),
            ctx=node.ctx,
        )
