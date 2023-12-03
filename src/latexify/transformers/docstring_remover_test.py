"""Tests for latexify.transformers.docstring_remover."""

import ast

from latexify import ast_utils, parser, test_utils
from latexify.transformers.docstring_remover import DocstringRemover


def test_remove_docstrings() -> None:
    def f():
        """Test docstring."""
        x = 42
        f()  # This Expr should not be removed.
        """This string constant should also be removed."""
        return x

    tree = parser.parse_function(f).body[0]
    assert isinstance(tree, ast.FunctionDef)

    expected = ast.FunctionDef(
        name="f",
        body=[
            ast.Assign(
                targets=[ast.Name(id="x", ctx=ast.Store())],
                value=ast_utils.make_constant(42),
            ),
            ast.Expr(value=ast.Call(func=ast.Name(id="f", ctx=ast.Load()))),
            ast.Return(value=ast.Name(id="x", ctx=ast.Load())),
        ],
    )
    transformed = DocstringRemover().visit(tree)
    test_utils.assert_ast_equal(transformed, expected)
