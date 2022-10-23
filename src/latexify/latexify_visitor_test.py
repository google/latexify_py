"""Tests for latexify.latexify_visitor."""

import ast
import pytest

from latexify.latexify_visitor import LatexifyVisitor


@pytest.mark.parametrize(
    "code,latex",
    [
        ("a == b", "{a = b}"),
        ("a > b", "{a > b}"),
        ("a >= b", r"{a \ge b}"),
        ("a in b", r"{a \in b}"),
        ("a is b", r"{a \equiv b}"),
        ("a is not b", r"{a \not\equiv b}"),
        ("a < b", "{a < b}"),
        ("a <= b", r"{a \le b}"),
        ("a != b", r"{a \ne b}"),
        ("a not in b", r"{a \notin b}"),
    ],
)
def test_visit_compare(code: str, latex: str) -> None:
    tree = ast.parse(code).body[0].value
    assert isinstance(tree, ast.Compare)
    assert LatexifyVisitor().visit(tree) == latex


def test_visit_compare_multiple() -> None:
    tree = ast.parse("a < b < c").body[0].value
    assert isinstance(tree, ast.Compare)
    with pytest.raises(SyntaxError, match=r"^Multiple compares are not supported\.$"):
        LatexifyVisitor().visit(tree)


@pytest.mark.parametrize(
    "code,latex",
    [
        ("a and b", r"{\left( a \right) \land \left( b \right)}"),
        (
            "a and b and c",
            r"{\left( a \right) \land \left( b \right) \land \left( c \right)}",
        ),
        ("a or b", r"{\left( a \right) \lor \left( b \right)}"),
        (
            "a or b or c",
            r"{\left( a \right) \lor \left( b \right) \lor \left( c \right)}",
        ),
    ],
)
def test_visit_boolop(code: str, latex: str) -> None:
    tree = ast.parse(code).body[0].value
    assert isinstance(tree, ast.BoolOp)
    assert LatexifyVisitor().visit(tree) == latex
