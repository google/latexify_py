"""Tests for latexify.codegen.function_codegen."""

from __future__ import annotations

import ast

import pytest

from latexify import exceptions, test_utils
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
    tree = ast.parse(
        """
def f(x):
    return x
    """
    )
    latex_without_flag = "x"
    latex_with_flag = r"\mathrm{f}(x) = x"
    assert FunctionCodegen().visit(tree) == latex_with_flag
    assert FunctionCodegen(use_signature=False).visit(tree) == latex_without_flag
    assert FunctionCodegen(use_signature=True).visit(tree) == latex_with_flag


def test_visit_functiondef_ignore_docstring() -> None:
    tree = ast.parse(
        """
def f(x):
    '''docstring'''
    return x"""
    )
    latex = r"\mathrm{f}(x) = x"
    assert FunctionCodegen().visit(tree) == latex


def test_visit_functiondef_ignore_multiple_constants() -> None:
    tree = ast.parse(
        """
def f(x):
    '''docstring'''
    3
    True
    return x"""
    )
    latex = r"\mathrm{f}(x) = x"
    assert FunctionCodegen().visit(tree) == latex


@pytest.mark.parametrize(
    "code,latex",
    [
        ("[i for i in n]", r"\left[ i \mid i \in n \right]"),
        (
            "[i for i in n if i > 0]",
            r"\left[ i \mid"
            r" \mathopen{}\left( i \in n \mathclose{}\right)"
            r" \land \mathopen{}\left( {i > {0}} \mathclose{}\right)"
            r" \right]",
        ),
        (
            "[i for i in n if i > 0 if f(i)]",
            r"\left[ i \mid"
            r" \mathopen{}\left( i \in n \mathclose{}\right)"
            r" \land \mathopen{}\left( {i > {0}} \mathclose{}\right)"
            r" \land \mathopen{}\left( \mathrm{f}\mathopen{}\left("
            r"i\mathclose{}\right) \mathclose{}\right)"
            r" \right]",
        ),
        ("[i for k in n for i in k]", r"\left[ i \mid k \in n, i \in k" r" \right]"),
        (
            "[i for k in n for i in k if i > 0]",
            r"\left[ i \mid"
            r" k \in n,"
            r" \mathopen{}\left( i \in k \mathclose{}\right)"
            r" \land \mathopen{}\left( {i > {0}} \mathclose{}\right)"
            r" \right]",
        ),
        (
            "[i for k in n if f(k) for i in k if i > 0]",
            r"\left[ i \mid"
            r" \mathopen{}\left( k \in n \mathclose{}\right)"
            r" \land \mathopen{}\left( \mathrm{f}\mathopen{}\left("
            r"k\mathclose{}\right) \mathclose{}\right),"
            r" \mathopen{}\left( i \in k \mathclose{}\right)"
            r" \land \mathopen{}\left( {i > {0}} \mathclose{}\right)"
            r" \right]",
        ),
    ],
)
def test_visit_listcomp(code: str, latex: str) -> None:
    node = ast.parse(code).body[0].value
    assert isinstance(node, ast.ListComp)
    assert FunctionCodegen().visit(node) == latex


