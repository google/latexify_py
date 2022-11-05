"""Tests for latexify.codegen.function_codegen."""

from __future__ import annotations

import ast
from latexify import exceptions
from latexify import test_utils

import pytest

from latexify.codegen import FunctionCodegen, function_codegen


def test_generic_visit() -> None:
    class UnknownNode(ast.AST):
        pass

    with pytest.raises(
        exceptions.LatexifyNotSupportedError,
        match=r"^Unsupported AST: UnknownNode$",
    ):
        function_codegen.FunctionCodegen().visit(UnknownNode())


def test_visit_functiondef_use_signature() -> None:
    tree = ast.FunctionDef(
        name="f",
        args=ast.arguments(
            args=[ast.arg(arg="x")],
            kwonlyargs=[],
            kw_defaults=[],
            defaults=[],
        ),
        body=[ast.Return(value=ast.Name(id="x", ctx=ast.Load()))],
        decorator_list=[],
    )
    latex_without_flag = "x"
    latex_with_flag = r"\mathrm{f}(x) = x"
    assert FunctionCodegen().visit(tree) == latex_with_flag
    assert FunctionCodegen(use_signature=False).visit(tree) == latex_without_flag
    assert FunctionCodegen(use_signature=True).visit(tree) == latex_with_flag


@pytest.mark.parametrize(
    "src_suffix,dest_suffix",
    [
        # No comprehension
        ("(x)", r" \left({x}\right)"),
        ("([1, 2])", r" \left({\left[ {1}\space,\space {2}\right] }\right)"),
        ("({1, 2})", r" \left({\left\{ {1}\space,\space {2}\right\} }\right)"),
        ("(f(x))", r" \left({\mathrm{f}\left(x\right)}\right)"),
        # Single comprehension
        ("(i for i in x)", r"_{i \in x}^{} \left({i}\right)"),
        (
            "(i for i in [1, 2])",
            r"_{i \in \left[ {1}\space,\space {2}\right] }^{} \left({i}\right)",
        ),
        (
            "(i for i in {1, 2})",
            r"_{i \in \left\{ {1}\space,\space {2}\right\} }^{} \left({i}\right)",
        ),
        ("(i for i in f(x))", r"_{i \in \mathrm{f}\left(x\right)}^{} \left({i}\right)"),
        ("(i for i in range(n))", r"_{i = {0}}^{{n - 1}} \left({i}\right)"),
        ("(i for i in range(3))", r"_{i = {0}}^{{2}} \left({i}\right)"),
        ("(i for i in range(n, m))", r"_{i = n}^{{m - 1}} \left({i}\right)"),
        ("(i for i in range(1, m))", r"_{i = {1}}^{{m - 1}} \left({i}\right)"),
        ("(i for i in range(n, 3))", r"_{i = n}^{{2}} \left({i}\right)"),
        (
            "(i for i in range(n, m, k))",
            r"_{i \in \mathrm{range}\left(n, m, k\right)}^{} \left({i}\right)",
        ),
    ],
)
def test_visit_call_sum_prod(src_suffix: str, dest_suffix: str) -> None:
    for src_fn, dest_fn in [("sum", r"\sum"), ("math.prod", r"\prod")]:
        node = ast.parse(src_fn + src_suffix).body[0].value
        assert isinstance(node, ast.Call)
        assert FunctionCodegen().visit(node) == dest_fn + dest_suffix


@pytest.mark.parametrize(
    "code,latex",
    [
        # 2 clauses
        (
            "sum(i for y in x for i in y)",
            r"\sum_{y \in x}^{} \sum_{i \in y}^{} \left({i}\right)",
        ),
        (
            "sum(i for y in x for z in y for i in z)",
            r"\sum_{y \in x}^{} \sum_{z \in y}^{} \sum_{i \in z}^{} \left({i}\right)",
        ),
        # 3 clauses
        (
            "math.prod(i for y in x for i in y)",
            r"\prod_{y \in x}^{} \prod_{i \in y}^{} \left({i}\right)",
        ),
        (
            "math.prod(i for y in x for z in y for i in z)",
            r"\prod_{y \in x}^{} \prod_{z \in y}^{} \prod_{i \in z}^{} "
            r"\left({i}\right)",
        ),
    ],
)
def test_visit_call_sum_prod_multiple_comprehension(code: str, latex: str) -> None:
    node = ast.parse(code).body[0].value
    assert isinstance(node, ast.Call)
    assert FunctionCodegen().visit(node) == latex


