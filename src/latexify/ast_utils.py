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


def create_function_def(
    name,
    args,
    body,
    decorator_list,
    returns=None,
    type_comment=None,
    type_params=None,
    lineno=None,
    col_offset=None,
    end_lineno=None,
    end_col_offset=None,
) -> ast.FunctionDef:
    """Creates a FunctionDef node.

    This function generates an `ast.FunctionDef` node, optionally removing
    the `type_params` keyword argument for Python versions below 3.12.

    Args:
        name: Name of the function.
        args: Arguments of the function.
        body: Body of the function.
        decorator_list: List of decorators.
        returns: Return type of the function.
        type_comment: Type comment of the function.
        type_params: Type parameters of the function.
        lineno: Line number of the function definition.
        col_offset: Column offset of the function definition.
        end_lineno: End line number of the function definition.
        end_col_offset: End column offset of the function definition.

    Returns:
        ast.FunctionDef: The generated FunctionDef node.
    """
    if sys.version_info.minor < 12:
        return ast.FunctionDef(
            name=name,
            args=args,
            body=body,
            decorator_list=decorator_list,
            returns=returns,
            type_comment=type_comment,
            lineno=lineno,
            col_offset=col_offset,
            end_lineno=end_lineno,
            end_col_offset=end_col_offset,
        )  # type: ignore
    return ast.FunctionDef(
        name=name,
        args=args,
        body=body,
        decorator_list=decorator_list,
        returns=returns,
        type_comment=type_comment,
        type_params=type_params,
        lineno=lineno,
        col_offset=col_offset,
        end_lineno=end_lineno,
        end_col_offset=end_col_offset,
    )  # type: ignore