@pytest.mark.parametrize(
    "code,latex",
    [
        ("{i for i in n}", r"\left\{ i \mid i \in n \right\}"),
        (
            "{i for i in n if i > 0}",
            r"\left\{ i \mid"
            r" \mathopen{}\left( i \in n \mathclose{}\right)"
            r" \land \mathopen{}\left( {i > {0}} \mathclose{}\right)"
            r" \right\}",
        ),
        (
            "{i for i in n if i > 0 if f(i)}",
            r"\left\{ i \mid"
            r" \mathopen{}\left( i \in n \mathclose{}\right)"
            r" \land \mathopen{}\left( {i > {0}} \mathclose{}\right)"
            r" \land \mathopen{}\left( \mathrm{f}\mathopen{}\left("
            r"i\mathclose{}\right) \mathclose{}\right)"
            r" \right\}",
        ),
        ("{i for k in n for i in k}", r"\left\{ i \mid k \in n, i \in k" r" \right\}"),
        (
            "{i for k in n for i in k if i > 0}",
            r"\left\{ i \mid"
            r" k \in n,"
            r" \mathopen{}\left( i \in k \mathclose{}\right)"
            r" \land \mathopen{}\left( {i > {0}} \mathclose{}\right)"
            r" \right\}",
        ),
        (
            "{i for k in n if f(k) for i in k if i > 0}",
            r"\left\{ i \mid"
            r" \mathopen{}\left( k \in n \mathclose{}\right)"
            r" \land \mathopen{}\left( \mathrm{f}\mathopen{}\left("
            r"k\mathclose{}\right) \mathclose{}\right),"
            r" \mathopen{}\left( i \in k \mathclose{}\right)"
            r" \land \mathopen{}\left( {i > {0}} \mathclose{}\right)"
            r" \right\}",
        ),
    ],
)
def test_visit_setcomp(code: str, latex: str) -> None:
    node = ast.parse(code).body[0].value
    assert isinstance(node, ast.SetComp)
    assert FunctionCodegen().visit(node) == latex


