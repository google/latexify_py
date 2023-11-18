"""Tests for latexify.codegen.expression_codegen."""

from __future__ import annotations

import ast

import pytest

from latexify import ast_utils, exceptions, test_utils
from latexify.codegen import expression_codegen


def test_generic_visit() -> None:
    class UnknownNode(ast.AST):
        pass

    with pytest.raises(
        exceptions.LatexifyNotSupportedError,
        match=r"^Unsupported AST: UnknownNode$",
    ):
        expression_codegen.ExpressionCodegen().visit(UnknownNode())


@pytest.mark.parametrize(
    "code,latex",
    [
        ("()", r"\mathopen{}\left(  \mathclose{}\right)"),
        ("(x,)", r"\mathopen{}\left( x \mathclose{}\right)"),
        ("(x, y)", r"\mathopen{}\left( x, y \mathclose{}\right)"),
        ("(x, y, z)", r"\mathopen{}\left( x, y, z \mathclose{}\right)"),
    ],
)
def test_visit_tuple(code: str, latex: str) -> None:
    node = ast_utils.parse_expr(code)
    assert isinstance(node, ast.Tuple)
    assert expression_codegen.ExpressionCodegen().visit(node) == latex


@pytest.mark.parametrize(
    "code,latex",
    [
        ("[]", r"\mathopen{}\left[  \mathclose{}\right]"),
        ("[x]", r"\mathopen{}\left[ x \mathclose{}\right]"),
        ("[x, y]", r"\mathopen{}\left[ x, y \mathclose{}\right]"),
        ("[x, y, z]", r"\mathopen{}\left[ x, y, z \mathclose{}\right]"),
    ],
)
def test_visit_list(code: str, latex: str) -> None:
    node = ast_utils.parse_expr(code)
    assert isinstance(node, ast.List)
    assert expression_codegen.ExpressionCodegen().visit(node) == latex


@pytest.mark.parametrize(
    "code,latex",
    [
        # TODO(odashi): Support set().
        # ("set()", r"\mathopen{}\left\{  \mathclose{}\right\}"),
        ("{x}", r"\mathopen{}\left\{ x \mathclose{}\right\}"),
        ("{x, y}", r"\mathopen{}\left\{ x, y \mathclose{}\right\}"),
        ("{x, y, z}", r"\mathopen{}\left\{ x, y, z \mathclose{}\right\}"),
    ],
)
def test_visit_set(code: str, latex: str) -> None:
    node = ast_utils.parse_expr(code)
    assert isinstance(node, ast.Set)
    assert expression_codegen.ExpressionCodegen().visit(node) == latex


@pytest.mark.parametrize(
    "code,latex",
    [
        ("[i for i in n]", r"\mathopen{}\left[ i \mid i \in n \mathclose{}\right]"),
        (
            "[i for i in n if i > 0]",
            r"\mathopen{}\left[ i \mid"
            r" \mathopen{}\left( i \in n \mathclose{}\right)"
            r" \land \mathopen{}\left( i > 0 \mathclose{}\right)"
            r" \mathclose{}\right]",
        ),
        (
            "[i for i in n if i > 0 if f(i)]",
            r"\mathopen{}\left[ i \mid"
            r" \mathopen{}\left( i \in n \mathclose{}\right)"
            r" \land \mathopen{}\left( i > 0 \mathclose{}\right)"
            r" \land \mathopen{}\left( f \mathopen{}\left("
            r" i \mathclose{}\right) \mathclose{}\right)"
            r" \mathclose{}\right]",
        ),
        (
            "[i for k in n for i in k]",
            r"\mathopen{}\left[ i \mid k \in n, i \in k" r" \mathclose{}\right]",
        ),
        (
            "[i for k in n for i in k if i > 0]",
            r"\mathopen{}\left[ i \mid"
            r" k \in n,"
            r" \mathopen{}\left( i \in k \mathclose{}\right)"
            r" \land \mathopen{}\left( i > 0 \mathclose{}\right)"
            r" \mathclose{}\right]",
        ),
        (
            "[i for k in n if f(k) for i in k if i > 0]",
            r"\mathopen{}\left[ i \mid"
            r" \mathopen{}\left( k \in n \mathclose{}\right)"
            r" \land \mathopen{}\left( f \mathopen{}\left("
            r" k \mathclose{}\right) \mathclose{}\right),"
            r" \mathopen{}\left( i \in k \mathclose{}\right)"
            r" \land \mathopen{}\left( i > 0 \mathclose{}\right)"
            r" \mathclose{}\right]",
        ),
    ],
)
def test_visit_listcomp(code: str, latex: str) -> None:
    node = ast_utils.parse_expr(code)
    assert isinstance(node, ast.ListComp)
    assert expression_codegen.ExpressionCodegen().visit(node) == latex


@pytest.mark.parametrize(
    "code,latex",
    [
        ("{i for i in n}", r"\mathopen{}\left\{ i \mid i \in n \mathclose{}\right\}"),
        (
            "{i for i in n if i > 0}",
            r"\mathopen{}\left\{ i \mid"
            r" \mathopen{}\left( i \in n \mathclose{}\right)"
            r" \land \mathopen{}\left( i > 0 \mathclose{}\right)"
            r" \mathclose{}\right\}",
        ),
        (
            "{i for i in n if i > 0 if f(i)}",
            r"\mathopen{}\left\{ i \mid"
            r" \mathopen{}\left( i \in n \mathclose{}\right)"
            r" \land \mathopen{}\left( i > 0 \mathclose{}\right)"
            r" \land \mathopen{}\left( f \mathopen{}\left("
            r" i \mathclose{}\right) \mathclose{}\right)"
            r" \mathclose{}\right\}",
        ),
        (
            "{i for k in n for i in k}",
            r"\mathopen{}\left\{ i \mid k \in n, i \in k" r" \mathclose{}\right\}",
        ),
        (
            "{i for k in n for i in k if i > 0}",
            r"\mathopen{}\left\{ i \mid"
            r" k \in n,"
            r" \mathopen{}\left( i \in k \mathclose{}\right)"
            r" \land \mathopen{}\left( i > 0 \mathclose{}\right)"
            r" \mathclose{}\right\}",
        ),
        (
            "{i for k in n if f(k) for i in k if i > 0}",
            r"\mathopen{}\left\{ i \mid"
            r" \mathopen{}\left( k \in n \mathclose{}\right)"
            r" \land \mathopen{}\left( f \mathopen{}\left("
            r" k \mathclose{}\right) \mathclose{}\right),"
            r" \mathopen{}\left( i \in k \mathclose{}\right)"
            r" \land \mathopen{}\left( i > 0 \mathclose{}\right)"
            r" \mathclose{}\right\}",
        ),
    ],
)
def test_visit_setcomp(code: str, latex: str) -> None:
    node = ast_utils.parse_expr(code)
    assert isinstance(node, ast.SetComp)
    assert expression_codegen.ExpressionCodegen().visit(node) == latex


