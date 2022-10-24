"""Tests for latexify.latexify_visitor."""

import ast
import pytest

from latexify.latexify_visitor import LatexifyVisitor


@pytest.mark.parametrize(
    "code,latex",
    [
        # 1 comparator
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
        # 2 comparators
        ("a == b == c", "{a = b = c}"),
        ("a == b > c", "{a = b > c}"),
        ("a == b >= c", r"{a = b \ge c}"),
        ("a == b < c", "{a = b < c}"),
        ("a == b <= c", r"{a = b \le c}"),
        ("a > b == c", "{a > b = c}"),
        ("a > b > c", "{a > b > c}"),
        ("a > b >= c", r"{a > b \ge c}"),
        ("a >= b == c", r"{a \ge b = c}"),
        ("a >= b > c", r"{a \ge b > c}"),
        ("a >= b >= c", r"{a \ge b \ge c}"),
        ("a < b == c", "{a < b = c}"),
        ("a < b < c", "{a < b < c}"),
        ("a < b <= c", r"{a < b \le c}"),
        ("a <= b == c", r"{a \le b = c}"),
        ("a <= b < c", r"{a \le b < c}"),
        ("a <= b <= c", r"{a \le b \le c}"),
    ],
)
def test_visit_compare(code: str, latex: str) -> None:
    tree = ast.parse(code).body[0].value
    assert isinstance(tree, ast.Compare)
    assert LatexifyVisitor().visit(tree) == latex


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
