"""Tests for FunctionCodegen with match statements."""

from __future__ import annotations

import ast
import textwrap

import pytest

from latexify import exceptions, test_utils
from latexify.codegen import function_codegen


@test_utils.require_at_least(10)
def test_visit_functiondef_match() -> None:
    tree = ast.parse(
        textwrap.dedent(
            """
            def f(x):
                match x:
                    case 0:
                        return 1
                    case _:
                        return 3 * x
            """
        )
    )
    expected = (
        r"f(x) ="
        r" \left\{ \begin{array}{ll}"
        r"1, & \mathrm{if} \ x = 0 \\"
        r" 3 x, & \mathrm{otherwise}"
        r" \end{array} \right."
    )
    assert function_codegen.FunctionCodegen().visit(tree) == expected


@test_utils.require_at_least(10)
def test_visit_match() -> None:
    tree = ast.parse(
        textwrap.dedent(
            """
            match x:
                case 0:
                    return 1
                case _:
                    return 2
            """
        )
    ).body[0]
    expected = (
        r"\left\{ \begin{array}{ll}"
        r"1, & \mathrm{if} \ x = 0 \\"
        r" 2, & \mathrm{otherwise}"
        r" \end{array} \right."
    )
    assert function_codegen.FunctionCodegen().visit(tree) == expected


@test_utils.require_at_least(10)
def test_visit_multiple_match_cases() -> None:
    tree = ast.parse(
        textwrap.dedent(
            """
            match x:
                case 0:
                    return 1
                case 1:
                    return 2
                case _:
                    return 3
            """
        )
    ).body[0]
    expected = (
        r"\left\{ \begin{array}{ll}"
        r"1, & \mathrm{if} \ x = 0 \\"
        r" 2, & \mathrm{if} \ x = 1 \\"
        r" 3, & \mathrm{otherwise}"
        r" \end{array} \right."
    )
    assert function_codegen.FunctionCodegen().visit(tree) == expected


@test_utils.require_at_least(10)
def test_visit_single_match_case_no_wildcards() -> None:
    tree = ast.parse(
        textwrap.dedent(
            """
            match x:
                case 0:
                    return 1
            """
        )
    ).body[0]

    with pytest.raises(
        exceptions.LatexifySyntaxError,
        match=r"^Match statement must contain the wildcard\.$",
    ):
        function_codegen.FunctionCodegen().visit(tree)


@test_utils.require_at_least(10)
def test_visit_multiple_match_cases_no_wildcards() -> None:
    tree = ast.parse(
        textwrap.dedent(
            """
            match x:
                case 0:
                    return 1
                case 1:
                    return 2
            """
        )
    ).body[0]

    with pytest.raises(
        exceptions.LatexifySyntaxError,
        match=r"^Match statement must contain the wildcard\.$",
    ):
        function_codegen.FunctionCodegen().visit(tree)


@test_utils.require_at_least(10)
def test_visit_only_wildcard_in_matchas() -> None:
    tree = ast.parse(
        textwrap.dedent(
            """
            match x:
                case [x] as y:
                    return 1
                case _:
                    return 2
            """
        )
    ).body[0]

    with pytest.raises(
        exceptions.LatexifySyntaxError,
        match=r"^Nonempty as-patterns are not supported in MatchAs nodes.$",
    ):
        function_codegen.FunctionCodegen().visit(tree)


@test_utils.require_at_least(10)
def test_visit_match_case_no_return() -> None:
    tree = ast.parse(
        textwrap.dedent(
            """
            match x:
                case 0:
                    x = 5
                case _:
                    return 0
            """
        )
    ).body[0]

    with pytest.raises(
        exceptions.LatexifyNotSupportedError,
        match=r"^Match cases must contain exactly 1 return statement\.$",
    ):
        function_codegen.FunctionCodegen().visit(tree)


@test_utils.require_at_least(10)
def test_visit_match_case_mutliple_statements() -> None:
    tree = ast.parse(
        textwrap.dedent(
            """
            match x:
                case 0:
                    x = 5
                    return 1
                case _:
                    return 0
            """
        )
    ).body[0]

    with pytest.raises(
        exceptions.LatexifyNotSupportedError,
        match=r"^Match cases must contain exactly 1 return statement\.$",
    ):
        function_codegen.FunctionCodegen().visit(tree)


@test_utils.require_at_least(10)
def test_visit_match_case_with_if() -> None:
    tree = ast.parse(
        textwrap.dedent(
            """
            match x:
                case x if x > 0:
                    return 1
                case _:
                    return 2
            """
        )
    ).body[0]

    assert (
        function_codegen.FunctionCodegen().visit(tree)
        == r"\left\{ \begin{array}{ll}"
        + r"1, & \mathrm{if} \ x > 0 \\ "
        + r"2, & \mathrm{otherwise} \end{array} \right."
    )


@test_utils.require_at_least(10)
def test_visit_match_case_with_if_and() -> None:
    tree = ast.parse(
        textwrap.dedent(
            """
            match x:
                case x if x > 0 and x <= 10:
                    return 1
                case _:
                    return 2
            """
        )
    ).body[0]

    assert (
        function_codegen.FunctionCodegen().visit(tree)
        == r"\left\{ \begin{array}{ll}1, & \mathrm{if} "
        + r"\ x > 0 \land x \le 10 \\"
        + r" 2, & \mathrm{otherwise} \end{array} \right."
    )


@test_utils.require_at_least(10)
def test_visit_matchcase_with_if_or() -> None:
    tree = ast.parse(
        textwrap.dedent(
            """
            match x:
                case x if x>0 or x<=10:
                    return 1
                case _:
                    return 2
            """
        )
    ).body[0]

    assert (
        function_codegen.FunctionCodegen().visit(tree)
        == r"\left\{ \begin{array}{ll}1,"
        + r" & \mathrm{if} \ x > 0 \lor x \le 10 \\"
        + r" 2, & \mathrm{otherwise} \end{array} \right."
    )


@test_utils.require_at_least(10)
def test_visit_match_case_with_combined_condition() -> None:
    tree = ast.parse(
        textwrap.dedent(
            """
            match x:
                case x if 0 < x <= 10:
                    return 1
                case _:
                    return 2
            """
        )
    ).body[0]

    assert (
        function_codegen.FunctionCodegen().visit(tree)
        == r"\left\{ \begin{array}{ll}1,"
        + r" & \mathrm{if} \ 0 < x \le 10 \\ 2,"
        + r" & \mathrm{otherwise} \end{array} \right."
    )


@test_utils.require_at_least(10)
def test_visit_match_case_or() -> None:
    tree = ast.parse(
        textwrap.dedent(
            """
            match x:
                case 0 | 1:
                    return 1
                case _:
                    return 2
            """
        )
    ).body[0]

    assert (
        function_codegen.FunctionCodegen().visit(tree)
        == r"\left\{ \begin{array}{ll}1, & \mathrm{if} \ x = 0 \lor x = 1 \\"
        + r" 2, & \mathrm{otherwise} \end{array} \right."
    )