@pytest.mark.parametrize(
    "code,latex",
    [
        ("foo(x)", r"\mathrm{foo} \mathopen{}\left( x \mathclose{}\right)"),
        ("f(x)", r"f \mathopen{}\left( x \mathclose{}\right)"),
        ("f(-x)", r"f \mathopen{}\left( -x \mathclose{}\right)"),
        ("f(x + y)", r"f \mathopen{}\left( x + y \mathclose{}\right)"),
        (
            "f(f(x))",
            r"f \mathopen{}\left("
            r" f \mathopen{}\left( x \mathclose{}\right)"
            r" \mathclose{}\right)",
        ),
        ("f(sqrt(x))", r"f \mathopen{}\left( \sqrt{ x } \mathclose{}\right)"),
        ("f(sin(x))", r"f \mathopen{}\left( \sin x \mathclose{}\right)"),
        ("f(factorial(x))", r"f \mathopen{}\left( x ! \mathclose{}\right)"),
        ("f(x, y)", r"f \mathopen{}\left( x, y \mathclose{}\right)"),
        ("sqrt(x)", r"\sqrt{ x }"),
        ("sqrt(-x)", r"\sqrt{ -x }"),
        ("sqrt(x + y)", r"\sqrt{ x + y }"),
        ("sqrt(f(x))", r"\sqrt{ f \mathopen{}\left( x \mathclose{}\right) }"),
        ("sqrt(sqrt(x))", r"\sqrt{ \sqrt{ x } }"),
        ("sqrt(sin(x))", r"\sqrt{ \sin x }"),
        ("sqrt(factorial(x))", r"\sqrt{ x ! }"),
        ("sin(x)", r"\sin x"),
        ("sin(-x)", r"\sin \mathopen{}\left( -x \mathclose{}\right)"),
        ("sin(x + y)", r"\sin \mathopen{}\left( x + y \mathclose{}\right)"),
        ("sin(f(x))", r"\sin f \mathopen{}\left( x \mathclose{}\right)"),
        ("sin(sqrt(x))", r"\sin \sqrt{ x }"),
        ("sin(sin(x))", r"\sin \sin x"),
        ("sin(factorial(x))", r"\sin \mathopen{}\left( x ! \mathclose{}\right)"),
        ("factorial(x)", r"x !"),
        ("factorial(-x)", r"\mathopen{}\left( -x \mathclose{}\right) !"),
        ("factorial(x + y)", r"\mathopen{}\left( x + y \mathclose{}\right) !"),
        (
            "factorial(f(x))",
            r"\mathopen{}\left("
            r" f \mathopen{}\left( x \mathclose{}\right)"
            r" \mathclose{}\right) !",
        ),
        ("factorial(sqrt(x))", r"\mathopen{}\left( \sqrt{ x } \mathclose{}\right) !"),
        ("factorial(sin(x))", r"\mathopen{}\left( \sin x \mathclose{}\right) !"),
        ("factorial(factorial(x))", r"\mathopen{}\left( x ! \mathclose{}\right) !"),
    ],
)
def test_visit_call(code: str, latex: str) -> None:
    node = ast_utils.parse_expr(code)
    assert isinstance(node, ast.Call)
    assert expression_codegen.ExpressionCodegen().visit(node) == latex


@pytest.mark.parametrize(
    "code,latex",
    [
        ("log(x)**2", r"\mathopen{}\left( \log x \mathclose{}\right)^{2}"),
        ("log(x**2)", r"\log \mathopen{}\left( x^{2} \mathclose{}\right)"),
        (
            "log(x**2)**3",
            r"\mathopen{}\left("
            r" \log \mathopen{}\left( x^{2} \mathclose{}\right)"
            r" \mathclose{}\right)^{3}",
        ),
    ],
)
def test_visit_call_with_pow(code: str, latex: str) -> None:
    node = ast_utils.parse_expr(code)
    assert isinstance(node, (ast.Call, ast.BinOp))
    assert expression_codegen.ExpressionCodegen().visit(node) == latex


