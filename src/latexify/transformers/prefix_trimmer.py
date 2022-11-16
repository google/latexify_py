"""Transformer to trim package prefixes."""

from __future__ import annotations

import ast


class PrefixTrimmer(ast.NodeTransformer):
    """NodeTransformer to trim prefixes of identifiers.

    Example:
        def foo(n):
            return math.sqrt(n)

        PrefixTrimmer({"math"}) will modify the AST of
        the function above to below:

        def foo(n):
            return sqrt(n)
    """

    def __init__(self, prefixes: set[str]):
        """Initializer.

        Args:
            prefixes: Set of prefixes to be trimmed.
        """
        self._prefixes = prefixes

    def visit_Call(self, node: ast.Call) -> ast.Call:
        """Visitor of Call."""
        node_func = node.func
        while isinstance(node_func, ast.Attribute):
            node_func = node_func.value

        # if outermost prefix matches any given prefix, loose
        # the entire chain (if it's a chain)
        if node_func.id in self._prefixes:
            return ast.Call(
                func=ast.Name(id=node.func.attr, ctx=node.func.ctx),
                args=node.args,
                keywords=node.keywords,
            )

        return node

    def visit_Attribute(self, node: ast.Attribute) -> ast.Name | ast.Attribute:
        """Visitor of Attribute."""
        node_value = node.value
        while isinstance(node_value, ast.Attribute):
            node_value = node_value.value

        # if outermost prefix matches any given prefix, loose
        # the entire chain (if it's a chain)
        if node_value.id in self._prefixes:
            return ast.Name(id=node.value, ctx=node.value.ctx)

        return node
