"""Utilities to generate AST nodes."""

from __future__ import annotations

import ast
import sys
from typing import Any


def make_constant(value: Any) -> ast.expr:
    """Generates a new Constant node.

    Args:
        value: Value of the node.

    Returns:
        Generated ast.Constant or its equivalent.

    Raises:
        ValueError: Unsupported value type.
    """
    if sys.version_info.minor < 8:
        if value is None or value is False or value is True:
            return ast.NameConstant(value=value)
        if value is ...:
            return ast.Ellipsis()
        if isinstance(value, (int, float, complex)):
            return ast.Num(n=value)
        if isinstance(value, str):
            return ast.Str(s=value)
        if isinstance(value, bytes):
            return ast.Bytes(s=value)
    else:
        if (
            value is None
            or value is ...
            or isinstance(value, (bool, int, float, complex, str, bytes))
        ):
            return ast.Constant(value=value)

    raise ValueError(f"Unsupported type to generate Constant: {type(value).__name__}")


def extract_int_or_none(node: ast.expr) -> int | None:
    """Extracts int constant from the given Constant node.

    Args:
        node: ast.Constant or its equivalent representing an int value.

    Returns:
        Extracted int value, or None if extraction failed.
    """
    if sys.version_info.minor < 8:
        if (
            isinstance(node, ast.Num)
            and isinstance(node.n, int)
            and not isinstance(node.n, bool)
        ):
            return node.n
    else:
        if (
            isinstance(node, ast.Constant)
            and isinstance(node.value, int)
            and not isinstance(node.n, bool)
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
