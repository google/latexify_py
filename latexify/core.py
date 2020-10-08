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

import dill

from latexify import constants

class LatexifyVisitor(ast.NodeVisitor):
  """Latexify AST visitor."""

  def __init__(self, math_symbol):
    self.math_symbol = math_symbol
    super().__init__()

  def _parse_math_symbols(self, val: str) -> str:
    if not self.math_symbol:
      return val
    if val in constants.MATH_SYMBOLS:
      return '{\\' + val + '}'
    return val

  def generic_visit(self, node):
    return str(node)

  def visit_Module(self, node):  # pylint: disable=invalid-name
    return self.visit(node.body[0])

  def visit_FunctionDef(self, node):  # pylint: disable=invalid-name
    name_str = r'\mathrm{' + str(node.name) + '}'
    arg_strs = [
        self._parse_math_symbols(str(arg.arg)) for arg in node.args.args]
    body_str = self.visit(node.body[0])
    return name_str + '(' + ', '.join(arg_strs) + r') \triangleq ' + body_str

  def visit_Return(self, node):  # pylint: disable=invalid-name
    return self.visit(node.value)

  def visit_Tuple(self, node):  # pylint: disable=invalid-name
    elts = [self.visit(i) for i in node.elts]
    return r'\left( ' + r'\space,\space '.join(elts) + r'\right) '

  def visit_List(self, node):  # pylint: disable=invalid-name
    elts = [self.visit(i) for i in node.elts]
    return r'\left[ ' + r'\space,\space '.join(elts) + r'\right] '

  def visit_Set(self, node):  # pylint: disable=invalid-name
    elts = [self.visit(i) for i in node.elts]
    return r'\left\{ ' + r'\space,\space '.join(elts) + r'\right\} '

  def visit_Call(self, node):  # pylint: disable=invalid-name
    """Visit a call node."""
    callee_str = self.visit(node.func)
    lstr, rstr = constants.BUILTIN_CALLEES.get(callee_str, (None, None))
    if lstr is None:
      if callee_str.startswith('math.'):
        callee_str = callee_str[5:]
      lstr = r'\mathrm{' + callee_str + r'}\left('
      rstr = r'\right)'

    arg_strs = [self.visit(arg) for arg in node.args]

    if callee_str == 'sum' and isinstance(node.args[0], ast.GeneratorExp):
      limit_str, formula_str = self.visit(node.args[0])
      lstr =  r'\sum' + limit_str + r' \left({'
      return lstr + formula_str + rstr
    if callee_str == 'range':
      return arg_strs

    return lstr + ', '.join(arg_strs) + rstr

  def visit_GeneratorExp(self, node):  # pylint: disable=invalid-name
    limit_str = self.visit(node.generators[0])
    formula_str = self.visit(node.elt)
    return limit_str, formula_str

  def visit_comprehension(self, node):  # pylint: disable=invalid-name
    var = self.visit(node.target)
    limits = self.visit(node.iter)
    try:
      if isinstance(limits, list):
        if len(limits) == 1:
          lower_limit, upper_limit = '0', limits[0]
        elif len(limits) == 2:
          lower_limit, upper_limit = limits
      else:
        raise ValueError
    except ValueError as e:
      print(e, 'Maybe function other than "range" is used is comprehension')
    return fr'_{{{var}={lower_limit}}}^{{{upper_limit}}}'


  def visit_Attribute(self, node):  # pylint: disable=invalid-name
    vstr = self.visit(node.value)
    astr = str(node.attr)
    return vstr + '.' + astr

  def visit_Name(self, node):  # pylint: disable=invalid-name
    return self._parse_math_symbols(str(node.id))

  def visit_Constant(self, node):  # pylint: disable=invalid-name
    # for python >= 3.8
    return str(node.n)

  def visit_Num(self, node):  # pylint: disable=invalid-name
    # for python < 3.8
    return str(node.n)

  def visit_UnaryOp(self, node):  # pylint: disable=invalid-name
    """Visit a unary op node."""
    def _wrap(child):
      latex = self.visit(child)
      if (isinstance(child, ast.BinOp) and
          isinstance(child.op, (ast.Add, ast.Sub))):
        return r'\left(' + latex + r'\right)'
      return latex

    reprs = {
        ast.UAdd: (lambda: _wrap(node.operand)),
        ast.USub: (lambda: '-' + _wrap(node.operand)),
        ast.Not: (lambda: r'\lnot\left(' + _wrap(node.operand)+r'\right)')
    }

    if type(node.op) in reprs:
      return reprs[type(node.op)]()
    return r'\mathrm{unknown\_uniop}(' + self.visit(node.operand) + ')'

  def visit_BinOp(self, node):  # pylint: disable=invalid-name
    """Visit a binary op node."""
    priority = constants.BIN_OP_PRIORITY

    def _unwrap(child):
      return self.visit(child)

    def _wrap(child):
      latex = _unwrap(child)
      if isinstance(child, ast.BinOp):
        cp = priority[type(child.op)] if type(child.op) in priority else 100
        pp = priority[type(node.op)] if type(node.op) in priority else 100
        if cp < pp:
          return '(' + latex + ')'
      return latex

    l = node.left
    r = node.right
    reprs = {
        ast.Add: (lambda: _wrap(l) + ' + ' + _wrap(r)),
        ast.Sub: (lambda: _wrap(l) + ' - ' + _wrap(r)),
        ast.Mult: (lambda: _wrap(l) + _wrap(r)),
        ast.MatMult: (lambda: _wrap(l) + _wrap(r)),
        ast.Div: (lambda: r'\frac{' + _unwrap(l) + '}{' + _unwrap(r) + '}'),
        ast.FloorDiv: (lambda: r'\left\lfloor\frac{' + _unwrap(l) + '}{' + _unwrap(r) + r'}\right\rfloor'),
        ast.Mod: (lambda: _wrap(l) + r' \bmod ' + _wrap(r)),
        ast.Pow: (lambda: _wrap(l) + '^{' + _unwrap(r) + '}'),
    }

    if type(node.op) in reprs:
      return reprs[type(node.op)]()
    return r'\mathrm{unknown\_binop}(' + _unwrap(l) + ', ' + _unwrap(r) + ')'

  def visit_Compare(self, node):  # pylint: disable=invalid-name
    """Visit a compare node."""
    lstr = self.visit(node.left)
    rstr = self.visit(node.comparators[0])

    if isinstance(node.ops[0], ast.Eq):
      return lstr + '=' + rstr
    if isinstance(node.ops[0], ast.Gt):
      return lstr + '>' + rstr
    if isinstance(node.ops[0], ast.Lt):
      return lstr + '<' + rstr
    if isinstance(node.ops[0], ast.GtE):
      return lstr + r'\ge ' + rstr
    if isinstance(node.ops[0], ast.LtE):
      return lstr + r'\le ' + rstr
    if isinstance(node.ops[0], ast.NotEq):
      return lstr + r'\ne ' + rstr
    if isinstance(node.ops[0], ast.Is):
      return lstr + r'\equiv' + rstr

    return r'\mathrm{unknown\_comparator}(' + lstr + ', ' + rstr + ')'

  def visit_BoolOp(self, node):  # pylint: disable=invalid-name
    logic_operator = r'\lor ' if isinstance(node.op, ast.Or) \
                else r'\land ' if isinstance(node.op, ast.And) \
                else r' \mathrm{unknown\_operator} '
    # visit all the elements in the ast.If node recursively
    return (r'\left(' + self.visit(node.values[0]) + r'\right)' + logic_operator
            + r'\left(' + self.visit(node.values[1]) + r'\right)')

  def visit_If(self, node):  # pylint: disable=invalid-name
    """Visit an if node."""
    latex = r'\left\{ \begin{array}{ll} '

    while isinstance(node, ast.If):
      cond_latex = self.visit(node.test)
      true_latex = self.visit(node.body[0])
      latex += true_latex + r', & \mathrm{if} \ ' + cond_latex + r' \\ '
      node = node.orelse[0]

    latex += self.visit(node)
    return latex + r', & \mathrm{otherwise} \end{array} \right.'


def get_latex(fn, math_symbol=True):
  try:
    source = inspect.getsource(fn)
  # pylint: disable=broad-except
  except Exception:
    # Maybe running on console.
    source = dill.source.getsource(fn)

  return LatexifyVisitor(math_symbol=math_symbol).visit(ast.parse(source))


def with_latex(*args, math_symbol=True):
  """Translate a function with latex representation."""

  class _LatexifiedFunction:
    """Function with latex representation."""

    def __init__(self, fn):
      self._fn = fn
      self._str = get_latex(fn, math_symbol=math_symbol)

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
      return r'$$ \displaystyle ' + self._str + ' $$'

  if len(args) == 1 and callable(args[0]):
    return _LatexifiedFunction(args[0])

  def ret(fn):
    return _LatexifiedFunction(fn)
  return ret
