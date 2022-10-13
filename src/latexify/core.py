# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# This is very scratchy and supports only limited portion of Python functions.
"""Latexify core module."""

import ast
import inspect
import textwrap

import dill

from latexify import constants
from latexify import node_visitor_base


class LatexifyVisitor(node_visitor_base.NodeVisitorBase):
    """Latexify AST visitor."""

    # Default config
    equality_sign = r"\triangleq"

    def __init__(self, math_symbol=False, raw_func_name=False):
        self.math_symbol = math_symbol
        self.raw_func_name = (
            raw_func_name  # True:do not treat underline as label of subscript(#31)
        )
        self.assign_var = {}
        super().__init__()

    def _parse_math_symbols(self, val: str) -> str:
        if not self.math_symbol:
            return val
        if val in constants.MATH_SYMBOLS:
            return rf"{{\{val}}}"
        return val

    def generic_visit(self, node, action):
        del action

        return str(node)

    def visit_Module(self, node, action):  # pylint: disable=invalid-name
        del action

        return self.visit(node.body[0])

    def visit_FunctionDef(self, node, action):  # pylint: disable=invalid-name
        del action

        name_str = rf"\mathrm{{{node.name}}}"
        if self.raw_func_name:
            name_str = name_str.replace(r"_", r"\_")  # fix #31
        arg_strs = [self._parse_math_symbols(str(arg.arg)) for arg in node.args.args]

        body_str = ''
        for el in node.body:
            # el: ast.Assign | ast.Return
            body_str = self.visit(el)
            if isinstance(el, ast.Return):
                break
        if body_str == '':
            raise ValueError('Error `return` missing.')

        return f"{name_str}({', '.join(arg_strs)}) {self.equality_sign} {body_str}"

    def visit_Assign(self, node, action):
        del action

        self.assign_var[node.targets[0].id] = self.visit(node.value)

    def visit_Return(self, node, action):  # pylint: disable=invalid-name
        del action

        return self.visit(node.value)

    def visit_Tuple(self, node, action):  # pylint: disable=invalid-name
        del action

        elts = [self.visit(i) for i in node.elts]
        return r"\left( " + r"\space,\space ".join(elts) + r"\right) "

    def visit_List(self, node, action):  # pylint: disable=invalid-name
        del action

        elts = [self.visit(i) for i in node.elts]
        return r"\left[ " + r"\space,\space ".join(elts) + r"\right] "

    def visit_Set(self, node, action):  # pylint: disable=invalid-name
        del action

        elts = [self.visit(i) for i in node.elts]
        return r"\left\{ " + r"\space,\space ".join(elts) + r"\right\} "

    def visit_Call(self, node, action):  # pylint: disable=invalid-name
        """Visit a call node."""

        def _decorated_lstr_and_arg(node, callee_str, lstr):
            """Decorates lstr and get its associated arguments"""
            if callee_str == "sum" and isinstance(node.args[0], ast.GeneratorExp):
                generator_info = self.visit(node.args[0], constants.actions.SET_BOUNDS)
                arg_str, comprehension = generator_info
                var_comp, args_comp = comprehension
                if len(args_comp) == 1:
                    arg1, arg2 = "0", args_comp[0]
                else:
                    arg1, arg2 = args_comp
                # the second arg in range func is exclusive
                try:
                    arg2 = str(int(arg2) - 1)
                except ValueError:
                    arg2 += "-1"

                decorator = rf"_{{{var_comp}={arg1}}}^{{{arg2}}}"
                lstr = rf"\sum{decorator} \left({{"

            else:
                arg_strs = [self.visit(arg) for arg in node.args]
                arg_str = ", ".join(arg_strs)

            return lstr, arg_str

        del action

        callee_str = self.visit(node.func)

        for prefix in constants.PREFIXES:
            if callee_str.startswith(f"{prefix}."):
                callee_str = callee_str[len(prefix) + 1:]
                break

        lstr, rstr = constants.BUILTIN_CALLEES.get(callee_str, (None, None))
        if lstr is None:
            lstr = rf"\mathrm{{{callee_str}}}\left("
            rstr = r"\right)"

        lstr, arg_str = _decorated_lstr_and_arg(node, callee_str, lstr)
        return lstr + arg_str + rstr

    def visit_Attribute(self, node, action):  # pylint: disable=invalid-name
        del action

        return f"{self.visit(node.value)}.{node.attr}"

    def visit_Name(self, node, action):  # pylint: disable=invalid-name
        del action
        if node.id in self.assign_var.keys():
            return self.assign_var[node.id]

        return self._parse_math_symbols(str(node.id))

    def visit_Constant(self, node, action):  # pylint: disable=invalid-name
        del action

        # for python >= 3.8
        return str(node.n)

    def visit_Num(self, node, action):  # pylint: disable=invalid-name
        del action

        # for python < 3.8
        return str(node.n)

    def visit_UnaryOp(self, node, action):  # pylint: disable=invalid-name
        """Visit a unary op node."""
        del action

        def _wrap(child):
            latex = self.visit(child)
            if isinstance(child, ast.BinOp) and isinstance(
                child.op, (ast.Add, ast.Sub)
            ):
                return rf"\left({latex}\right)"
            return latex

        reprs = {
            ast.UAdd: (lambda: _wrap(node.operand)),
            ast.USub: (lambda: "-" + _wrap(node.operand)),
            ast.Not: (lambda: r"\lnot\left(" + _wrap(node.operand) + r"\right)"),
        }

        if type(node.op) in reprs:
            return reprs[type(node.op)]()
        return rf"\mathrm{{unknown\_uniop}}({self.visit(node.operand)})"

    def visit_BinOp(self, node, action):  # pylint: disable=invalid-name
        """Visit a binary op node."""
        del action

        priority = constants.BIN_OP_PRIORITY

        def _unwrap(child):
            return self.visit(child)

        def _wrap(child):
            latex = _unwrap(child)
            if isinstance(child, ast.BinOp):
                cp = priority[type(child.op)] if type(child.op) in priority else 100
                pp = priority[type(node.op)] if type(node.op) in priority else 100
                if cp < pp:
                    return f"({latex})"
            return latex

        lhs = node.left
        rhs = node.right
        reprs = {
            ast.Add: (lambda: _wrap(lhs) + " + " + _wrap(rhs)),
            ast.Sub: (lambda: _wrap(lhs) + " - " + _wrap(rhs)),
            ast.Mult: (lambda: _wrap(lhs) + _wrap(rhs)),
            ast.MatMult: (lambda: _wrap(lhs) + _wrap(rhs)),
            ast.Div: (lambda: r"\frac{" + _unwrap(lhs) + "}{" + _unwrap(rhs) + "}"),
            ast.FloorDiv: (
                lambda: r"\left\lfloor\frac{"
                + _unwrap(lhs)
                + "}{"
                + _unwrap(rhs)
                + r"}\right\rfloor"
            ),
            ast.Mod: (lambda: _wrap(lhs) + r" \bmod " + _wrap(rhs)),
            ast.Pow: (lambda: _wrap(lhs) + "^{" + _unwrap(rhs) + "}"),
        }

        if type(node.op) in reprs:
            return reprs[type(node.op)]()
        return r"\mathrm{unknown\_binop}(" + _unwrap(lhs) + ", " + _unwrap(rhs) + ")"

    def visit_Compare(self, node, action):  # pylint: disable=invalid-name
        """Visit a compare node."""
        del action

        lstr = self.visit(node.left)
        rstr = self.visit(node.comparators[0])

        if isinstance(node.ops[0], ast.Eq):
            return lstr + "=" + rstr
        if isinstance(node.ops[0], ast.Gt):
            return lstr + ">" + rstr
        if isinstance(node.ops[0], ast.Lt):
            return lstr + "<" + rstr
        if isinstance(node.ops[0], ast.GtE):
            return lstr + r"\ge " + rstr
        if isinstance(node.ops[0], ast.LtE):
            return lstr + r"\le " + rstr
        if isinstance(node.ops[0], ast.NotEq):
            return lstr + r"\ne " + rstr
        if isinstance(node.ops[0], ast.Is):
            return lstr + r"\equiv" + rstr

        return r"\mathrm{unknown\_comparator}(" + lstr + ", " + rstr + ")"

    def visit_BoolOp(self, node, action):  # pylint: disable=invalid-name
        del action

        logic_operator = (
            r"\lor "
            if isinstance(node.op, ast.Or)
            else r"\land "
            if isinstance(node.op, ast.And)
            else r" \mathrm{unknown\_operator} "
        )
        # visit all the elements in the ast.If node recursively
        return (
            r"\left("
            + self.visit(node.values[0])
            + r"\right)"
            + logic_operator
            + r"\left("
            + self.visit(node.values[1])
            + r"\right)"
        )

    def visit_If(self, node, action):  # pylint: disable=invalid-name
        """Visit an if node."""
        del action

        latex = r"\left\{ \begin{array}{ll} "

        while isinstance(node, ast.If):
            cond_latex = self.visit(node.test)
            true_latex = self.visit(node.body[0])
            latex += rf"{true_latex}, & \mathrm{{if}} \ {cond_latex} \\ "
            node = node.orelse[0]

        latex += self.visit(node)
        return rf"{latex}, & \mathrm{{otherwise}} \end{{array}} \right."

    def visit_GeneratorExp_set_bounds(self, node):  # pylint: disable=invalid-name
        action = constants.actions.SET_BOUNDS
        output = self.visit(node.elt)
        comprehensions = [
            self.visit(generator, action) for generator in node.generators
        ]
        if len(comprehensions) == 1:
            return output, comprehensions[0]
        raise TypeError(
            f"visit_GeneratorExp_sum() supports a single for clause"
            f"but {len(comprehensions)} were given"
        )

    def visit_comprehension_set_bounds(self, node):  # pylint: disable=invalid-name
        """Visit a comprehension node, which represents a for clause"""
        var = self.visit(node.target)
        if isinstance(node.iter, ast.Call):
            callee_str = self.visit(node.iter.func)
        if callee_str == "range":
            args = [self.visit(arg) for arg in node.iter.args]
            if len(args) in (1, 2):
                return var, args
        raise TypeError(
            "Comprehension for sum only supports range func " "with 1 or 2 args"
        )


