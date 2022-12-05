# Getting started

This document describes how to use `latexify` with your Python code.


## Installation

`latexify` depends on only Python libraries at this point.
You can simply install `latexify` via `pip`:

```shell
$ pip install latexify-py
```

Note that you have to install `latexify-py` rather than `latexify`.


## Using `latexify` in Jupyter

`latexify.function` decorator function wraps your functions to pretty-print them as
corresponding LaTeX formulas.
Jupyter recognizes this wrapper and try to print LaTeX instead of the original function.

The following snippet:

```python
@latexify.function
def solve(a, b, c):
    return (-b + math.sqrt(b**2 - 4 * a * c)) / (2 * a)

solve
```

will print the following formula to the output:

$$ \mathrm{solve}(a, b, c) = \frac{-b + \sqrt{b^2 - 4ac}}{2a} $$


Invoking wrapped functions work transparently as the original function.

```python
solve(1, 2, 1)
```

```
-1.0
```

Applying `str` to the wrapped function returns the underlying LaTeX source.

```python
print(solve)
```

```
f(n) = \\frac{-b + \\sqrt{b^{2} - 4ac}}{2a}
```

`latexify.expression` works similarly to `latexify.function`,
but it prints the function without its signature:
```python
@latexify.expression
def solve(a, b, c):
    return (-b + math.sqrt(b**2 - 4 * a * c)) / (2 * a)

solve
```

$$ \frac{-b + \sqrt{b^2 - 4ac}}{2a} $$


## Obtaining LaTeX expression directly

You can also use `latexify.get_latex`, which takes a function and directly returns the
LaTeX expression corresponding to the given function.

The same parameters with `latexify.function` can be applied to `latexify.get_latex` as
well.

```python
def solve(a, b, c):
    return (-b + math.sqrt(b**2 - 4 * a * c)) / (2 * a)

latexify.get_latex(solve)
```

```
f(n) = \\frac{-b + \\sqrt{b^{2} - 4ac}}{2a}
```
