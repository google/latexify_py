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
"""Latexify module-level constants"""

import ast
from typing import NamedTuple


class Actions(NamedTuple):
    """A class which holds supported actions as constants"""

    SET_BOUNDS = "set_bounds"


actions = Actions()

PREFIXES = ["math", "numpy", "np"]

BUILTIN_CALLEES = {
    "abs": (r"\left|{", r"}\right|"),
    "acos": (r"\arccos{\left({", r"}\right)}"),
    "acosh": (r"\mathrm{arccosh}{\left({", r"}\right)}"),
    "arccos": (r"\arccos{\left({", r"}\right)}"),
    "arccosh": (r"\mathrm{arccosh}{\left({", r"}\right)}"),
    "arcsin": (r"\arcsin{\left({", r"}\right)}"),
    "arcsinh": (r"\mathrm{arcsinh}{\left({", r"}\right)}"),
    "arctan": (r"\arctan{\left({", r"}\right)}"),
    "arctanh": (r"\mathrm{arctanh}{\left({", r"}\right)}"),
    "asin": (r"\arcsin{\left({", r"}\right)}"),
    "asinh": (r"\mathrm{arcsinh}{\left({", r"}\right)}"),
    "atan": (r"\arctan{\left({", r"}\right)}"),
    "atanh": (r"\mathrm{arctanh}{\left({", r"}\right)}"),
    "ceil": (r"\left\lceil{", r"}\right\rceil"),
    "cos": (r"\cos{\left({", r"}\right)}"),
    "cosh": (r"\cosh{\left({", r"}\right)}"),
    "exp": (r"\exp{\left({", r"}\right)}"),
    "fabs": (r"\left|{", r"}\right|"),
    "factorial": (r"\left({", r"}\right)!"),
    "floor": (r"\left\lfloor{", r"}\right\rfloor"),
    "fsum": (r"\sum\left({", r"}\right)"),
    "gamma": (r"\Gamma\left({", r"}\right)"),
    "log": (r"\log{\left({", r"}\right)}"),
    "log10": (r"\log_{10}{\left({", r"}\right)}"),
    "log2": (r"\log_{2}{\left({", r"}\right)}"),
    "prod": (r"\prod \left({", r"}\right)"),
    "sin": (r"\sin{\left({", r"}\right)}"),
    "sinh": (r"\sinh{\left({", r"}\right)}"),
    "sqrt": (r"\sqrt{", "}"),
    "tan": (r"\tan{\left({", r"}\right)}"),
    "tanh": (r"\tanh{\left({", r"}\right)}"),
    "sum": (r"\sum \left({", r"}\right)"),
}

BIN_OP_PRIORITY = {
    ast.Add: 10,
    ast.Sub: 10,
    ast.Mult: 20,
    ast.MatMult: 20,
    ast.Div: 20,
    ast.FloorDiv: 20,
    ast.Mod: 20,
    ast.Pow: 30,
}