@pytest.mark.parametrize(
    "src_suffix,dest_suffix",
    [
        # No arguments
        ("()", r" \mathopen{}\left( \mathclose{}\right)"),
        # No comprehension
        ("(x)", r" x"),
        (
            "([1, 2])",
            r" \mathopen{}\left[ 1, 2 \mathclose{}\right]",
        ),
        (
            "({1, 2})",
            r" \mathopen{}\left\{ 1, 2 \mathclose{}\right\}",
        ),
        ("(f(x))", r" f \mathopen{}\left( x \mathclose{}\right)"),
        # Single comprehension
        ("(i for i in x)", r"_{i \in x}^{} \mathopen{}\left({i}\mathclose{}\right)"),
        (
            "(i for i in [1, 2])",
            r"_{i \in \mathopen{}\left[ 1, 2 \mathclose{}\right]}^{} "
            r"\mathopen{}\left({i}\mathclose{}\right)",
        ),
        (
            "(i for i in {1, 2})",
            r"_{i \in \mathopen{}\left\{ 1, 2 \mathclose{}\right\}}^{}"
            r" \mathopen{}\left({i}\mathclose{}\right)",
        ),
        (
            "(i for i in f(x))",
            r"_{i \in f \mathopen{}\left( x \mathclose{}\right)}^{}"
            r" \mathopen{}\left({i}\mathclose{}\right)",
        ),
        (
            "(i for i in range(n))",
            r"_{i = 0}^{n - 1} \mathopen{}\left({i}\mathclose{}\right)",
        ),
        (
            "(i for i in range(n + 1))",
            r"_{i = 0}^{n} \mathopen{}\left({i}\mathclose{}\right)",
        ),
        (
            "(i for i in range(n + 2))",
            r"_{i = 0}^{n + 1} \mathopen{}\left({i}\mathclose{}\right)",
        ),
        (
            # ast.parse() does not recognize negative integers.
            "(i for i in range(n - -1))",
            r"_{i = 0}^{n - -1 - 1} \mathopen{}\left({i}\mathclose{}\right)",
        ),
        (
            "(i for i in range(n - 1))",
            r"_{i = 0}^{n - 2} \mathopen{}\left({i}\mathclose{}\right)",
        ),
        (
            "(i for i in range(n + m))",
            r"_{i = 0}^{n + m - 1} \mathopen{}\left({i}\mathclose{}\right)",
        ),
        (
            "(i for i in range(n - m))",
            r"_{i = 0}^{n - m - 1} \mathopen{}\left({i}\mathclose{}\right)",
        ),
        (
            "(i for i in range(3))",
            r"_{i = 0}^{2} \mathopen{}\left({i}\mathclose{}\right)",
        ),
        (
            "(i for i in range(3 + 1))",
            r"_{i = 0}^{3} \mathopen{}\left({i}\mathclose{}\right)",
        ),
        (
            "(i for i in range(3 + 2))",
            r"_{i = 0}^{3 + 1} \mathopen{}\left({i}\mathclose{}\right)",
        ),
        (
            "(i for i in range(3 - 1))",
            r"_{i = 0}^{3 - 2} \mathopen{}\left({i}\mathclose{}\right)",
        ),
        (
            # ast.parse() does not recognize negative integers.
            "(i for i in range(3 - -1))",
            r"_{i = 0}^{3 - -1 - 1} \mathopen{}\left({i}\mathclose{}\right)",
        ),
        (
            "(i for i in range(3 + m))",
            r"_{i = 0}^{3 + m - 1} \mathopen{}\left({i}\mathclose{}\right)",
        ),
        (
            "(i for i in range(3 - m))",
            r"_{i = 0}^{3 - m - 1} \mathopen{}\left({i}\mathclose{}\right)",
        ),
        (
            "(i for i in range(n, m))",
            r"_{i = n}^{m - 1} \mathopen{}\left({i}\mathclose{}\right)",
        ),
        (
            "(i for i in range(1, m))",
            r"_{i = 1}^{m - 1} \mathopen{}\left({i}\mathclose{}\right)",
        ),
        (
            "(i for i in range(n, 3))",
            r"_{i = n}^{2} \mathopen{}\left({i}\mathclose{}\right)",
        ),
        (
            "(i for i in range(n, m, k))",
            r"_{i \in \mathrm{range} \mathopen{}\left( n, m, k \mathclose{}\right)}^{}"
            r" \mathopen{}\left({i}\mathclose{}\right)",
        ),
    ],
)
def test_visit_call_sum_prod(src_suffix: str, dest_suffix: str) -> None:
    for src_fn, dest_fn in [("fsum", r"\sum"), ("sum", r"\sum"), ("prod", r"\prod")]:
        node = ast_utils.parse_expr(src_fn + src_suffix)
        assert isinstance(node, ast.Call)
        assert (
            expression_codegen.ExpressionCodegen().visit(node) == dest_fn + dest_suffix
        )


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
            "prod(i for y in x for i in y)",
            r"\prod_{y \in x}^{} \prod_{i \in y}^{} "
            r"\mathopen{}\left({i}\mathclose{}\right)",
        ),
        (
            "prod(i for y in x for z in y for i in z)",
            r"\prod_{y \in x}^{} \prod_{z \in y}^{} \prod_{i \in z}^{} "
            r"\mathopen{}\left({i}\mathclose{}\right)",
        ),
        # reduce stop parameter
        (
            "sum(i for i in range(n+1))",
            r"\sum_{i = 0}^{n} \mathopen{}\left({i}\mathclose{}\right)",
        ),
        (
            "prod(i for i in range(n-1))",
            r"\prod_{i = 0}^{n - 2} \mathopen{}\left({i}\mathclose{}\right)",
        ),
        # reduce stop parameter
        (
            "sum(i for i in range(n+1))",
            r"\sum_{i = 0}^{n} \mathopen{}\left({i}\mathclose{}\right)",
        ),
        (
            "prod(i for i in range(n-1))",
            r"\prod_{i = 0}^{n - 2} \mathopen{}\left({i}\mathclose{}\right)",
        ),
    ],
)
def test_visit_call_sum_prod_multiple_comprehension(code: str, latex: str) -> None:
    node = ast_utils.parse_expr(code)
    assert isinstance(node, ast.Call)
    assert expression_codegen.ExpressionCodegen().visit(node) == latex


@pytest.mark.parametrize(
    "src_suffix,dest_suffix",
    [
        (
            "(i for i in x if i < y)",
            r"_{\mathopen{}\left( i \in x \mathclose{}\right) "
            r"\land \mathopen{}\left( i < y \mathclose{}\right)}^{} "
            r"\mathopen{}\left({i}\mathclose{}\right)",
        ),
        (
            "(i for i in x if i < y if f(i))",
            r"_{\mathopen{}\left( i \in x \mathclose{}\right)"
            r" \land \mathopen{}\left( i < y \mathclose{}\right)"
            r" \land \mathopen{}\left( f \mathopen{}\left("
            r" i \mathclose{}\right) \mathclose{}\right)}^{}"
            r" \mathopen{}\left({i}\mathclose{}\right)",
        ),
    ],
)
def test_visit_call_sum_prod_with_if(src_suffix: str, dest_suffix: str) -> None:
    for src_fn, dest_fn in [("sum", r"\sum"), ("prod", r"\prod")]:
        node = ast_utils.parse_expr(src_fn + src_suffix)
        assert isinstance(node, ast.Call)
        assert (
            expression_codegen.ExpressionCodegen().visit(node) == dest_fn + dest_suffix
        )


