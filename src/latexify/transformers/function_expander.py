from __future__ import annotations

import ast
from collections.abc import Callable
from functools import reduce
from typing import Any

from latexify import exceptions


class FunctionExpander(ast.NodeTransformer):
    """NodeTransformer to expand functions.

    This class replaces function calls with an expanded form.

    Example:
        def f(x, y):
            return hypot(x, y)

        FunctionExpander(["hypot"]) will modify the AST of the function above to below:

        def f(x, y):
            return sqrt(x**2, y**2)
    """

    def __init__(self, functions):
        self.functions = functions

    def visit_Call(self, node: ast.Call) -> Any:
        """Visitor of FunctionDef nodes."""
        if (
            isinstance(node.func, ast.Name)
            and node.func.id in self.functions
            and node.func.id in _FUNCTION_EXPANDERS
        ):
            return _FUNCTION_EXPANDERS[node.func.id](node, self)

        return node


def _hypot_expander(node: ast.Call, function_expander: FunctionExpander) -> ast.AST:
    if len(node.args) == 0:
        raise exceptions.LatexifyNotSupportedError(
            "AssignmentReducer does not support expanding 'hypot' with zero arguments."
        )

    args = []
    for arg in node.args:
        args.append(ast.BinOp(arg, ast.Pow(), ast.Num(2)))

    args = list(map(lambda arg: function_expander.visit(arg), args))

    node.func.id = "sqrt"
    if len(args) <= 1:
        node.args = args
    else:
        node.args = [
            reduce(lambda acc, arg: ast.BinOp(acc, ast.Add(), arg), args[1:], args[0])
        ]

    return node


_FUNCTION_EXPANDERS: dict[str, Callable[[ast.Call, FunctionExpander], ast.AST]] = {
    "hypot": _hypot_expander
}
