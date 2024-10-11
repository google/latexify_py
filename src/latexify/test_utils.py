"""Test utilities."""

from __future__ import annotations

import ast
import functools
import sys
from collections.abc import Callable
from typing import cast


def require_at_least(
    minor: int,
) -> Callable[[Callable[..., None]], Callable[..., None]]:
    """Require the minimum minor version of Python 3 to run the test.

    Args:
        minor: Minimum minor version (inclusive) that the test case supports.

    Returns:
        A decorator function to wrap the test case function.
    """

    def decorator(fn: Callable[..., None]) -> Callable[..., None]:
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            if sys.version_info.minor < minor:
                return
            fn(*args, **kwargs)

        return wrapper

    return decorator


def require_at_most(
    minor: int,
) -> Callable[[Callable[..., None]], Callable[..., None]]:
    """Require the maximum minor version of Python 3 to run the test.

    Args:
        minor: Maximum minor version (inclusive) that the test case supports.

    Returns:
        A decorator function to wrap the test case function.
    """

    def decorator(fn: Callable[..., None]) -> Callable[..., None]:
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            if sys.version_info.minor > minor:
                return
            fn(*args, **kwargs)

        return wrapper

    return decorator


def ast_equal(observed: ast.AST, expected: ast.AST) -> bool:
    """Checks the equality between two ASTs.

    This function checks if `observed` contains at least the same subtree with
    `expected`. If `observed` has some extra branches that `expected` does not cover,
    it is ignored.

    Args:
        observed: An AST to check.
        expected: The expected AST.

    Returns:
        True if observed and expected represent the same AST, False otherwise.
    """
    ignore_keys = {"lineno", "col_offset", "end_lineno", "end_col_offset", "kind"}
    if sys.version_info.minor <= 12:
        ignore_keys.add("type_params")

    try:
        assert type(observed) is type(expected)

        for k, ve in vars(expected).items():
            if k in ignore_keys:
                continue

            vo = getattr(observed, k)  # May cause AttributeError.

            if isinstance(ve, ast.AST):
                assert ast_equal(cast(ast.AST, vo), ve)
            elif isinstance(ve, list):
                vo = cast(list, vo)
                assert len(vo) == len(ve)
                assert all(
                    ast_equal(cast(ast.AST, co), cast(ast.AST, ce))
                    for co, ce in zip(vo, ve)
                )
            else:
                assert type(vo) is type(ve)
                assert vo == ve

    except (AssertionError, AttributeError):
        raise  # raise to debug easier.

    return True


def assert_ast_equal(observed: ast.AST, expected: ast.AST) -> None:
    """Asserts the equality between two ASTs.

    Args:
        observed: An AST to compare.
        expected: Another AST.

    Raises:
        AssertionError: observed and expected represent different ASTs.
    """
    indent = 4 if sys.version_info.minor >= 9 else None
    assert ast_equal(
        observed, expected
    ), f"AST does not match. observed = {observed}\nexpected = {expected}"