def get_latex(fn, *args, **kwargs):
    try:
        source = inspect.getsource(fn)
    # pylint: disable=broad-except
    except Exception:
        # Maybe running on console.
        source = dill.source.getsource(fn)

    source = textwrap.dedent(source)

    return LatexifyVisitor(*args, **kwargs).visit(ast.parse(source))


def with_latex(*args, **kwargs):
    """Translate a function with latex representation."""

    class _LatexifiedFunction:
        """Function with latex representation."""

        def __init__(self, fn):
            self._fn = fn
            self._str = get_latex(fn, *args, **kwargs)

        @property
        def __doc__(self):
            return self._fn.__doc__

        @__doc__.setter
        def __doc__(self, val):
            self._fn.__doc__ = val

        @property
        def __name__(self):
            return self._fn.__name__

        @__name__.setter
        def __name__(self, val):
            self._fn.__name__ = val

        def __call__(self, *args):
            return self._fn(*args)

        def __str__(self):
            return self._str

        def _repr_latex_(self):
            """
            Hooks into Jupyter notebook's display system.
            """
            return rf"$$ \displaystyle {self._str} $$"

    if len(args) == 1 and callable(args[0]):
        return _LatexifiedFunction(args[0])

    def ret(fn):
        return _LatexifiedFunction(fn)

    return ret


def set_config(**kwargs):
    """
    Parameters :
    * `equality_sign`
    """
    for key, value in kwargs.items():
        setattr(LatexifyVisitor, key, value)
