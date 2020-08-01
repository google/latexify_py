# This is very scratchy and supports only limited portion of Python functions.

import ast
import math
import inspect


class LatexifyVisitor(ast.NodeVisitor):

  def __init__(self, math_symbol):
    self.math_symbol = math_symbol
    super(ast.NodeVisitor).__init__()

  def _parse_math_symbols(self, val: str) -> str:
    if not self.math_symbol:
      return val
    greek_and_hebrew = [
        'aleph', 'alpha', 'beta', 'beth', 'chi', 'daleth',
        'delta', 'digamma', 'epsilon', 'eta', 'gimel',
        'iota', 'kappa', 'lambda', 'mu', 'nu', 'omega', 'omega',
        'phi', 'pi', 'psi', 'rho', 'sigma', 'tau', 'theta',
        'upsilon', 'varepsilon', 'varkappa', 'varphi', 'varpi', 'varrho',
        'varsigma', 'vartheta', 'xi', 'zeta', 'Delta', 'Gamma',
        'Lambda', 'Omega', 'Phi', 'Pi', 'Sigma', 'Theta',
        'Upsilon', 'Xi',
        # 'gamma' <-- might break with `math.gamma`; leaving out for now.
    ]
    if val in greek_and_hebrew:
      return '{\\' + val + '}'
    else:
      return val

  def generic_visit(self, node):
    return str(node)

  def visit_Module(self, node):
    return self.visit(node.body[0])

  def visit_FunctionDef(self, node, equal:str=r'\triangleq'):
    name_str = r'\operatorname{' + str(node.name) + '}'
    arg_strs = [self._parse_math_symbols(str(arg.arg)) for arg in node.args.args]
    body_str = self.visit(node.body[0])
    # CHANGE:(20200801@1MLightyears)
    # use r"\triangleq" as default is fine but maybe it is more user-friendly
    # to leave an interface for users to choose what equal mark they want to.
    # I leave it here as-is and may implement this in future.
    return name_str + '(' + ', '.join(arg_strs) + r') ' + equal + ' ' + body_str

  def visit_Return(self, node):
    return self.visit(node.value)

  def visit_Call(self, node):
    builtin_callees = {
        'abs': (r'\left|{', r'}\right|'),
        'math.acos': (r'\arccos{\left({', r'}\right)}'),
        'math.acosh': (r'\operatorname{arccosh}{\left({', r'}\right)}'),
        'math.asin': (r'\arcsin{\left({', r'}\right)}'),
        'math.asinh': (r'\operatorname{arcsinh}{\left({', r'}\right)}'),
        'math.atan': (r'\arctan{\left({', r'}\right)}'),
        'math.atanh': (r'\operatorname{arctanh}{\left({', r'}\right)}'),
        'math.ceil': (r'\left\lceil{', r'}\right\rceil'),
        'math.cos': (r'\cos{\left({', r'}\right)}'),
        'math.cosh': (r'\cosh{\left({', r'}\right)}'),
        'math.exp': (r'\exp{\left({', r'}\right)}'),
        'math.fabs': (r'\left|{', r'}\right|'),
        'math.factorial': (r'\left({', r'}\right)!'),
        'math.floor': (r'\left\lfloor{', r'}\right\rfloor'),
        'math.fsum': (r'\sum\left({', r'}\right)'),
        'math.gamma': (r'\Gamma\left({', r'}\right)'),
        'math.log': (r'\log{\left({', r'}\right)}'),
        'math.log10': (r'\log_{10}{\left({', r'}\right)}'),
        'math.log2': (r'\log_{2}{\left({', r'}\right)}'),
        'math.prod': (r'\prod \left({', r'}\right)'),
        'math.sin': (r'\sin{\left({', r'}\right)}'),
        'math.sinh': (r'\sinh{\left({', r'}\right)}'),
        'math.sqrt': (r'\sqrt{', '}'),
        'math.tan': (r'\tan{\left({', r'}\right)}'),
        'math.tanh': (r'\tanh{\left({', r'}\right)}'),
        'sum': (r'\sum \left({', r'}\right)'),
    }

    callee_str = self.visit(node.func)
    if callee_str in builtin_callees:
      lstr, rstr = builtin_callees[callee_str]
    else:
      if callee_str.startswith('math.'):
        callee_str = callee_str[5:]
      lstr = r'\operatorname{' + callee_str + r'}\left('
      rstr = r'\right)'

    arg_strs = [self.visit(arg) for arg in node.args]
    return lstr + ', '.join(arg_strs) + rstr

  def visit_Attribute(self, node):
    vstr = self.visit(node.value)
    astr = str(node.attr)
    return vstr + '.' + astr

  def visit_Name(self, node):
    return self._parse_math_symbols(str(node.id))

  def visit_Num(self, node):
    return str(node.n)

  def visit_UnaryOp(self, node):
    def _wrap(child):
      latex = self.visit(child)
      if isinstance(child, ast.BinOp) and isinstance(child.op, (ast.Add, ast.Sub)):
        return '(' + latex + ')'
      return latex

    reprs = {
        ast.UAdd: (lambda: _wrap(node.operand)),
        ast.USub: (lambda: '-' + _wrap(node.operand)),
    }

    if type(node.op) in reprs:
      return reprs[type(node.op)]()
    else:
      return r'\operatorname{unknown\_uniop}(' + vstr + ')'

  def visit_BinOp(self, node):
    priority = {
        ast.Add: 10,
        ast.Sub: 10,
        ast.Mult: 20,
        ast.MatMult: 20,
        ast.Div: 20,
        ast.FloorDiv: 20,
        ast.Mod: 20,
        ast.Pow: 30,
    }

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
    else:
      return r'\operatorname{unknown\_binop}(' + _unwrap(l) + ', ' + _unwrap(r) + ')'

  def visit_Compare(self, node):
    lstr = self.visit(node.left)
    rstr = self.visit(node.comparators[0])

    if isinstance(node.ops[0], ast.Eq):
      return lstr + '=' + rstr
    # CHANGE:(20200801@1MLightyears) Add support for conditions for <,>,\ge,\le,\ne,is
    elif isinstance(node.ops[0], ast.Gt):
      return lstr + '>' + rstr
    elif isinstance(node.ops[0], ast.Lt):
      return lstr + '<' + rstr
    elif isinstance(node.ops[0], ast.GtE):
      return lstr + r'\ge ' + rstr
    elif isinstance(node.ops[0], ast.LtE):
      return lstr + r'\le ' + rstr
    elif isinstance(node.ops[0], ast.NotEq):
      return lstr + r'\ne ' + rstr
    elif isinstance(node.ops[0], ast.Is):
      return lstr + r'\space is\space ' + rstr
    elif isinstance(node.ops[0], ast.IsNot):
      return lstr + r'\space is\space not\space ' + rstr

    else:
      return r'\operatorname{unknown\_comparator}(' + lstr + ', ' + rstr + ')'

  # CHANGE:(20200801@1MLightyears) Add support for BoolOp, which allow Latexify to
  # deal with more complex boolean statements.
  # The structure is weak, for I seldom use very complex boolean statements and
  # currently have no idea how to simply implement a result like "x=0,1" instead of
  # "x=0 Or x=1" as it is now XD
  def visit_BoolOp(self, node):
    '''
    When node is an instance of ast.BoolOp, it has:
    node.op(ast.And, ast.Or, ast.Not): type of the boolean operator.
    node.values(list of ast.Compare, ast.BoolOp): a list of boolean sub-clause.
    '''
    logic_operator = r' \operatorname{unknown\_comparator} '
    if isinstance(node.op, ast.Or):
      logic_operator = r'\\&\mathrm{Or}\space '
    elif isinstance(node.op, ast.And):
      logic_operator = r'\\&\mathrm{And}\space '
    # visit all the elements in the ast.If node recursively
    return logic_operator.join([self.visit(subnode) for subnode in node.values])

  def visit_If(self, node):
    latex = r'\left\{ \begin{array}{ll} '

    while isinstance(node, ast.If):
      cond_latex = self.visit(node.test)
      true_latex = self.visit(node.body[0])
      latex += true_latex + r', & \mathrm{if} \ ' + cond_latex + r' \\ '
      node = node.orelse[0]

    return latex + self.visit(node) + r', & \mathrm{otherwise} \end{array} \right.'


def get_latex(fn, math_symbol=True):
  return LatexifyVisitor(math_symbol=math_symbol).visit(ast.parse(inspect.getsource(fn)))


def with_latex(*args, math_symbol=True):

  class _LatexifiedFunction:
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
      return self._str

  if len(args) == 1 and callable(args[0]):
    return _LatexifiedFunction(args[0])
  else:
    return lambda fn: _LatexifiedFunction(fn)
