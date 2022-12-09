from __future__ import annotations

import ast
import functools
from collections.abc import Callable

from latexify import ast_utils, exceptions


# TODO(ZibingZhang): handle mutually recursive function expansions
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
        """Visit a Call node."""
        func_name = ast_utils.extract_function_name_or_none(node)
        if (
            func_name is not None
            and func_name in self._functions
            and func_name in _FUNCTION_EXPANDERS
        ):
            return _FUNCTION_EXPANDERS[func_name](self, node)

        kwargs = {
            "func": self.visit(node.func),
            "args": [self.visit(x) for x in node.args],
        }

        if hasattr(node, "keywords"):
            kwargs["keywords"] = [
                ast.keyword(arg=x.arg, value=self.visit(x.value)) for x in node.keywords
            ]

        return ast.Call(**kwargs)


def _atan2_expander(function_expander: FunctionExpander, node: ast.Call) -> ast.AST:
    _check_num_args(node, 2)
    return ast.Call(
        func=ast.Name(id="atan", ctx=ast.Load()),
        args=[
            ast.BinOp(
                left=function_expander.visit(node.args[0]),
                op=ast.Div(),
                right=function_expander.visit(node.args[1]),
            )
        ],
    )


def _exp_expander(function_expander: FunctionExpander, node: ast.Call) -> ast.AST:
    _check_num_args(node, 1)
    return ast.BinOp(
        left=ast.Name(id="e", ctx=ast.Load()),
        op=ast.Pow(),
        right=function_expander.visit(node.args[0]),
    )


def _exp2_expander(function_expander: FunctionExpander, node: ast.Call) -> ast.AST:
    _check_num_args(node, 1)
    return ast.BinOp(
        left=ast_utils.make_constant(2),
        op=ast.Pow(),
        right=function_expander.visit(node.args[0]),
    )


def _expm1_expander(function_expander: FunctionExpander, node: ast.Call) -> ast.AST:
    _check_num_args(node, 1)
    return ast.BinOp(
        left=function_expander.visit(
            ast.Call(
                func=ast.Name(id="exp", ctx=ast.Load()),
                args=[node.args[0]],
            )
        ),
        op=ast.Sub(),
        right=ast_utils.make_constant(1),
    )


def _hypot_expander(function_expander: FunctionExpander, node: ast.Call) -> ast.AST:
    if not node.args:
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
        func=ast.Name(id="sqrt", ctx=ast.Load()),
        args=[args_reduced],
    )


def _log1p_expander(function_expander: FunctionExpander, node: ast.Call) -> ast.AST:
    _check_num_args(node, 1)
    return ast.Call(
        func=ast.Name(id="log", ctx=ast.Load()),
        args=[
            ast.BinOp(
                left=ast_utils.make_constant(1),
                op=ast.Add(),
                right=function_expander.visit(node.args[0]),
            )
        ],
    )


def _pow_expander(function_expander: FunctionExpander, node: ast.Call) -> ast.AST:
    _check_num_args(node, 2)
    return ast.BinOp(
        left=function_expander.visit(node.args[0]),
        op=ast.Pow(),
        right=function_expander.visit(node.args[1]),
    )


def _check_num_args(node: ast.Call, nargs: int) -> None:
    if len(node.args) != nargs:
        fn_name = ast_utils.extract_function_name_or_none(node)
        raise exceptions.LatexifySyntaxError(
            f"Incorrect number of arguments for {fn_name}."
            f" expected: {nargs}, but got {len(node.args)}"
        )


_FUNCTION_EXPANDERS: dict[str, Callable[[FunctionExpander, ast.Call], ast.AST]] = {
    "atan2": _atan2_expander,
    "exp": _exp_expander,
    "exp2": _exp2_expander,
    "expm1": _expm1_expander,
    "hypot": _hypot_expander,
    "log1p": _log1p_expander,
    "pow": _pow_expander,
}