@pytest.mark.parametrize(
    "src_suffix,dest_suffix",
    [
        (
            "(i for i in x if i < y)",
            r"_{i \in x \land {i < y}}^{} \left({i}\right)",
        ),
        (
            "(i for i in x if i < y if f(i))",
            r"_{i \in x \land {i < y} \land \mathrm{f}\left(i\right)}^{} "
            r"\left({i}\right)",
        ),
    ],
)
def test_visit_call_sum_prod_with_if(src_suffix: str, dest_suffix: str) -> None:
    for src_fn, dest_fn in [("sum", r"\sum"), ("math.prod", r"\prod")]:
        node = ast.parse(src_fn + src_suffix).body[0].value
        assert isinstance(node, ast.Call)
        assert FunctionCodegen().visit(node) == dest_fn + dest_suffix


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
    assert function_codegen.FunctionCodegen().visit(tree) == latex


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
    assert function_codegen.FunctionCodegen().visit(tree) == latex


@test_utils.require_at_most(7)
@pytest.mark.parametrize(
    "code,cls,latex",
    [
        ("0", ast.Num, "{0}"),
        ("1", ast.Num, "{1}"),
        ("0.0", ast.Num, "{0.0}"),
        ("1.5", ast.Num, "{1.5}"),
        ("0.0j", ast.Num, "{0j}"),
        ("1.0j", ast.Num, "{1j}"),
        ("1.5j", ast.Num, "{1.5j}"),
        ('"abc"', ast.Str, r'\textrm{"abc"}'),
        ('b"abc"', ast.Bytes, r"\textrm{b'abc'}"),
        ("None", ast.NameConstant, r"\mathrm{None}"),
        ("False", ast.NameConstant, r"\mathrm{False}"),
        ("True", ast.NameConstant, r"\mathrm{True}"),
        ("...", ast.Ellipsis, r"{\cdots}"),
    ],
)
def test_visit_constant_lagacy(code: str, cls: type[ast.expr], latex: str) -> None:
    tree = ast.parse(code).body[0].value
    assert isinstance(tree, cls)
    assert function_codegen.FunctionCodegen().visit(tree) == latex


@test_utils.require_at_least(8)
@pytest.mark.parametrize(
    "code,latex",
    [
        ("0", "{0}"),
        ("1", "{1}"),
        ("0.0", "{0.0}"),
        ("1.5", "{1.5}"),
        ("0.0j", "{0j}"),
        ("1.0j", "{1j}"),
        ("1.5j", "{1.5j}"),
        ('"abc"', r'\textrm{"abc"}'),
        ('b"abc"', r"\textrm{b'abc'}"),
        ("None", r"\mathrm{None}"),
        ("False", r"\mathrm{False}"),
        ("True", r"\mathrm{True}"),
        ("...", r"{\cdots}"),
    ],
)
def test_visit_constant(code: str, latex: str) -> None:
    tree = ast.parse(code).body[0].value
    assert isinstance(tree, ast.Constant)


@pytest.mark.parametrize(
    "code,latex",
    [
        ("x[0]", "{x_{{0}}}"),
        ("x[0][1]", "{x_{{0}, {1}}}"),
        ("x[0][1][2]", "{x_{{0}, {1}, {2}}}"),
        ("x[foo]", "{x_{foo}}"),
        ("x[math.floor(x)]", r"{x_{\left\lfloor{x}\right\rfloor}}"),
    ],
)
def test_visit_subscript(code: str, latex: str) -> None:
    tree = ast.parse(code).body[0].value
    assert isinstance(tree, ast.Subscript)
    assert function_codegen.FunctionCodegen().visit(tree) == latex
