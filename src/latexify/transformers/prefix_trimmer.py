from __future__ import annotations

import ast


class PrefixTrimmer(ast.NodeTransformer):
    """NodeTransformer to trim function prefixes.

    Example:
        def f(x, y):
            return math.hypot(x, y)

        PrefixTrimmer({"math"}) will modify the AST of the function above to below:

        def f(x, y):
            return hypot(x, y)
    """

    def __init__(self, prefixes: set[str]) -> None:
        self._prefixes = prefixes

    def visit_Attribute(self, node: ast.Attribute) -> ast.AST:
        """Visitor of Attribute nodes."""
        if issubclass(node.value.__class__, ast.Name):
            if node.value.id in self._prefixes:
                return ast.Name(id=node.attr, ctx=node.ctx)
        if issubclass(node.value.__class__, ast.Attribute):
            kwargs = node.__dict__
            kwargs["value"] = self.visit_Attribute(node.value)
            return ast.Attribute(**kwargs)
        return node
