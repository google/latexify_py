# `latexify` parameters

This document describes the list of parameters to control the behavior of `latexify`.


## `identifiers: dict[str, str]`

Key-value pair of identifiers to replace.

```python
identifiers = {
    "my_function": "f",
    "my_inner_function": "g",
    "my_argument": "x",
}

@latexify.function(identifiers=identifiers)
def my_function(my_argument):
    return my_inner_function(my_argument)

my_function
```

$$f(x) = \mathrm{g}\left(x\right)$$


## `reduce_assignments: bool`

Whether to compose all variables defined before the `return` statement.

The current version of `latexify` recognizes only the assignment statements.
Analyzing functions with other control flows may raise errors.

```python
@latexify.function(reduce_assignments=True)
def f(a, b, c):
    discriminant = b**2 - 4 * a * c
    numerator = -b + math.sqrt(discriminant)
    denominator = 2 * a
    return numerator / denominator

f
```

$$f(a, b, c) = \frac{-b + \sqrt{b^{2} - 4 a c}}{2 a}$$


## `use_math_symbols: bool`

Whether to automatically convert variables with symbol names into LaTeX symbols or not.

```python
@latexify.function(use_math_symbols=True)
def greek(alpha, beta, gamma, Omega):
  return alpha * beta + math.gamma(gamma) + Omega

greek
```

$$\mathrm{greek}({\alpha}, {\beta}, {\gamma}, {\Omega}) = {\alpha} {\beta} + \Gamma\left({{\gamma}}\right) + {\Omega}$$


## `use_set_symbols: bool`

Whether to use binary operators for set operations or not.

```python
@latexify.function(use_set_symbols=True)
def f(x, y):
    return x & y, x | y, x - y, x ^ y, x < y, x <= y, x > y, x >= y

f
```

$$f(x, y) = \left( x \cap y\space,\space x \cup y\space,\space x \setminus y\space,\space x \mathbin{\triangle} y\space,\space {x \subset y}\space,\space {x \subseteq y}\space,\space {x \supset y}\space,\space {x \supseteq y}\right)$$


## `use_signature: bool`

Whether to output the function signature or not.

The default value of this flag depends on the frontend function.
`True` is used in `latexify.function`, while `False` is used in `latexify.expression`.

```python
@latexify.function(use_signature=False)
def f(a, b, c):
    return (-b + math.sqrt(b**2 - 4 * a * c)) / (2 * a)

f
```

$$\frac{-b + \sqrt{b^{2} - 4 a c}}{2 a}$$