@pytest.mark.parametrize(
    "src_suffix,dest_suffix",
    [
        # No comprehension
        ("(x)", r" \left({x}\right)"),
        ("([1, 2])", r" \left({\left[ {1}\space,\space {2}\right] }\right)"),
        ("({1, 2})", r" \left({\left\{ {1}\space,\space {2}\right\} }\right)"),
        ("(f(x))", r" \left({\mathrm{f}\mathopen{}\left(x\mathclose{}\right)}\right)"),
        # Single comprehension
        ("(i for i in x)", r"_{i \in x}^{} \mathopen{}\left({i}\mathclose{}\right)"),
        (
            "(i for i in [1, 2])",
            r"_{i \in \left[ {1}\space,\space {2}\right] }^{} "
            r"\mathopen{}\left({i}\mathclose{}\right)",
        ),
        (
            "(i for i in {1, 2})",
            r"_{i \in \left\{ {1}\space,\space {2}\right\} }^{} "
            r"\mathopen{}\left({i}\mathclose{}\right)",
        ),
        (
            "(i for i in f(x))",
            r"_{i \in \mathrm{f}\mathopen{}\left(x\mathclose{}\right)}^{} "
            r"\mathopen{}\left({i}\mathclose{}\right)",
        ),
        (
            "(i for i in range(n))",
            r"_{i = {0}}^{{n - 1}} \mathopen{}\left({i}\mathclose{}\right)",
        ),
        (
            "(i for i in range(3))",
            r"_{i = {0}}^{{2}} \mathopen{}\left({i}\mathclose{}\right)",
        ),
        (
            "(i for i in range(n, m))",
            r"_{i = n}^{{m - 1}} \mathopen{}\left({i}\mathclose{}\right)",
        ),
        (
            "(i for i in range(1, m))",
            r"_{i = {1}}^{{m - 1}} \mathopen{}\left({i}\mathclose{}\right)",
        ),
        (
            "(i for i in range(n, 3))",
            r"_{i = n}^{{2}} \mathopen{}\left({i}\mathclose{}\right)",
        ),
        (
            "(i for i in range(n, m, k))",
            r"_{i \in \mathrm{range}\mathopen{}\left(n, m, k"
            r"\mathclose{}\right)}^{} \mathopen{}\left({i}\mathclose{}\right)",
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
            r"\sum_{y \in x}^{} \sum_{i \in y}^{} "
            r"\mathopen{}\left({i}\mathclose{}\right)",
        ),
        (
            "sum(i for y in x for z in y for i in z)",
            r"\sum_{y \in x}^{} \sum_{z \in y}^{} \sum_{i \in z}^{} "
            r"\mathopen{}\left({i}\mathclose{}\right)",
        ),
        # 3 clauses
        (
            "math.prod(i for y in x for i in y)",
            r"\prod_{y \in x}^{} \prod_{i \in y}^{} "
            r"\mathopen{}\left({i}\mathclose{}\right)",
        ),
        (
            "math.prod(i for y in x for z in y for i in z)",
            r"\prod_{y \in x}^{} \prod_{z \in y}^{} \prod_{i \in z}^{} "
            r"\mathopen{}\left({i}\mathclose{}\right)",
        ),
        # reduce stop parameter
        (
            "sum(i for i in range(n+1))",
            r"\sum_{i = {0}}^{{n}} \mathopen{}\left({i}\mathclose{}\right)",
        ),
        (
            "math.prod(i for i in range(n-1))",
            r"\prod_{i = {0}}^{{n - {2}}} \mathopen{}\left({i}\mathclose{}\right)",
        ),
        # reduce stop parameter
        (
            "sum(i for i in range(n+1))",
            r"\sum_{i = {0}}^{{n}} \mathopen{}\left({i}\mathclose{}\right)",
        ),
        (
            "math.prod(i for i in range(n-1))",
            r"\prod_{i = {0}}^{{n - {2}}} \mathopen{}\left({i}\mathclose{}\right)",
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
            r"_{\mathopen{}\left( i \in x \mathclose{}\right) "
            r"\land \mathopen{}\left( {i < y} \mathclose{}\right)}^{} "
            r"\mathopen{}\left({i}\mathclose{}\right)",
        ),
        (
            "(i for i in x if i < y if f(i))",
            r"_{\mathopen{}\left( i \in x \mathclose{}\right) "
            r"\land \mathopen{}\left( {i < y} \mathclose{}\right)"
            r" \land \mathopen{}\left( \mathrm{f}\mathopen{}\left("
            r"i\mathclose{}\right) \mathclose{}\right)}^{}"
            r" \mathopen{}\left({i}\mathclose{}\right)",
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
        (
            "x if x < y else y",
            r"\left\{ \begin{array}{ll} x,"
            r" & \mathrm{if} \ {x < y} \\ y,"
            r" & \mathrm{otherwise} \end{array} \right.",
        ),
        (
            "x if x < y else (y if y < z else z)",
            r"\left\{ \begin{array}{ll} x,"
            r" & \mathrm{if} \ {x < y} \\ y,"
            r" & \mathrm{if} \ {y < z} \\ z,"
            r" & \mathrm{otherwise} \end{array} \right.",
        ),
        (
            "x if x < y else (y if y < z else (z if z < w else w))",
            r"\left\{ \begin{array}{ll} x,"
            r" & \mathrm{if} \ {x < y} \\ y,"
            r" & \mathrm{if} \ {y < z} \\ z,"
            r" & \mathrm{if} \ {z < w} \\ w,"
            r" & \mathrm{otherwise} \end{array} \right.",
        ),
    ],
)
def test_if_then_else(code: str, latex: str) -> None:
    node = ast.parse(code).body[0].value
    assert isinstance(node, ast.IfExp)
    assert FunctionCodegen().visit(node) == latex


@pytest.mark.parametrize(
    "code,latex",
    [
        # x op y
        ("x**y", r"x^{y}"),
        ("x * y", r"x y"),
        ("x @ y", r"x y"),
        ("x / y", r"\frac{x}{y}"),
        ("x // y", r"\left\lfloor\frac{x}{y}\right\rfloor"),
        ("x % y", r"x \mathbin{\%} y"),
        ("x + y", r"x + y"),
        ("x - y", r"x - y"),
        ("x << y", r"x \ll y"),
        ("x >> y", r"x \gg y"),
        ("x & y", r"x \mathbin{\&} y"),
        ("x ^ y", r"x \oplus y"),
        ("x | y", R"x \mathbin{|} y"),
        # (x op y) op z
        ("(x**y)**z", r"\mathopen{}\left( x^{y} \mathclose{}\right)^{z}"),
        ("(x * y) * z", r"x y z"),
        ("(x @ y) @ z", r"x y z"),
        ("(x / y) / z", r"\frac{\frac{x}{y}}{z}"),
        (
            "(x // y) // z",
            r"\left\lfloor\frac{\left\lfloor\frac{x}{y}\right\rfloor}{z}\right\rfloor",
        ),
        ("(x % y) % z", r"x \mathbin{\%} y \mathbin{\%} z"),
        ("(x + y) + z", r"x + y + z"),
        ("(x - y) - z", r"x - y - z"),
        ("(x << y) << z", r"x \ll y \ll z"),
        ("(x >> y) >> z", r"x \gg y \gg z"),
        ("(x & y) & z", r"x \mathbin{\&} y \mathbin{\&} z"),
        ("(x ^ y) ^ z", r"x \oplus y \oplus z"),
        ("(x | y) | z", r"x \mathbin{|} y \mathbin{|} z"),
        # x op (y op z)
        ("x**(y**z)", r"x^{y^{z}}"),
        ("x * (y * z)", r"x y z"),
        ("x @ (y @ z)", r"x y z"),
        ("x / (y / z)", r"\frac{x}{\frac{y}{z}}"),
        (
            "x // (y // z)",
            r"\left\lfloor\frac{x}{\left\lfloor\frac{y}{z}\right\rfloor}\right\rfloor",
        ),
        (
            "x % (y % z)",
            r"x \mathbin{\%} \mathopen{}\left( y \mathbin{\%} z \mathclose{}\right)",
        ),
        ("x + (y + z)", r"x + y + z"),
        ("x - (y - z)", r"x - \mathopen{}\left( y - z \mathclose{}\right)"),
        ("x << (y << z)", r"x \ll \mathopen{}\left( y \ll z \mathclose{}\right)"),
        ("x >> (y >> z)", r"x \gg \mathopen{}\left( y \gg z \mathclose{}\right)"),
        ("x & (y & z)", r"x \mathbin{\&} y \mathbin{\&} z"),
        ("x ^ (y ^ z)", r"x \oplus y \oplus z"),
        ("x | (y | z)", r"x \mathbin{|} y \mathbin{|} z"),
        # x OP y op z
        ("x**y * z", r"x^{y} z"),
        ("x * y + z", r"x y + z"),
        ("x @ y + z", r"x y + z"),
        ("x / y + z", r"\frac{x}{y} + z"),
        ("x // y + z", r"\left\lfloor\frac{x}{y}\right\rfloor + z"),
        ("x % y + z", r"x \mathbin{\%} y + z"),
        ("x + y << z", r"x + y \ll z"),
        ("x - y << z", r"x - y \ll z"),
        ("x << y & z", r"x \ll y \mathbin{\&} z"),
        ("x >> y & z", r"x \gg y \mathbin{\&} z"),
        ("x & y ^ z", r"x \mathbin{\&} y \oplus z"),
        ("x ^ y | z", r"x \oplus y \mathbin{|} z"),
        # x OP (y op z)
        ("x**(y * z)", r"x^{y z}"),
        ("x * (y + z)", r"x \mathopen{}\left( y + z \mathclose{}\right)"),
        ("x @ (y + z)", r"x \mathopen{}\left( y + z \mathclose{}\right)"),
        ("x / (y + z)", r"\frac{x}{y + z}"),
        ("x // (y + z)", r"\left\lfloor\frac{x}{y + z}\right\rfloor"),
        ("x % (y + z)", r"x \mathbin{\%} \mathopen{}\left( y + z \mathclose{}\right)"),
        ("x + (y << z)", r"x + \mathopen{}\left( y \ll z \mathclose{}\right)"),
        ("x - (y << z)", r"x - \mathopen{}\left( y \ll z \mathclose{}\right)"),
        (
            "x << (y & z)",
            r"x \ll \mathopen{}\left( y \mathbin{\&} z \mathclose{}\right)",
        ),
        (
            "x >> (y & z)",
            r"x \gg \mathopen{}\left( y \mathbin{\&} z \mathclose{}\right)",
        ),
        (
            "x & (y ^ z)",
            r"x \mathbin{\&} \mathopen{}\left( y \oplus z \mathclose{}\right)",
        ),
        (
            "x ^ (y | z)",
            r"x \oplus \mathopen{}\left( y \mathbin{|} z \mathclose{}\right)",
        ),
        # x op y OP z
        ("x * y**z", r"x y^{z}"),
        ("x + y * z", r"x + y z"),
        ("x + y @ z", r"x + y z"),
        ("x + y / z", r"x + \frac{y}{z}"),
        ("x + y // z", r"x + \left\lfloor\frac{y}{z}\right\rfloor"),
        ("x + y % z", r"x + y \mathbin{\%} z"),
        ("x << y + z", r"x \ll y + z"),
        ("x << y - z", r"x \ll y - z"),
        ("x & y << z", r"x \mathbin{\&} y \ll z"),
        ("x & y >> z", r"x \mathbin{\&} y \gg z"),
        ("x ^ y & z", r"x \oplus y \mathbin{\&} z"),
        ("x | y ^ z", r"x \mathbin{|} y \oplus z"),
        # (x op y) OP z
        ("(x * y)**z", r"\mathopen{}\left( x y \mathclose{}\right)^{z}"),
        ("(x + y) * z", r"\mathopen{}\left( x + y \mathclose{}\right) z"),
        ("(x + y) @ z", r"\mathopen{}\left( x + y \mathclose{}\right) z"),
        ("(x + y) / z", r"\frac{x + y}{z}"),
        ("(x + y) // z", r"\left\lfloor\frac{x + y}{z}\right\rfloor"),
        ("(x + y) % z", r"\mathopen{}\left( x + y \mathclose{}\right) \mathbin{\%} z"),
        ("(x << y) + z", r"\mathopen{}\left( x \ll y \mathclose{}\right) + z"),
        ("(x << y) - z", r"\mathopen{}\left( x \ll y \mathclose{}\right) - z"),
        (
            "(x & y) << z",
            r"\mathopen{}\left( x \mathbin{\&} y \mathclose{}\right) \ll z",
        ),
        (
            "(x & y) >> z",
            r"\mathopen{}\left( x \mathbin{\&} y \mathclose{}\right) \gg z",
        ),
        (
            "(x ^ y) & z",
            r"\mathopen{}\left( x \oplus y \mathclose{}\right) \mathbin{\&} z",
        ),
        (
            "(x | y) ^ z",
            r"\mathopen{}\left( x \mathbin{|} y \mathclose{}\right) \oplus z",
        ),
        # is_wrapped
        ("(x // y)**z", r"\left\lfloor\frac{x}{y}\right\rfloor^{z}"),
        # With Call
        ("x**f(y)", r"x^{\mathrm{f}\mathopen{}\left(y\mathclose{}\right)}"),
        ("f(x)**y", r"\mathrm{f}\mathopen{}\left(x\mathclose{}\right)^{y}"),
        ("x * f(y)", r"x \mathrm{f}\mathopen{}\left(y\mathclose{}\right)"),
        ("f(x) * y", r"\mathrm{f}\mathopen{}\left(x\mathclose{}\right) y"),
        ("x / f(y)", r"\frac{x}{\mathrm{f}\mathopen{}\left(y\mathclose{}\right)}"),
        ("f(x) / y", r"\frac{\mathrm{f}\mathopen{}\left(x\mathclose{}\right)}{y}"),
        ("x + f(y)", r"x + \mathrm{f}\mathopen{}\left(y\mathclose{}\right)"),
        ("f(x) + y", r"\mathrm{f}\mathopen{}\left(x\mathclose{}\right) + y"),
        # With UnaryOp
        ("x**-y", r"x^{-y}"),
        ("(-x)**y", r"\mathopen{}\left( -x \mathclose{}\right)^{y}"),
        ("x * -y", r"x -y"),  # TODO(odashi): google/latexify_py#89
        ("-x * y", r"-x y"),
        ("x / -y", r"\frac{x}{-y}"),
        ("-x / y", r"\frac{-x}{y}"),
        ("x + -y", r"x + -y"),
        ("-x + y", r"-x + y"),
        # With Compare
        ("x**(y == z)", r"x^{{y = z}}"),
        ("(x == y)**z", r"\mathopen{}\left( {x = y} \mathclose{}\right)^{z}"),
        ("x * (y == z)", r"x \mathopen{}\left( {y = z} \mathclose{}\right)"),
        ("(x == y) * z", r"\mathopen{}\left( {x = y} \mathclose{}\right) z"),
        ("x / (y == z)", r"\frac{x}{{y = z}}"),
        ("(x == y) / z", r"\frac{{x = y}}{z}"),
        ("x + (y == z)", r"x + \mathopen{}\left( {y = z} \mathclose{}\right)"),
        ("(x == y) + z", r"\mathopen{}\left( {x = y} \mathclose{}\right) + z"),
        # With BoolOp
        ("x**(y and z)", r"x^{{y \land z}}"),
        ("(x and y)**z", r"\mathopen{}\left( {x \land y} \mathclose{}\right)^{z}"),
        ("x * (y and z)", r"x \mathopen{}\left( {y \land z} \mathclose{}\right)"),
        ("(x and y) * z", r"\mathopen{}\left( {x \land y} \mathclose{}\right) z"),
        ("x / (y and z)", r"\frac{x}{{y \land z}}"),
        ("(x and y) / z", r"\frac{{x \land y}}{z}"),
        ("x + (y and z)", r"x + \mathopen{}\left( {y \land z} \mathclose{}\right)"),
        ("(x and y) + z", r"\mathopen{}\left( {x \land y} \mathclose{}\right) + z"),
    ],
)
def test_visit_binop(code: str, latex: str) -> None:
    tree = ast.parse(code).body[0].value
    assert isinstance(tree, ast.BinOp)
    assert function_codegen.FunctionCodegen().visit(tree) == latex


@pytest.mark.parametrize(
    "code,latex",
    [
        # With literals
        ("+x", r"+x"),
        ("-x", r"-x"),
        ("~x", r"\mathord{\sim} x"),
        ("not x", r"\lnot x"),
        # With Call
        ("+f(x)", r"+\mathrm{f}\mathopen{}\left(x\mathclose{}\right)"),
        ("-f(x)", r"-\mathrm{f}\mathopen{}\left(x\mathclose{}\right)"),
        ("~f(x)", r"\mathord{\sim} \mathrm{f}\mathopen{}\left(x\mathclose{}\right)"),
        ("not f(x)", r"\lnot \mathrm{f}\mathopen{}\left(x\mathclose{}\right)"),
        # With BinOp
        ("+(x + y)", r"+\mathopen{}\left( x + y \mathclose{}\right)"),
        ("-(x + y)", r"-\mathopen{}\left( x + y \mathclose{}\right)"),
        ("~(x + y)", r"\mathord{\sim} \mathopen{}\left( x + y \mathclose{}\right)"),
        ("not x + y", r"\lnot \mathopen{}\left( x + y \mathclose{}\right)"),
        # With Compare
        ("+(x == y)", r"+\mathopen{}\left( {x = y} \mathclose{}\right)"),
        ("-(x == y)", r"-\mathopen{}\left( {x = y} \mathclose{}\right)"),
        ("~(x == y)", r"\mathord{\sim} \mathopen{}\left( {x = y} \mathclose{}\right)"),
        ("not x == y", r"\lnot \mathopen{}\left( {x = y} \mathclose{}\right)"),
        # With BoolOp
        ("+(x and y)", r"+\mathopen{}\left( {x \land y} \mathclose{}\right)"),
        ("-(x and y)", r"-\mathopen{}\left( {x \land y} \mathclose{}\right)"),
        (
            "~(x and y)",
            r"\mathord{\sim} \mathopen{}\left( {x \land y} \mathclose{}\right)",
        ),
        ("not (x and y)", r"\lnot \mathopen{}\left( {x \land y} \mathclose{}\right)"),
    ],
)
def test_visit_unaryop(code: str, latex: str) -> None:
    tree = ast.parse(code).body[0].value
    assert isinstance(tree, ast.UnaryOp)
    assert function_codegen.FunctionCodegen().visit(tree) == latex


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
        # With Call
        ("a == f(b)", r"{a = \mathrm{f}\mathopen{}\left(b\mathclose{}\right)}"),
        ("f(a) == b", r"{\mathrm{f}\mathopen{}\left(a\mathclose{}\right) = b}"),
        # With BinOp
        ("a == b + c", r"{a = b + c}"),
        ("a + b == c", r"{a + b = c}"),
        # With UnaryOp
        ("a == -b", r"{a = -b}"),
        ("-a == b", r"{-a = b}"),
        ("a == (not b)", r"{a = \lnot b}"),
        ("(not a) == b", r"{\lnot a = b}"),
        # With BoolOp
        ("a == (b and c)", r"{a = \mathopen{}\left( {b \land c} \mathclose{}\right)}"),
        ("(a and b) == c", r"{\mathopen{}\left( {a \land b} \mathclose{}\right) = c}"),
    ],
)
def test_visit_compare(code: str, latex: str) -> None:
    tree = ast.parse(code).body[0].value
    assert isinstance(tree, ast.Compare)
    assert function_codegen.FunctionCodegen().visit(tree) == latex