@pytest.mark.parametrize(
    "code,latex",
    [
        (
            "x if x < y else y",
            r"\left\{ \begin{array}{ll}"
            r" x, & \mathrm{if} \ x < y \\"
            r" y, & \mathrm{otherwise}"
            r" \end{array} \right.",
        ),
        (
            "x if x < y else (y if y < z else z)",
            r"\left\{ \begin{array}{ll}"
            r" x, & \mathrm{if} \ x < y \\"
            r" y, & \mathrm{if} \ y < z \\"
            r" z, & \mathrm{otherwise}"
            r" \end{array} \right.",
        ),
        (
            "x if x < y else (y if y < z else (z if z < w else w))",
            r"\left\{ \begin{array}{ll}"
            r" x, & \mathrm{if} \ x < y \\"
            r" y, & \mathrm{if} \ y < z \\"
            r" z, & \mathrm{if} \ z < w \\"
            r" w, & \mathrm{otherwise}"
            r" \end{array} \right.",
        ),
    ],
)
def test_if_then_else(code: str, latex: str) -> None:
    node = ast_utils.parse_expr(code)
    assert isinstance(node, ast.IfExp)
    assert expression_codegen.ExpressionCodegen().visit(node) == latex


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
        ("x * (y + z)", r"x \cdot \mathopen{}\left( y + z \mathclose{}\right)"),
        ("x @ (y + z)", r"x \cdot \mathopen{}\left( y + z \mathclose{}\right)"),
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
        ("x**f(y)", r"x^{f \mathopen{}\left( y \mathclose{}\right)}"),
        (
            "f(x)**y",
            r"\mathopen{}\left("
            r" f \mathopen{}\left( x \mathclose{}\right)"
            r" \mathclose{}\right)^{y}",
        ),
        ("x * f(y)", r"x \cdot f \mathopen{}\left( y \mathclose{}\right)"),
        ("f(x) * y", r"f \mathopen{}\left( x \mathclose{}\right) \cdot y"),
        ("x / f(y)", r"\frac{x}{f \mathopen{}\left( y \mathclose{}\right)}"),
        ("f(x) / y", r"\frac{f \mathopen{}\left( x \mathclose{}\right)}{y}"),
        ("x + f(y)", r"x + f \mathopen{}\left( y \mathclose{}\right)"),
        ("f(x) + y", r"f \mathopen{}\left( x \mathclose{}\right) + y"),
        # With is_wrapped Call
        ("sqrt(x) ** y", r"\sqrt{ x }^{y}"),
        # With UnaryOp
        ("x**-y", r"x^{-y}"),
        ("(-x)**y", r"\mathopen{}\left( -x \mathclose{}\right)^{y}"),
        ("x * -y", r"x \cdot -y"),
        ("-x * y", r"-x y"),
        ("x / -y", r"\frac{x}{-y}"),
        ("-x / y", r"\frac{-x}{y}"),
        ("x + -y", r"x + -y"),
        ("-x + y", r"-x + y"),
        # With Compare
        ("x**(y == z)", r"x^{y = z}"),
        ("(x == y)**z", r"\mathopen{}\left( x = y \mathclose{}\right)^{z}"),
        ("x * (y == z)", r"x \cdot \mathopen{}\left( y = z \mathclose{}\right)"),
        ("(x == y) * z", r"\mathopen{}\left( x = y \mathclose{}\right) z"),
        ("x / (y == z)", r"\frac{x}{y = z}"),
        ("(x == y) / z", r"\frac{x = y}{z}"),
        ("x + (y == z)", r"x + \mathopen{}\left( y = z \mathclose{}\right)"),
        ("(x == y) + z", r"\mathopen{}\left( x = y \mathclose{}\right) + z"),
        # With BoolOp
        ("x**(y and z)", r"x^{y \land z}"),
        ("(x and y)**z", r"\mathopen{}\left( x \land y \mathclose{}\right)^{z}"),
        ("x * (y and z)", r"x \cdot \mathopen{}\left( y \land z \mathclose{}\right)"),
        ("(x and y) * z", r"\mathopen{}\left( x \land y \mathclose{}\right) z"),
        ("x / (y and z)", r"\frac{x}{y \land z}"),
        ("(x and y) / z", r"\frac{x \land y}{z}"),
        ("x + (y and z)", r"x + \mathopen{}\left( y \land z \mathclose{}\right)"),
        ("(x and y) + z", r"\mathopen{}\left( x \land y \mathclose{}\right) + z"),
    ],
)
def test_visit_binop(code: str, latex: str) -> None:
    tree = ast_utils.parse_expr(code)
    assert isinstance(tree, ast.BinOp)
    assert expression_codegen.ExpressionCodegen().visit(tree) == latex


@pytest.mark.parametrize(
    "code,latex",
    [
        # With literals
        ("+x", r"+x"),
        ("-x", r"-x"),
        ("~x", r"\mathord{\sim} x"),
        ("not x", r"\lnot x"),
        # With Call
        ("+f(x)", r"+f \mathopen{}\left( x \mathclose{}\right)"),
        ("-f(x)", r"-f \mathopen{}\left( x \mathclose{}\right)"),
        ("~f(x)", r"\mathord{\sim} f \mathopen{}\left( x \mathclose{}\right)"),
        ("not f(x)", r"\lnot f \mathopen{}\left( x \mathclose{}\right)"),
        # With BinOp
        ("+(x + y)", r"+\mathopen{}\left( x + y \mathclose{}\right)"),
        ("-(x + y)", r"-\mathopen{}\left( x + y \mathclose{}\right)"),
        ("~(x + y)", r"\mathord{\sim} \mathopen{}\left( x + y \mathclose{}\right)"),
        ("not x + y", r"\lnot \mathopen{}\left( x + y \mathclose{}\right)"),
        # With Compare
        ("+(x == y)", r"+\mathopen{}\left( x = y \mathclose{}\right)"),
        ("-(x == y)", r"-\mathopen{}\left( x = y \mathclose{}\right)"),
        ("~(x == y)", r"\mathord{\sim} \mathopen{}\left( x = y \mathclose{}\right)"),
        ("not x == y", r"\lnot \mathopen{}\left( x = y \mathclose{}\right)"),
        # With BoolOp
        ("+(x and y)", r"+\mathopen{}\left( x \land y \mathclose{}\right)"),
        ("-(x and y)", r"-\mathopen{}\left( x \land y \mathclose{}\right)"),
        (
            "~(x and y)",
            r"\mathord{\sim} \mathopen{}\left( x \land y \mathclose{}\right)",
        ),
        ("not (x and y)", r"\lnot \mathopen{}\left( x \land y \mathclose{}\right)"),
    ],
)
def test_visit_unaryop(code: str, latex: str) -> None:
    tree = ast_utils.parse_expr(code)
    assert isinstance(tree, ast.UnaryOp)
    assert expression_codegen.ExpressionCodegen().visit(tree) == latex


