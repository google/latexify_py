"""Utilities to generate AST nodes."""

from __future__ import annotations

import ast
import sys
from typing import Any


def parse_expr(code: str) -> ast.expr:
    """Parses given Python expression.

    Args:
        code: Python expression to parse.

    Returns:
        ast.expr corresponding to `code`.
    """
    return ast.parse(code, mode="eval").body


def make_name(id: str) -> ast.Name:
    """Generates a new Name node.

    Args:
        id: Name of the node.

    Returns:
        Generated ast.Name.
    """
    return ast.Name(id=id, ctx=ast.Load())


def make_attribute(value: ast.expr, attr: str):
    """Generates a new Attribute node.

    Args:
        value: Parent value.
        attr: Attribute name.

    Returns:
        Generated ast.Attribute.
    """
    return ast.Attribute(value=value, attr=attr, ctx=ast.Load())


def make_constant(value: Any) -> ast.expr:
    """Generates a new Constant node.

    Args:
        value: Value of the node.

    Returns:
        Generated ast.Constant or its equivalent.

    Raises:
        ValueError: Unsupported value type.
    """
    if (
        value is None
        or value is ...
        or isinstance(value, (bool, int, float, complex, str, bytes))
    ):
        return ast.Constant(value=value)

    raise ValueError(f"Unsupported type to generate Constant: {type(value).__name__}")


def is_constant(node: ast.AST) -> bool:
    """Checks if the node is a constant.

    Args:
        node: The node to examine.

    Returns:
        True if the node is a constant, False otherwise.
    """
    return isinstance(node, ast.Constant)


def is_str(node: ast.AST) -> bool:
    """Checks if the node is a str constant.

    Args:
        node: The node to examine.

    Returns:
        True if the node is a str constant, False otherwise.
    """
    if sys.version_info.minor < 8 and isinstance(node, ast.Str):
        return True

    return isinstance(node, ast.Constant) and isinstance(node.value, str)


def extract_int_or_none(node: ast.expr) -> int | None:
    """Extracts int constant from the given Constant node.

    Args:
        node: ast.Constant or its equivalent representing an int value.

    Returns:
        Extracted int value, or None if extraction failed.
    """
    if (
        isinstance(node, ast.Constant)
        and isinstance(node.value, int)
        and not isinstance(node.value, bool)
    ):
        return node.value

    return None


def extract_int(node: ast.expr) -> int:
    """Extracts int constant from the given Constant node.

    Args:
        node: ast.Constant or its equivalent representing an int value.

    Returns:
        Extracted int value.

    Raises:
        ValueError: Not a subtree containing an int value.
    """
    value = extract_int_or_none(node)

    if value is None:
        raise ValueError(f"Unsupported node to extract int: {type(node).__name__}")

    return value


def extract_function_name_or_none(node: ast.Call) -> str | None:
    """Extracts function name from the given Call node.

    Args:
        node: ast.Call.

    Returns:
        Extracted function name, or None if not found.
    """
    if isinstance(node.func, ast.Name):
        return node.func.id
    if isinstance(node.func, ast.Attribute):
        return node.func.attr

    return None


def ast_function_def(*args, **kwargs) -> ast.FunctionDef:
    if sys.version_info.minor < 12:
        kwargs.pop("type_params", None)
    return ast.FunctionDef(*args, **kwargs)
