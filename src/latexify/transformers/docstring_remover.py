"""Transformer to remove all docstrings."""

from __future__ import annotations

import ast
from typing import Union

from latexify import ast_utils


class DocstringRemover(ast.NodeTransformer):
    """NodeTransformer to remove all docstrings.

    Docstrings here are detected as Expr nodes with a single string constant.
    """

    def visit_Expr(self, node: ast.Expr) -> Union[ast.Expr, None]:
        if ast_utils.is_str(node.value):
            return None
        return node
