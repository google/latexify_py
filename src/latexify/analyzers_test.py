"""Tests for latexify.analyzers."""

from __future__ import annotations

import ast

import pytest

from latexify import analyzers, ast_utils, exceptions, test_utils


@test_utils.require_at_least(8)
@pytest.mark.parametrize(
    "code,start,stop,step,start_int,stop_int,step_int",
    [
        (
            "range(x)",
            ast.Constant(value=0),
            ast.Name(id="x", ctx=ast.Load()),
            ast.Constant(value=1),
            0,
            None,
            1,
        ),
        (
            "range(123)",
            ast.Constant(value=0),
            ast.Constant(value=123),
            ast.Constant(value=1),
            0,
            123,
            1,
        ),
        (
            "range(x, y)",
            ast.Name(id="x", ctx=ast.Load()),
            ast.Name(id="y", ctx=ast.Load()),
            ast.Constant(value=1),
            None,
            None,
            1,
        ),
        (
            "range(123, y)",
            ast.Constant(value=123),
            ast.Name(id="y", ctx=ast.Load()),
            ast.Constant(value=1),
            123,
            None,
            1,
        ),
        (
            "range(x, 123)",
            ast.Name(id="x", ctx=ast.Load()),
            ast.Constant(value=123),
            ast.Constant(value=1),
            None,
            123,
            1,
        ),
        (
            "range(x, y, z)",
            ast.Name(id="x", ctx=ast.Load()),
            ast.Name(id="y", ctx=ast.Load()),
            ast.Name(id="z", ctx=ast.Load()),
            None,
            None,
            None,
        ),
        (
            "range(123, y, z)",
            ast.Constant(value=123),
            ast.Name(id="y", ctx=ast.Load()),
            ast.Name(id="z", ctx=ast.Load()),
            123,
            None,
            None,
        ),
        (
            "range(x, 123, z)",
            ast.Name(id="x", ctx=ast.Load()),
            ast.Constant(value=123),
            ast.Name(id="z", ctx=ast.Load()),
            None,
            123,
            None,
        ),
        (
            "range(x, y, 123)",
            ast.Name(id="x", ctx=ast.Load()),
            ast.Name(id="y", ctx=ast.Load()),
            ast.Constant(value=123),
            None,
            None,
            123,
        ),
    ],
)
def test_analyze_range(
    code: str,
    start: ast.expr,
    stop: ast.expr,
    step: ast.expr,
    start_int: int | None,
    stop_int: int | None,
    step_int: int | None,
) -> None:
    node = ast_utils.parse_expr(code)
    assert isinstance(node, ast.Call)

    info = analyzers.analyze_range(node)

    test_utils.assert_ast_equal(observed=info.start, expected=start)
    test_utils.assert_ast_equal(observed=info.stop, expected=stop)
    if step is not None:
        test_utils.assert_ast_equal(observed=info.step, expected=step)
    else:
        assert info.step is None

    def check_int(observed: int | None, expected: int | None) -> None:
        if expected is not None:
            assert observed == expected
        else:
            assert observed is None

    check_int(observed=info.start_int, expected=start_int)
    check_int(observed=info.stop_int, expected=stop_int)
    check_int(observed=info.step_int, expected=step_int)


@pytest.mark.parametrize(
    "code",
    [
        # Not a direct call
        "__builtins__.range(x)",
        'getattr(__builtins__, "range")(x)',
        # Unsupported functions
        "f(x)",
        "iter(range(x))",
        # Range with invalid arguments
        "range()",
        "range(x, y, z, w)",
    ],
)
def test_analyze_range_invalid(code: str) -> None:
    node = ast_utils.parse_expr(code)
    assert isinstance(node, ast.Call)

    with pytest.raises(
        exceptions.LatexifySyntaxError, match=r"^Unsupported AST for analyze_range\.$"
    ):
        analyzers.analyze_range(node)


@pytest.mark.parametrize(
    "before,after",
    [
        ("n + 1", "n"),
        ("n + 2", "n + 1"),
        ("n - (-1)", "n - (-1) - 1"),
        ("n - 1", "n - 2"),
        ("1 * 2", "1 * 2 - 1"),
    ],
)
def test_reduce_stop_parameter(before: str, after: str) -> None:
    test_utils.assert_ast_equal(
        analyzers.reduce_stop_parameter(ast_utils.parse_expr(before)),
        ast_utils.parse_expr(after),
    )
