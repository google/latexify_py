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
    "code,latex",
    [
        ("[i for i in n]", r"\left[ i \mid i \in n \right]"),
        (
            "[i for i in n if i > 0]",
            r"\left[ i \mid"
            r" \left( i \in n \right)"
            r" \land \left( {i > {0}} \right)"
            r" \right]",
        ),
        (
            "[i for i in n if i > 0 if f(i)]",
            r"\left[ i \mid"
            r" \left( i \in n \right)"
            r" \land \left( {i > {0}} \right)"
            r" \land \left( \mathrm{f}\left(i\right) \right)"
            r" \right]",
        ),
        ("[i for k in n for i in k]", r"\left[ i \mid k \in n, i \in k" r" \right]"),
        (
            "[i for k in n for i in k if i > 0]",
            r"\left[ i \mid"
            r" k \in n,"
            r" \left( i \in k \right)"
            r" \land \left( {i > {0}} \right)"
            r" \right]",
        ),
        (
            "[i for k in n if f(k) for i in k if i > 0]",
            r"\left[ i \mid"
            r" \left( k \in n \right)"
            r" \land \left( \mathrm{f}\left(k\right) \right),"
            r" \left( i \in k \right)"
            r" \land \left( {i > {0}} \right)"
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
            r" \left( i \in n \right)"
            r" \land \left( {i > {0}} \right)"
            r" \right\}",
        ),
        (
            "{i for i in n if i > 0 if f(i)}",
            r"\left\{ i \mid"
            r" \left( i \in n \right)"
            r" \land \left( {i > {0}} \right)"
            r" \land \left( \mathrm{f}\left(i\right) \right)"
            r" \right\}",
        ),
        ("{i for k in n for i in k}", r"\left\{ i \mid k \in n, i \in k" r" \right\}"),
        (
            "{i for k in n for i in k if i > 0}",
            r"\left\{ i \mid"
            r" k \in n,"
            r" \left( i \in k \right)"
            r" \land \left( {i > {0}} \right)"
            r" \right\}",
        ),
        (
            "{i for k in n if f(k) for i in k if i > 0}",
            r"\left\{ i \mid"
            r" \left( k \in n \right)"
            r" \land \left( \mathrm{f}\left(k\right) \right),"
            r" \left( i \in k \right)"
            r" \land \left( {i > {0}} \right)"
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
            r"_{\left( i \in x \right) \land \left( {i < y} \right)}^{} "
            r"\left({i}\right)",
        ),
        (
            "(i for i in x if i < y if f(i))",
            r"_{\left( i \in x \right) \land \left( {i < y} \right)"
            r" \land \left( \mathrm{f}\left(i\right) \right)}^{}"
            r" \left({i}\right)",
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
        ("(x**y)**z", r"\left( x^{y} \right)^{z}"),
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
        ("x % (y % z)", r"x \mathbin{\%} \left( y \mathbin{\%} z \right)"),
        ("x + (y + z)", r"x + y + z"),
        ("x - (y - z)", r"x - \left( y - z \right)"),
        ("x << (y << z)", r"x \ll \left( y \ll z \right)"),
        ("x >> (y >> z)", r"x \gg \left( y \gg z \right)"),
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
        ("x * (y + z)", r"x \left( y + z \right)"),
        ("x @ (y + z)", r"x \left( y + z \right)"),
        ("x / (y + z)", r"\frac{x}{y + z}"),
        ("x // (y + z)", r"\left\lfloor\frac{x}{y + z}\right\rfloor"),
        ("x % (y + z)", r"x \mathbin{\%} \left( y + z \right)"),
        ("x + (y << z)", r"x + \left( y \ll z \right)"),
        ("x - (y << z)", r"x - \left( y \ll z \right)"),
        ("x << (y & z)", r"x \ll \left( y \mathbin{\&} z \right)"),
        ("x >> (y & z)", r"x \gg \left( y \mathbin{\&} z \right)"),
        ("x & (y ^ z)", r"x \mathbin{\&} \left( y \oplus z \right)"),
        ("x ^ (y | z)", r"x \oplus \left( y \mathbin{|} z \right)"),
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
        ("(x * y)**z", r"\left( x y \right)^{z}"),
        ("(x + y) * z", r"\left( x + y \right) z"),
        ("(x + y) @ z", r"\left( x + y \right) z"),
        ("(x + y) / z", r"\frac{x + y}{z}"),
        ("(x + y) // z", r"\left\lfloor\frac{x + y}{z}\right\rfloor"),
        ("(x + y) % z", r"\left( x + y \right) \mathbin{\%} z"),
        ("(x << y) + z", r"\left( x \ll y \right) + z"),
        ("(x << y) - z", r"\left( x \ll y \right) - z"),
        ("(x & y) << z", r"\left( x \mathbin{\&} y \right) \ll z"),
        ("(x & y) >> z", r"\left( x \mathbin{\&} y \right) \gg z"),
        ("(x ^ y) & z", r"\left( x \oplus y \right) \mathbin{\&} z"),
        ("(x | y) ^ z", r"\left( x \mathbin{|} y \right) \oplus z"),
        # is_wrapped
        ("(x // y)**z", r"\left\lfloor\frac{x}{y}\right\rfloor^{z}"),
        # With Call
        ("x**f(y)", r"x^{\mathrm{f}\left(y\right)}"),
        ("f(x)**y", r"\mathrm{f}\left(x\right)^{y}"),
        ("x * f(y)", r"x \mathrm{f}\left(y\right)"),
        ("f(x) * y", r"\mathrm{f}\left(x\right) y"),
        ("x / f(y)", r"\frac{x}{\mathrm{f}\left(y\right)}"),
        ("f(x) / y", r"\frac{\mathrm{f}\left(x\right)}{y}"),
        ("x + f(y)", r"x + \mathrm{f}\left(y\right)"),
        ("f(x) + y", r"\mathrm{f}\left(x\right) + y"),
        # With UnaryOp
        ("x**-y", r"x^{-y}"),
        ("(-x)**y", r"\left( -x \right)^{y}"),
        ("x * -y", r"x -y"),  # TODO(odashi): google/latexify_py#89
        ("-x * y", r"-x y"),
        ("x / -y", r"\frac{x}{-y}"),
        ("-x / y", r"\frac{-x}{y}"),
        ("x + -y", r"x + -y"),
        ("-x + y", r"-x + y"),
        # With Compare
        ("x**(y == z)", r"x^{{y = z}}"),
        ("(x == y)**z", r"\left( {x = y} \right)^{z}"),
        ("x * (y == z)", r"x \left( {y = z} \right)"),
        ("(x == y) * z", r"\left( {x = y} \right) z"),
        ("x / (y == z)", r"\frac{x}{{y = z}}"),
        ("(x == y) / z", r"\frac{{x = y}}{z}"),
        ("x + (y == z)", r"x + \left( {y = z} \right)"),
        ("(x == y) + z", r"\left( {x = y} \right) + z"),
        # With BoolOp
        ("x**(y and z)", r"x^{{y \land z}}"),
        ("(x and y)**z", r"\left( {x \land y} \right)^{z}"),
        ("x * (y and z)", r"x \left( {y \land z} \right)"),
        ("(x and y) * z", r"\left( {x \land y} \right) z"),
        ("x / (y and z)", r"\frac{x}{{y \land z}}"),
        ("(x and y) / z", r"\frac{{x \land y}}{z}"),
        ("x + (y and z)", r"x + \left( {y \land z} \right)"),
        ("(x and y) + z", r"\left( {x \land y} \right) + z"),
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
        ("+f(x)", r"+\mathrm{f}\left(x\right)"),
        ("-f(x)", r"-\mathrm{f}\left(x\right)"),
        ("~f(x)", r"\mathord{\sim} \mathrm{f}\left(x\right)"),
        ("not f(x)", r"\lnot \mathrm{f}\left(x\right)"),
        # With BinOp
        ("+(x + y)", r"+\left( x + y \right)"),
        ("-(x + y)", r"-\left( x + y \right)"),
        ("~(x + y)", r"\mathord{\sim} \left( x + y \right)"),
        ("not x + y", r"\lnot \left( x + y \right)"),
        # With Compare
        ("+(x == y)", r"+\left( {x = y} \right)"),
        ("-(x == y)", r"-\left( {x = y} \right)"),
        ("~(x == y)", r"\mathord{\sim} \left( {x = y} \right)"),
        ("not x == y", r"\lnot \left( {x = y} \right)"),
        # With BoolOp
        ("+(x and y)", r"+\left( {x \land y} \right)"),
        ("-(x and y)", r"-\left( {x \land y} \right)"),
        ("~(x and y)", r"\mathord{\sim} \left( {x \land y} \right)"),
        ("not (x and y)", r"\lnot \left( {x \land y} \right)"),
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
        ("a == f(b)", r"{a = \mathrm{f}\left(b\right)}"),
        ("f(a) == b", r"{\mathrm{f}\left(a\right) = b}"),
        # With BinOp
        ("a == b + c", r"{a = b + c}"),
        ("a + b == c", r"{a + b = c}"),
        # With UnaryOp
        ("a == -b", r"{a = -b}"),
        ("-a == b", r"{-a = b}"),
        ("a == (not b)", r"{a = \lnot b}"),
        ("(not a) == b", r"{\lnot a = b}"),
        # With BoolOp
        ("a == (b and c)", r"{a = \left( {b \land c} \right)}"),
        ("(a and b) == c", r"{\left( {a \land b} \right) = c}"),
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
        ("(a or b) and c", r"{\left( {a \lor b} \right) \land c}"),
        ("a and b or c", r"{{a \land b} \lor c}"),
        ("a and (b or c)", r"{a \land \left( {b \lor c} \right)}"),
        # With Call
        ("a and f(b)", r"{a \land \mathrm{f}\left(b\right)}"),
        ("f(a) and b", r"{\mathrm{f}\left(a\right) \land b}"),
        ("a or f(b)", r"{a \lor \mathrm{f}\left(b\right)}"),
        ("f(a) or b", r"{\mathrm{f}\left(a\right) \lor b}"),
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


@pytest.mark.parametrize(
    "code,latex",
    [
        ("np.ndarray([1])", r"\begin{bmatrix} 1 \end{bmatrix}"),
        ("np.ndarray([1, 2])", r"\begin{bmatrix} 1 & 2 \end{bmatrix}"),
        (
            "np.ndarray([[1, 2], [3, 4]])",
            r"\begin{bmatrix} 1 & 2 \\" r"3 & 4 \end{bmatrix}",
        ),
        (
            "np.ndarray([[1,2], [3,4], [5,6]])",
            r"\begin{bmatrix}"
            r"1 & 2 \\" r"3 & 4 \\" r"5 & 6 " r"\end{bmatrix}"
        ),
        ("np.ndarray([[1], [2], [3]])", r"\begin{bmatrix} 1 \\ 2 \\ 3 \end{bmatrix}"),
    ],
)
def test_numpy_array(code: str, latex: str) -> None:
    tree = ast.parse(code).body[0].value
    assert isinstance(tree, ast.Call)
    assert function_codegen.FunctionCodegen().visit(tree) == latex
