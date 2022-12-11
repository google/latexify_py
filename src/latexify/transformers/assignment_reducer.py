"""NodeTransformer to reduce assigned expressions."""

from __future__ import annotations

import ast
from typing import Any

from latexify import exceptions


class AssignmentReducer(ast.NodeTransformer):
    """NodeTransformer to reduce assigned expressions.

    This class replaces a functions with multiple assignments to a function with only
    single return.

    Example:
        def f(x):
            y = 2 + x
            z = 3 * y
            return 4 + z

        AssignmentReducer modifies the function above to below:

        def f(x):
            return 4 + 3 * (2 + x)
    """

    _assignments: dict[str, ast.expr] | None = None

    # TODO(odashi):
    # Currently, this function does not care much about some expressions, e.g.,
    # comprehensions or lambdas, which introduces inner scopes.
    # It may cause some mistakes in the resulting AST.
    def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
        """Visit a FunctionDef node."""
        # Push stack
        parent_assignments = self._assignments
        self._assignments = {}

        for child in node.body[:-1]:
            if not isinstance(child, ast.Assign):
                raise exceptions.LatexifyNotSupportedError(
                    "AssignmentReducer supports only Assign nodes, "
                    f"but got: {type(child).__name__}"
                )

            value = self.visit(child.value)

            for target in child.targets:
                if not isinstance(target, ast.Name):
                    raise exceptions.LatexifyNotSupportedError(
                        "AssignmentReducer does not recognize list/tuple "
                        "decomposition."
                    )
                self._assignments[target.id] = value

        return_original = node.body[-1]

        if not isinstance(return_original, (ast.Return, ast.If)):
            raise exceptions.LatexifySyntaxError(
                f"Unsupported last statement: {type(return_original).__name__}"
            )

        return_transformed = self.visit(return_original)

        # Pop stack
        self._assignments = parent_assignments

        return ast.FunctionDef(
            name=node.name,
            args=node.args,
            body=[return_transformed],
            decorator_list=node.decorator_list,
        )

    def visit_Name(self, node: ast.Name) -> Any:
        """Visit a Name node."""
        if self._assignments is not None:
            return self._assignments.get(node.id, node)

        return node
