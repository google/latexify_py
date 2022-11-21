from __future__ import annotations

import ast
import functools
from collections.abc import Callable

from latexify import ast_utils, constants


# TODO(ZibingZhang): handle recursive function expansions
class FunctionExpander(ast.NodeTransformer):
    """NodeTransformer to expand functions.

    This class replaces function calls with an expanded form.

    Example:
        def f(x, y):
            return hypot(x, y)

        FunctionExpander({"hypot"}) will modify the AST of the function above to below:

        def f(x, y):
            return sqrt(x**2, y**2)
    """

    def __init__(self, functions: set[str]) -> None:
        self._functions = functions

    def visit_Call(self, node: ast.Call) -> ast.AST:
        """Visitor of Call nodes."""
        func_name = ast_utils.extract_function_name_or_none(node)
        if (
            func_name is not None
            and func_name in self._functions
            and func_name in _FUNCTION_EXPANDERS
        ):
            return _FUNCTION_EXPANDERS[func_name](self, node)

        return node


def _hypot_expander(function_expander: FunctionExpander, node: ast.Call) -> ast.AST:
    if len(node.args) == 0:
        return ast_utils.make_constant(0)

    args = [
        ast.BinOp(
            left=function_expander.visit(arg),
            op=ast.Pow(),
            right=ast_utils.make_constant(2),
        )
        for arg in node.args
    ]

    args_reduced = functools.reduce(
        lambda a, b: ast.BinOp(left=a, op=ast.Add(), right=b), args
    )
    return ast.Call(
        func=ast.Name(id=constants.BuiltinFnName.SQRT.value, ctx=ast.Load()),
        args=[args_reduced],
    )


_FUNCTION_EXPANDERS: dict[str, Callable[[FunctionExpander, ast.Call], ast.AST]] = {
    "hypot": _hypot_expander
}
