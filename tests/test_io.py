import math
import pytest

from latexify import with_latex


def solve(a, b, c):
  return (-b + math.sqrt(b**2 - 4*a*c)) / (2*a)


solve_latex = r'\mathrm{solve}(a, b, c) \triangleq \frac{-b + \sqrt{b^{2} - 4ac}}{2a}'


def sinc(x):
  if x == 0:
    return 1
  else:
    return math.sin(x) / x


sinc_latex = (
  r'\mathrm{sinc}(x) \triangleq \left\{ \begin{array}{ll} 1, & \mathrm{if} \ x=0 \\ \frac{\sin{(x)}}{x}, &'
  r' \mathrm{otherwise} \end{array} \right.'
)


func_and_latex_str_list = [
  (solve, solve_latex),
  (sinc, sinc_latex)
]


@pytest.mark.parametrize('func, expected_latex', func_and_latex_str_list)
def test_with_latex_to_str(func, expected_latex):
  latexified_function = with_latex(func)
  assert str(latexified_function) == expected_latex
  assert latexified_function._repr_latex_() == expected_latex