@pytest.mark.parametrize(
    "code,latex",
    [
        # 1 comparator
        ("a == b", "a = b"),
        ("a > b", "a > b"),
        ("a >= b", r"a \ge b"),
        ("a in b", r"a \in b"),
        ("a is b", r"a \equiv b"),
        ("a is not b", r"a \not\equiv b"),
        ("a < b", "a < b"),
        ("a <= b", r"a \le b"),
        ("a != b", r"a \ne b"),
        ("a not in b", r"a \notin b"),
        # 2 comparators
        ("a == b == c", "a = b = c"),
        ("a == b > c", "a = b > c"),
        ("a == b >= c", r"a = b \ge c"),
        ("a == b < c", "a = b < c"),
        ("a == b <= c", r"a = b \le c"),
        ("a > b == c", "a > b = c"),
        ("a > b > c", "a > b > c"),
        ("a > b >= c", r"a > b \ge c"),
        ("a >= b == c", r"a \ge b = c"),
        ("a >= b > c", r"a \ge b > c"),
        ("a >= b >= c", r"a \ge b \ge c"),
        ("a < b == c", "a < b = c"),
        ("a < b < c", "a < b < c"),
        ("a < b <= c", r"a < b \le c"),
        ("a <= b == c", r"a \le b = c"),
        ("a <= b < c", r"a \le b < c"),
        ("a <= b <= c", r"a \le b \le c"),
        # With Call
        ("a == f(b)", r"a = f \mathopen{}\left( b \mathclose{}\right)"),
        ("f(a) == b", r"f \mathopen{}\left( a \mathclose{}\right) = b"),
        # With BinOp
        ("a == b + c", r"a = b + c"),
        ("a + b == c", r"a + b = c"),
        # With UnaryOp
        ("a == -b", r"a = -b"),
        ("-a == b", r"-a = b"),
        ("a == (not b)", r"a = \lnot b"),
        ("(not a) == b", r"\lnot a = b"),
        # With BoolOp
        ("a == (b and c)", r"a = \mathopen{}\left( b \land c \mathclose{}\right)"),
        ("(a and b) == c", r"\mathopen{}\left( a \land b \mathclose{}\right) = c"),
    ],
)
def test_visit_compare(code: str, latex: str) -> None:
    tree = ast_utils.parse_expr(code)
    assert isinstance(tree, ast.Compare)
    assert expression_codegen.ExpressionCodegen().visit(tree) == latex


@pytest.mark.parametrize(
    "code,latex",
    [
        # With literals
        ("a and b", r"a \land b"),
        ("a and b and c", r"a \land b \land c"),
        ("a or b", r"a \lor b"),
        ("a or b or c", r"a \lor b \lor c"),
        ("a or b and c", r"a \lor b \land c"),
        (
            "(a or b) and c",
            r"\mathopen{}\left( a \lor b \mathclose{}\right) \land c",
        ),
        ("a and b or c", r"a \land b \lor c"),
        (
            "a and (b or c)",
            r"a \land \mathopen{}\left( b \lor c \mathclose{}\right)",
        ),
        # With Call
        ("a and f(b)", r"a \land f \mathopen{}\left( b \mathclose{}\right)"),
        ("f(a) and b", r"f \mathopen{}\left( a \mathclose{}\right) \land b"),
        ("a or f(b)", r"a \lor f \mathopen{}\left( b \mathclose{}\right)"),
        ("f(a) or b", r"f \mathopen{}\left( a \mathclose{}\right) \lor b"),
        # With BinOp
        ("a and b + c", r"a \land b + c"),
        ("a + b and c", r"a + b \land c"),
        ("a or b + c", r"a \lor b + c"),
        ("a + b or c", r"a + b \lor c"),
        # With UnaryOp
        ("a and not b", r"a \land \lnot b"),
        ("not a and b", r"\lnot a \land b"),
        ("a or not b", r"a \lor \lnot b"),
        ("not a or b", r"\lnot a \lor b"),
        # With Compare
        ("a and b == c", r"a \land b = c"),
        ("a == b and c", r"a = b \land c"),
        ("a or b == c", r"a \lor b = c"),
        ("a == b or c", r"a = b \lor c"),
    ],
)
def test_visit_boolop(code: str, latex: str) -> None:
    tree = ast_utils.parse_expr(code)
    assert isinstance(tree, ast.BoolOp)
    assert expression_codegen.ExpressionCodegen().visit(tree) == latex


@test_utils.require_at_most(7)
@pytest.mark.parametrize(
    "code,cls,latex",
    [
        ("0", ast.Num, "0"),
        ("1", ast.Num, "1"),
        ("0.0", ast.Num, "0.0"),
        ("1.5", ast.Num, "1.5"),
        ("0.0j", ast.Num, "0j"),
        ("1.0j", ast.Num, "1j"),
        ("1.5j", ast.Num, "1.5j"),
        ('"abc"', ast.Str, r'\textrm{"abc"}'),
        ('b"abc"', ast.Bytes, r"\textrm{b'abc'}"),
        ("None", ast.NameConstant, r"\mathrm{None}"),
        ("False", ast.NameConstant, r"\mathrm{False}"),
        ("True", ast.NameConstant, r"\mathrm{True}"),
        ("...", ast.Ellipsis, r"\cdots"),
    ],
)
def test_visit_constant_lagacy(code: str, cls: type[ast.expr], latex: str) -> None:
    tree = ast_utils.parse_expr(code)
    assert isinstance(tree, cls)
    assert expression_codegen.ExpressionCodegen().visit(tree) == latex


@test_utils.require_at_least(8)
@pytest.mark.parametrize(
    "code,latex",
    [
        ("0", "0"),
        ("1", "1"),
        ("0.0", "0.0"),
        ("1.5", "1.5"),
        ("0.0j", "0j"),
        ("1.0j", "1j"),
        ("1.5j", "1.5j"),
        ('"abc"', r'\textrm{"abc"}'),
        ('b"abc"', r"\textrm{b'abc'}"),
        ("None", r"\mathrm{None}"),
        ("False", r"\mathrm{False}"),
        ("True", r"\mathrm{True}"),
        ("...", r"\cdots"),
    ],
)
def test_visit_constant(code: str, latex: str) -> None:
    tree = ast_utils.parse_expr(code)
    assert isinstance(tree, ast.Constant)
    assert expression_codegen.ExpressionCodegen().visit(tree) == latex


