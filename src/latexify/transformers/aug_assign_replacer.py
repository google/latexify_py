"""Transformer to replace AugAssign to Assign."""

from __future__ import annotations

import ast


class AugAssignReplacer(ast.NodeTransformer):
    """NodeTransformer to replace AugAssign to corresponding Assign.

    AugAssign(target, op, value) => Assign([target], BinOp(target, op, value))

    """

    def visit_AugAssign(self, node: ast.AugAssign) -> ast.Assign:
        left_args = {**vars(node.target), "ctx": ast.Load()}
        left = type(node.target)(**left_args)
        return ast.Assign(
            targets=[node.target], value=ast.BinOp(left, node.op, node.value)
        )
