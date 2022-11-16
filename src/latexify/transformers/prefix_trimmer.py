"""Transformer to trim package prefixes."""

from __future__ import annotations

import ast


class PrefixTrimmer(ast.NodeTransformer):
    """NodeTransformer to trim package prefixes.

    Example:
        import math

        def foo(n):
            return math.sqrt(n)

        PrefixTrimmer(["math"]) will modify the AST of
        the function above to below:

        import math

        def foo(n):
            return sqrt(n)
    """

    def __init__(self, prefixes: list[str]):
        """Initializer.

        Args:
            prefixes: Set of prefixes to be trimmed.
        """
        self._prefixes = prefixes

    def visit_Call(self, node: ast.Call) -> ast.Name:
        """Visitor of Call."""
        if (
            isinstance(node.func, ast.Attribute)
            and node.func.value.id in self._prefixes
        ):
            new_node_func = ast.Name(id=node.func.attr, ctx=node.func.ctx)
            node.func = new_node_func

        return node