@pytest.mark.parametrize(
    "code,latex",
    [
        ("x[0]", "x_{0}"),
        ("x[0][1]", "x_{0, 1}"),
        ("x[0][1][2]", "x_{0, 1, 2}"),
        ("x[foo]", r"x_{\mathrm{foo}}"),
        ("x[floor(x)]", r"x_{\mathopen{}\left\lfloor x \mathclose{}\right\rfloor}"),
    ],
)
def test_visit_subscript(code: str, latex: str) -> None:
    tree = ast_utils.parse_expr(code)
    assert isinstance(tree, ast.Subscript)
    assert expression_codegen.ExpressionCodegen().visit(tree) == latex


@pytest.mark.parametrize(
    "code,latex",
    [
        ("a - b", r"a \setminus b"),
        ("a & b", r"a \cap b"),
        ("a ^ b", r"a \mathbin{\triangle} b"),
        ("a | b", r"a \cup b"),
    ],
)
def test_visit_binop_use_set_symbols(code: str, latex: str) -> None:
    tree = ast_utils.parse_expr(code)
    assert isinstance(tree, ast.BinOp)
    assert (
        expression_codegen.ExpressionCodegen(use_set_symbols=True).visit(tree) == latex
    )


@pytest.mark.parametrize(
    "code,latex",
    [
        ("a < b", r"a \subset b"),
        ("a <= b", r"a \subseteq b"),
        ("a > b", r"a \supset b"),
        ("a >= b", r"a \supseteq b"),
    ],
)
def test_visit_compare_use_set_symbols(code: str, latex: str) -> None:
    tree = ast_utils.parse_expr(code)
    assert isinstance(tree, ast.Compare)
    assert (
        expression_codegen.ExpressionCodegen(use_set_symbols=True).visit(tree) == latex
    )


@pytest.mark.parametrize(
    "code,latex",
    [
        ("array(1)", r"\mathrm{array} \mathopen{}\left( 1 \mathclose{}\right)"),
        (
            "array([])",
            r"\mathrm{array} \mathopen{}\left("
            r" \mathopen{}\left[  \mathclose{}\right]"
            r" \mathclose{}\right)",
        ),
        ("array([1])", r"\begin{bmatrix} 1 \end{bmatrix}"),
        ("array([1, 2, 3])", r"\begin{bmatrix} 1 & 2 & 3 \end{bmatrix}"),
        (
            "array([[]])",
            r"\mathrm{array} \mathopen{}\left("
            r" \mathopen{}\left[ \mathopen{}\left["
            r"  \mathclose{}\right] \mathclose{}\right]"
            r" \mathclose{}\right)",
        ),
        ("array([[1]])", r"\begin{bmatrix} 1 \end{bmatrix}"),
        ("array([[1], [2], [3]])", r"\begin{bmatrix} 1 \\ 2 \\ 3 \end{bmatrix}"),
        (
            "array([[1], [2], [3, 4]])",
            r"\mathrm{array} \mathopen{}\left("
            r" \mathopen{}\left["
            r" \mathopen{}\left[ 1 \mathclose{}\right],"
            r" \mathopen{}\left[ 2 \mathclose{}\right],"
            r" \mathopen{}\left[ 3, 4 \mathclose{}\right]"
            r" \mathclose{}\right]"
            r" \mathclose{}\right)",
        ),
        (
            "array([[1, 2], [3, 4], [5, 6]])",
            r"\begin{bmatrix} 1 & 2 \\ 3 & 4 \\ 5 & 6 \end{bmatrix}",
        ),
        # Only checks two cases for ndarray.
        ("ndarray(1)", r"\mathrm{ndarray} \mathopen{}\left( 1 \mathclose{}\right)"),
        ("ndarray([1])", r"\begin{bmatrix} 1 \end{bmatrix}"),
    ],
)
def test_numpy_array(code: str, latex: str) -> None:
    tree = ast_utils.parse_expr(code)
    assert isinstance(tree, ast.Call)
    assert expression_codegen.ExpressionCodegen().visit(tree) == latex


@pytest.mark.parametrize(
    "code,latex",
    [
        ("zeros(0)", r"\mathbf{0}^{1 \times 0}"),
        ("zeros(1)", r"\mathbf{0}^{1 \times 1}"),
        ("zeros(2)", r"\mathbf{0}^{1 \times 2}"),
        ("zeros(())", r"0"),
        ("zeros((0,))", r"\mathbf{0}^{1 \times 0}"),
        ("zeros((1,))", r"\mathbf{0}^{1 \times 1}"),
        ("zeros((2,))", r"\mathbf{0}^{1 \times 2}"),
        ("zeros((0, 0))", r"\mathbf{0}^{0 \times 0}"),
        ("zeros((1, 1))", r"\mathbf{0}^{1 \times 1}"),
        ("zeros((2, 3))", r"\mathbf{0}^{2 \times 3}"),
        ("zeros((0, 0, 0))", r"\mathbf{0}^{0 \times 0 \times 0}"),
        ("zeros((1, 1, 1))", r"\mathbf{0}^{1 \times 1 \times 1}"),
        ("zeros((2, 3, 5))", r"\mathbf{0}^{2 \times 3 \times 5}"),
        # Unsupported
        ("zeros()", r"\mathrm{zeros} \mathopen{}\left( \mathclose{}\right)"),
        ("zeros(x)", r"\mathrm{zeros} \mathopen{}\left( x \mathclose{}\right)"),
        ("zeros(0, x)", r"\mathrm{zeros} \mathopen{}\left( 0, x \mathclose{}\right)"),
        (
            "zeros((x,))",
            r"\mathrm{zeros} \mathopen{}\left("
            r" \mathopen{}\left( x \mathclose{}\right)"
            r" \mathclose{}\right)",
        ),
    ],
)
def test_zeros(code: str, latex: str) -> None:
    tree = ast_utils.parse_expr(code)
    assert isinstance(tree, ast.Call)
    assert expression_codegen.ExpressionCodegen().visit(tree) == latex


@pytest.mark.parametrize(
    "code,latex",
    [
        ("identity(0)", r"\mathbf{I}_{0}"),
        ("identity(1)", r"\mathbf{I}_{1}"),
        ("identity(2)", r"\mathbf{I}_{2}"),
        # Unsupported
        ("identity()", r"\mathrm{identity} \mathopen{}\left( \mathclose{}\right)"),
        ("identity(x)", r"\mathrm{identity} \mathopen{}\left( x \mathclose{}\right)"),
        (
            "identity(0, x)",
            r"\mathrm{identity} \mathopen{}\left( 0, x \mathclose{}\right)",
        ),
    ],
)
def test_identity(code: str, latex: str) -> None:
    tree = ast_utils.parse_expr(code)
    assert isinstance(tree, ast.Call)
    assert expression_codegen.ExpressionCodegen().visit(tree) == latex


