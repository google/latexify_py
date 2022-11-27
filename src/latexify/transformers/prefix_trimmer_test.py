import ast
from latexify import test_utils
from latexify.transformers.prefix_trimmer import PrefixTrimmer


def test_not_trimmed():
    prefix = ast.Attribute(
        value=ast.Name(id="math", ctx=ast.Load()), attr="sin", ctx=ast.Load()
    )
    trimmed_prefix = PrefixTrimmer(set()).visit_Attribute(prefix)

    test_utils.assert_ast_equal(
        trimmed_prefix,
        ast.Attribute(
            value=ast.Name(id="math", ctx=ast.Load()), attr="sin", ctx=ast.Load()
        ),
    )


def test_trim_basic_prefix():
    prefix = ast.Attribute(
        value=ast.Name(id="math", ctx=ast.Load()), attr="sin", ctx=ast.Load()
    )
    trimmed_prefix = PrefixTrimmer({"math"}).visit_Attribute(prefix)

    test_utils.assert_ast_equal(trimmed_prefix, ast.Name(id="sin", ctx=ast.Load()))


def test_trim_complex_prefix():
    prefix = ast.Attribute(
        value=ast.Attribute(
            value=ast.Name(id="multiple", ctx=ast.Load()),
            attr="prefixes",
            ctx=ast.Load(),
        ),
        attr="sin",
        ctx=ast.Load(),
    )
    trimmed_prefix = PrefixTrimmer({"multiple"}).visit_Attribute(prefix)

    test_utils.assert_ast_equal(
        trimmed_prefix,
        ast.Attribute(
            value=ast.Name(id="prefixes", ctx=ast.Load()),
            attr="sin",
            ctx=ast.Load(),
        ),
    )