@pytest.mark.parametrize(
    "code,latex",
    [
        # With literals
        ("a and b", r"{a \land b}"),
        ("a and b and c", r"{a \land b \land c}"),
        ("a or b", r"{a \lor b}"),
        ("a or b or c", r"{a \lor b \lor c}"),
        ("a or b and c", r"{a \lor {b \land c}}"),
        (
            "(a or b) and c",
            r"{\mathopen{}\left( {a \lor b} \mathclose{}\right) \land c}",
        ),
        ("a and b or c", r"{{a \land b} \lor c}"),
        (
            "a and (b or c)",
            r"{a \land \mathopen{}\left( {b \lor c} \mathclose{}\right)}",
        ),
        # With Call
        ("a and f(b)", r"{a \land \mathrm{f}\mathopen{}\left(b\mathclose{}\right)}"),
        ("f(a) and b", r"{\mathrm{f}\mathopen{}\left(a\mathclose{}\right) \land b}"),
        ("a or f(b)", r"{a \lor \mathrm{f}\mathopen{}\left(b\mathclose{}\right)}"),
        ("f(a) or b", r"{\mathrm{f}\mathopen{}\left(a\mathclose{}\right) \lor b}"),
        # With BinOp
        ("a and b + c", r"{a \land b + c}"),
        ("a + b and c", r"{a + b \land c}"),
        ("a or b + c", r"{a \lor b + c}"),
        ("a + b or c", r"{a + b \lor c}"),
        # With UnaryOp
        ("a and not b", r"{a \land \lnot b}"),
        ("not a and b", r"{\lnot a \land b}"),
        ("a or not b", r"{a \lor \lnot b}"),
        ("not a or b", r"{\lnot a \lor b}"),
        # With Compare
        ("a and b == c", r"{a \land {b = c}}"),
        ("a == b and c", r"{{a = b} \land c}"),
        ("a or b == c", r"{a \lor {b = c}}"),
        ("a == b or c", r"{{a = b} \lor c}"),
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


@pytest.mark.parametrize(
    "code,latex",
    [
        ("a - b", r"a \setminus b"),
        ("a & b", r"a \cap b"),
        ("a ^ b", r"a \mathbin{\triangle} b"),
        ("a | b", r"a \cup b"),
    ],
)
def test_use_set_symbols_binop(code: str, latex: str) -> None:
    tree = ast.parse(code).body[0].value
    assert isinstance(tree, ast.BinOp)
    assert function_codegen.FunctionCodegen(use_set_symbols=True).visit(tree) == latex


@pytest.mark.parametrize(
    "code,latex",
    [
        ("a < b", r"{a \subset b}"),
        ("a <= b", r"{a \subseteq b}"),
        ("a > b", r"{a \supset b}"),
        ("a >= b", r"{a \supseteq b}"),
    ],
)
def test_use_set_symbols_compare(code: str, latex: str) -> None:
    tree = ast.parse(code).body[0].value
    assert isinstance(tree, ast.Compare)
    assert function_codegen.FunctionCodegen(use_set_symbols=True).visit(tree) == latex