@pytest.mark.parametrize(
    "code,latex",
    [
        ("transpose(A)", r"\mathbf{A}^\intercal"),
        ("transpose(b)", r"\mathbf{b}^\intercal"),
        # Unsupported
        ("transpose()", r"\mathrm{transpose} \mathopen{}\left( \mathclose{}\right)"),
        ("transpose(2)", r"\mathrm{transpose} \mathopen{}\left( 2 \mathclose{}\right)"),
        (
            "transpose(a, (1, 0))",
            r"\mathrm{transpose} \mathopen{}\left( a, "
            r"\mathopen{}\left( 1, 0 \mathclose{}\right) \mathclose{}\right)",
        ),
    ],
)
def test_transpose(code: str, latex: str) -> None:
    tree = ast_utils.parse_expr(code)
    assert isinstance(tree, ast.Call)
    assert expression_codegen.ExpressionCodegen().visit(tree) == latex


@pytest.mark.parametrize(
    "code,latex",
    [
        ("det(A)", r"\det \mathopen{}\left( \mathbf{A} \mathclose{}\right)"),
        ("det(b)", r"\det \mathopen{}\left( \mathbf{b} \mathclose{}\right)"),
        (
            "det([[1, 2], [3, 4]])",
            r"\det \mathopen{}\left( \begin{bmatrix} 1 & 2 \\"
            r" 3 & 4 \end{bmatrix} \mathclose{}\right)",
        ),
        (
            "det([[1, 2, 3], [4, 5, 6], [7, 8, 9]])",
            r"\det \mathopen{}\left( \begin{bmatrix} 1 & 2 & 3 \\ 4 & 5 & 6 \\"
            r" 7 & 8 & 9 \end{bmatrix} \mathclose{}\right)",
        ),
        # Unsupported
        ("det()", r"\mathrm{det} \mathopen{}\left( \mathclose{}\right)"),
        ("det(2)", r"\mathrm{det} \mathopen{}\left( 2 \mathclose{}\right)"),
        (
            "det(a, (1, 0))",
            r"\mathrm{det} \mathopen{}\left( a, "
            r"\mathopen{}\left( 1, 0 \mathclose{}\right) \mathclose{}\right)",
        ),
    ],
)
def test_determinant(code: str, latex: str) -> None:
    tree = ast_utils.parse_expr(code)
    assert isinstance(tree, ast.Call)
    assert expression_codegen.ExpressionCodegen().visit(tree) == latex


@pytest.mark.parametrize(
    "code,latex",
    [
        (
            "matrix_rank(A)",
            r"\mathrm{rank} \mathopen{}\left( \mathbf{A} \mathclose{}\right)",
        ),
        (
            "matrix_rank(b)",
            r"\mathrm{rank} \mathopen{}\left( \mathbf{b} \mathclose{}\right)",
        ),
        (
            "matrix_rank([[1, 2], [3, 4]])",
            r"\mathrm{rank} \mathopen{}\left( \begin{bmatrix} 1 & 2 \\"
            r" 3 & 4 \end{bmatrix} \mathclose{}\right)",
        ),
        (
            "matrix_rank([[1, 2, 3], [4, 5, 6], [7, 8, 9]])",
            r"\mathrm{rank} \mathopen{}\left( \begin{bmatrix} 1 & 2 & 3 \\ 4 & 5 & 6 \\"
            r" 7 & 8 & 9 \end{bmatrix} \mathclose{}\right)",
        ),
        # Unsupported
        (
            "matrix_rank()",
            r"\mathrm{matrix\_rank} \mathopen{}\left( \mathclose{}\right)",
        ),
        (
            "matrix_rank(2)",
            r"\mathrm{matrix\_rank} \mathopen{}\left( 2 \mathclose{}\right)",
        ),
        (
            "matrix_rank(a, (1, 0))",
            r"\mathrm{matrix\_rank} \mathopen{}\left( a, "
            r"\mathopen{}\left( 1, 0 \mathclose{}\right) \mathclose{}\right)",
        ),
    ],
)
def test_matrix_rank(code: str, latex: str) -> None:
    tree = ast_utils.parse_expr(code)
    assert isinstance(tree, ast.Call)
    assert expression_codegen.ExpressionCodegen().visit(tree) == latex


@pytest.mark.parametrize(
    "code,latex",
    [
        ("matrix_power(A, 2)", r"\mathbf{A}^{2}"),
        ("matrix_power(b, 2)", r"\mathbf{b}^{2}"),
        (
            "matrix_power([[1, 2], [3, 4]], 2)",
            r"\begin{bmatrix} 1 & 2 \\ 3 & 4 \end{bmatrix}^{2}",
        ),
        (
            "matrix_power([[1, 2, 3], [4, 5, 6], [7, 8, 9]], 42)",
            r"\begin{bmatrix} 1 & 2 & 3 \\ 4 & 5 & 6 \\ 7 & 8 & 9 \end{bmatrix}^{42}",
        ),
        # Unsupported
        (
            "matrix_power()",
            r"\mathrm{matrix\_power} \mathopen{}\left( \mathclose{}\right)",
        ),
        (
            "matrix_power(2)",
            r"\mathrm{matrix\_power} \mathopen{}\left( 2 \mathclose{}\right)",
        ),
        (
            "matrix_power(a, (1, 0))",
            r"\mathrm{matrix\_power} \mathopen{}\left( a, "
            r"\mathopen{}\left( 1, 0 \mathclose{}\right) \mathclose{}\right)",
        ),
    ],
)
def test_matrix_power(code: str, latex: str) -> None:
    tree = ast_utils.parse_expr(code)
    assert isinstance(tree, ast.Call)
    assert expression_codegen.ExpressionCodegen().visit(tree) == latex


