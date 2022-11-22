from __future__ import annotations

import ast
import functools
from collections.abc import Callable

from latexify import ast_utils, constants, exceptions


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


def _exp_expander(function_expander: FunctionExpander, node: ast.Call) -> ast.AST:
    if len(node.args) != 1:
        raise exceptions.LatexifyNotSupportedError(
            "FunctionExpander only supports expanding 'exp' with one argument"
        )

    return ast.BinOp(
        left=ast.Name(id="e", ctx=ast.Load()),
        op=ast.Pow(),
        right=function_expander.visit(node.args[0]),
    )


def _exp2_expander(function_expander: FunctionExpander, node: ast.Call) -> ast.AST:
    if len(node.args) != 1:
        raise exceptions.LatexifyNotSupportedError(
            "FunctionExpander only supports expanding 'exp2' with one argument"
        )

    return ast.BinOp(
        left=ast_utils.make_constant(2),
        op=ast.Pow(),
        right=function_expander.visit(node.args[0]),
    )


def _expm1_expander(function_expander: FunctionExpander, node: ast.Call) -> ast.AST:
    if len(node.args) != 1:
        raise exceptions.LatexifyNotSupportedError(
            "FunctionExpander only supports expanding 'expm1' with one argument"
        )

    return ast.BinOp(
        left=ast.Call(
            func=ast.Name(id=constants.BuiltinFnName.EXP.value, ctx=ast.Load()),
            args=[function_expander.visit(node.args[0])],
        ),
        op=ast.Sub(),
        right=ast_utils.make_constant(1),
    )


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


def _log1p_expander(function_expander: FunctionExpander, node: ast.Call) -> ast.AST:
    if len(node.args) != 1:
        raise exceptions.LatexifyNotSupportedError(
            "FunctionExpander only supports expanding 'log1p' with one argument"
        )

    return ast.Call(
        func=ast.Name(id=constants.BuiltinFnName.LOG.value, ctx=ast.Load()),
        args=[
            ast.BinOp(
                left=ast_utils.make_constant(1),
                op=ast.Add(),
                right=function_expander.visit(node.args[0]),
            )
        ],
    )


_FUNCTION_EXPANDERS: dict[str, Callable[[FunctionExpander, ast.Call], ast.AST]] = {
    "exp": _exp_expander,
    "exp2": _exp2_expander,
    "expm1": _expm1_expander,
    "hypot": _hypot_expander,
    "log1p": _log1p_expander,
}
