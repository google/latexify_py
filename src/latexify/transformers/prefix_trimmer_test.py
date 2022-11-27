"""Tests for latexify.transformers.prefix_trimmer."""

from __future__ import annotations

import ast

import pytest

from latexify import ast_utils, test_utils
from latexify.transformers import prefix_trimmer

# For convenience
make_name = ast_utils.make_name
make_attr = ast_utils.make_attribute
PrefixTrimmer = prefix_trimmer.PrefixTrimmer


@pytest.mark.parametrize(
    "prefix", [".x", "x.", "1", "1x", "x.1", "x.1x", "x.x.1", "x.x.1x" "x..x", "x.x..x"]
)
def test_invalid_prefix(prefix: str) -> None:
    with pytest.raises(ValueError, match=rf"^Invalid prefix: {prefix}$"):
        PrefixTrimmer({prefix})


@pytest.mark.parametrize(
    "prefixes,expected",
    [
        (set(), make_name("foo")),
        ({"foo"}, make_name("foo")),
        ({"bar"}, make_name("foo")),
        ({"foo.bar"}, make_name("foo")),
        ({"foo", "bar"}, make_name("foo")),
        ({"foo", "foo.bar"}, make_name("foo")),
    ],
)
def test_name(prefixes: set[str], expected: ast.expr) -> None:
    source = make_name("foo")
    transformed = PrefixTrimmer(prefixes).visit(source)
    test_utils.assert_ast_equal(transformed, expected)


@pytest.mark.parametrize(
    "prefixes,expected",
    [
        (set(), make_attr(make_name("foo"), "bar")),
        ({"fo"}, make_attr(make_name("foo"), "bar")),
        ({"foo"}, make_name("bar")),
        ({"bar"}, make_attr(make_name("foo"), "bar")),
        ({"baz"}, make_attr(make_name("foo"), "bar")),
        ({"foo.bar"}, make_attr(make_name("foo"), "bar")),
        ({"foo", "bar"}, make_name("bar")),
        ({"foo", "foo.bar"}, make_name("bar")),
    ],
)
def test_attr_1(prefixes: set[str], expected: ast.expr) -> None:
    source = make_attr(make_name("foo"), "bar")
    transformed = PrefixTrimmer(prefixes).visit(source)
    test_utils.assert_ast_equal(transformed, expected)


@pytest.mark.parametrize(
    "prefixes,expected",
    [
        (set(), make_attr(make_attr(make_name("foo"), "bar"), "baz")),
        ({"fo"}, make_attr(make_attr(make_name("foo"), "bar"), "baz")),
        ({"foo"}, make_attr(make_name("bar"), "baz")),
        ({"bar"}, make_attr(make_attr(make_name("foo"), "bar"), "baz")),
        ({"baz"}, make_attr(make_attr(make_name("foo"), "bar"), "baz")),
        ({"foo.ba"}, make_attr(make_attr(make_name("foo"), "bar"), "baz")),
        ({"foo.bar"}, make_name("baz")),
        ({"foo.bar.baz"}, make_attr(make_attr(make_name("foo"), "bar"), "baz")),
        ({"foo", "bar"}, make_attr(make_name("bar"), "baz")),
        ({"foo", "foo.bar"}, make_name("baz")),
    ],
)
def test_attr_2(prefixes: set[str], expected: ast.expr) -> None:
    source = make_attr(make_attr(make_name("foo"), "bar"), "baz")
    transformed = PrefixTrimmer(prefixes).visit(source)
    test_utils.assert_ast_equal(transformed, expected)