@pytest.mark.parametrize(
    "code,latex",
    [
        ("inv(A)", r"\mathbf{A}^{-1}"),
        ("inv(b)", r"\mathbf{b}^{-1}"),
        ("inv([[1, 2], [3, 4]])", r"\begin{bmatrix} 1 & 2 \\ 3 & 4 \end{bmatrix}^{-1}"),
        (
            "inv([[1, 2, 3], [4, 5, 6], [7, 8, 9]])",
            r"\begin{bmatrix} 1 & 2 & 3 \\ 4 & 5 & 6 \\ 7 & 8 & 9 \end{bmatrix}^{-1}",
        ),
        # Unsupported
        ("inv()", r"\mathrm{inv} \mathopen{}\left( \mathclose{}\right)"),
        ("inv(2)", r"\mathrm{inv} \mathopen{}\left( 2 \mathclose{}\right)"),
        (
            "inv(a, (1, 0))",
            r"\mathrm{inv} \mathopen{}\left( a, "
            r"\mathopen{}\left( 1, 0 \mathclose{}\right) \mathclose{}\right)",
        ),
    ],
)
def test_inv(code: str, latex: str) -> None:
    tree = ast_utils.parse_expr(code)
    assert isinstance(tree, ast.Call)
    assert expression_codegen.ExpressionCodegen().visit(tree) == latex


@pytest.mark.parametrize(
    "code,latex",
    [
        ("pinv(A)", r"\mathbf{A}^{+}"),
        ("pinv(b)", r"\mathbf{b}^{+}"),
        ("pinv([[1, 2], [3, 4]])", r"\begin{bmatrix} 1 & 2 \\ 3 & 4 \end{bmatrix}^{+}"),
        (
            "pinv([[1, 2, 3], [4, 5, 6], [7, 8, 9]])",
            r"\begin{bmatrix} 1 & 2 & 3 \\ 4 & 5 & 6 \\ 7 & 8 & 9 \end{bmatrix}^{+}",
        ),
        # Unsupported
        ("pinv()", r"\mathrm{pinv} \mathopen{}\left( \mathclose{}\right)"),
        ("pinv(2)", r"\mathrm{pinv} \mathopen{}\left( 2 \mathclose{}\right)"),
        (
            "pinv(a, (1, 0))",
            r"\mathrm{pinv} \mathopen{}\left( a, "
            r"\mathopen{}\left( 1, 0 \mathclose{}\right) \mathclose{}\right)",
        ),
    ],
)
def test_pinv(code: str, latex: str) -> None:
    tree = ast_utils.parse_expr(code)
    assert isinstance(tree, ast.Call)
    assert expression_codegen.ExpressionCodegen().visit(tree) == latex


# Check list for #89.
# https://github.com/google/latexify_py/issues/89#issuecomment-1344967636
@pytest.mark.parametrize(
    "left,right,latex",
    [
        ("2", "3", r"2 \cdot 3"),
        ("2", "y", "2 y"),
        ("2", "beta", r"2 \beta"),
        ("2", "bar", r"2 \mathrm{bar}"),
        ("2", "g(y)", r"2 g \mathopen{}\left( y \mathclose{}\right)"),
        ("2", "(u + v)", r"2 \mathopen{}\left( u + v \mathclose{}\right)"),
        ("x", "3", r"x \cdot 3"),
        ("x", "y", "x y"),
        ("x", "beta", r"x \beta"),
        ("x", "bar", r"x \cdot \mathrm{bar}"),
        ("x", "g(y)", r"x \cdot g \mathopen{}\left( y \mathclose{}\right)"),
        ("x", "(u + v)", r"x \cdot \mathopen{}\left( u + v \mathclose{}\right)"),
        ("alpha", "3", r"\alpha \cdot 3"),
        ("alpha", "y", r"\alpha y"),
        ("alpha", "beta", r"\alpha \beta"),
        ("alpha", "bar", r"\alpha \cdot \mathrm{bar}"),
        ("alpha", "g(y)", r"\alpha \cdot g \mathopen{}\left( y \mathclose{}\right)"),
        (
            "alpha",
            "(u + v)",
            r"\alpha \cdot \mathopen{}\left( u + v \mathclose{}\right)",
        ),
        ("foo", "3", r"\mathrm{foo} \cdot 3"),
        ("foo", "y", r"\mathrm{foo} \cdot y"),
        ("foo", "beta", r"\mathrm{foo} \cdot \beta"),
        ("foo", "bar", r"\mathrm{foo} \cdot \mathrm{bar}"),
        (
            "foo",
            "g(y)",
            r"\mathrm{foo} \cdot g \mathopen{}\left( y \mathclose{}\right)",
        ),
        (
            "foo",
            "(u + v)",
            r"\mathrm{foo} \cdot \mathopen{}\left( u + v \mathclose{}\right)",
        ),
        ("f(x)", "3", r"f \mathopen{}\left( x \mathclose{}\right) \cdot 3"),
        ("f(x)", "y", r"f \mathopen{}\left( x \mathclose{}\right) \cdot y"),
        ("f(x)", "beta", r"f \mathopen{}\left( x \mathclose{}\right) \cdot \beta"),
        (
            "f(x)",
            "bar",
            r"f \mathopen{}\left( x \mathclose{}\right) \cdot \mathrm{bar}",
        ),
        (
            "f(x)",
            "g(y)",
            r"f \mathopen{}\left( x \mathclose{}\right)"
            r" \cdot g \mathopen{}\left( y \mathclose{}\right)",
        ),
        (
            "f(x)",
            "(u + v)",
            r"f \mathopen{}\left( x \mathclose{}\right)"
            r" \cdot \mathopen{}\left( u + v \mathclose{}\right)",
        ),
        ("(s + t)", "3", r"\mathopen{}\left( s + t \mathclose{}\right) \cdot 3"),
        ("(s + t)", "y", r"\mathopen{}\left( s + t \mathclose{}\right) y"),
        ("(s + t)", "beta", r"\mathopen{}\left( s + t \mathclose{}\right) \beta"),
        (
            "(s + t)",
            "bar",
            r"\mathopen{}\left( s + t \mathclose{}\right) \mathrm{bar}",
        ),
        (
            "(s + t)",
            "g(y)",
            r"\mathopen{}\left( s + t \mathclose{}\right)"
            r" g \mathopen{}\left( y \mathclose{}\right)",
        ),
        (
            "(s + t)",
            "(u + v)",
            r"\mathopen{}\left( s + t \mathclose{}\right)"
            r" \mathopen{}\left( u + v \mathclose{}\right)",
        ),
    ],
)
def test_remove_multiply(left: str, right: str, latex: str) -> None:
    for op in ["*", "@"]:
        tree = ast_utils.parse_expr(f"{left} {op} {right}")
        assert isinstance(tree, ast.BinOp)
        assert (
            expression_codegen.ExpressionCodegen(use_math_symbols=True).visit(tree)
            == latex
        )
