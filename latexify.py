# This is very scratchy and supports only limited portion of Python functions.

import ast
import math
import inspect


class LatexifyVisitor(ast.NodeVisitor):
  def generic_visit(self, node):
    return str(node)

  def visit_Module(self, node):
    return self.visit(node.body[0])

  def visit_FunctionDef(self, node):
    name_str = r'\mathrm{' + str(node.name) + '}'
    arg_strs = [str(arg.arg) for arg in node.args.args]
    body_str = self.visit(node.body[0])
    return name_str + '(' + ', '.join(arg_strs) + r') \triangleq ' + body_str

  def visit_Return(self, node):
    return self.visit(node.value)

  def visit_Call(self, node):
    builtin_callees = {
        'math.sqrt': (r'\sqrt{', '}'),
        'math.sin': (r'\sin{(', ')}'),
    }

    callee_str = self.visit(node.func)
    if callee_str in builtin_callees:
      lstr, rstr = builtin_callees[callee_str]
    else:
      lstr = r'\mathrm{' + callee_str + '}('
      rstr = ')'

    arg_strs = [self.visit(arg) for arg in node.args]
    return lstr + ', '.join(arg_strs) + rstr

  def visit_Attribute(self, node):
    vstr = self.visit(node.value)
    astr = str(node.attr)
    return vstr + '.' + astr

  def visit_Name(self, node):
    return str(node.id)

  def visit_Num(self, node):
    return str(node.n)

  def visit_UnaryOp(self, node):
    def _wrap(child):
      repr = self.visit(child)
      if isinstance(child, ast.BinOp) and child.op in (ast.Add, ast.Sub):
        return '(' + repr + ')'
      return repr

    reprs = {
        ast.UAdd: (lambda: _wrap(node.operand)),
        ast.USub: (lambda: '-' + _wrap(node.operand)),
    }

    if type(node.op) in reprs:
      return reprs[type(node.op)]()
    else:
      return r'\mathrm{unknown_uniop}(' + vstr + ')'

  def visit_BinOp(self, node):
    priority = {
        ast.Add: 10,
        ast.Sub: 10,
        ast.Mult: 20,
        ast.Div: 20,
        ast.Pow: 30,
    }

    def _unwrap(child):
      return self.visit(child)

    def _wrap(child):
      repr = _unwrap(child)
      if isinstance(child, ast.BinOp):
        cp = priority[type(child.op)] if type(child.op) in priority else 100
        pp = priority[type(node.op)] if type(node.op) in priority else 100
        if cp < pp:
          return '(' + repr + ')'
      return repr

    l = node.left
    r = node.right
    reprs = {
        ast.Add: (lambda: _wrap(l) + ' + ' + _wrap(r)),
        ast.Sub: (lambda: _wrap(l) + ' - ' + _wrap(r)),
        ast.Mult: (lambda: _wrap(l) + _wrap(r)),
        ast.Div: (lambda: r'\frac{' + _unwrap(l) + '}{' + _unwrap(r) + '}'),
        ast.Pow: (lambda: _wrap(l) + '^{' + _unwrap(r) + '}'),
    }

    if type(node.op) in reprs:
      return reprs[type(node.op)]()
    else:
      return r'\mathrm{unknown_binop}(' + lstr + ', ' + rstr + ')'

  def visit_Compare(self, node):
    lstr = self.visit(node.left)
    rstr = self.visit(node.comparators[0])

    if isinstance(node.ops[0], ast.Eq):
      return lstr + '=' + rstr
    else:
      return r'\mathrm{unknown_compop}(' + lstr + ', ' + rstr + ')'

  def visit_If(self, node):
    cond_str = self.visit(node.test)
    tstr = self.visit(node.body[0])
    fstr = self.visit(node.orelse[0])
    return r'\left\{ \begin{array}{ll} ' + tstr + r', & \mathrm{if} \ ' + cond_str + r' \\ ' + fstr + r', & \mathrm{otherwise} \end{array} \right.'


def get_latex(fn):
  return LatexifyVisitor().visit(ast.parse(inspect.getsource(fn)))


def with_latex(fn):
  class _wrapper:
    def __init__(self, fn):
      self._fn = fn
      self._str = get_latex(fn)
    def __call__(self, *args):
      return self._fn(*args)
    def __str__(self):
      return self._str
  return _wrapper(fn)
