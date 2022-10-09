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

MATH_SYMBOLS = {
    "aleph",
    "alpha",
    "beta",
    "beth",
    "chi",
    "daleth",
    "delta",
    "digamma",
    "epsilon",
    "eta",
    "gamma",
    "gimel",
    "iota",
    "kappa",
    "lambda",
    "mu",
    "nu",
    "omega",
    "omega",
    "phi",
    "pi",
    "psi",
    "rho",
    "sigma",
    "tau",
    "theta",
    "upsilon",
    "varepsilon",
    "varkappa",
    "varphi",
    "varpi",
    "varrho",
    "varsigma",
    "vartheta",
    "xi",
    "zeta",
    "Delta",
    "Gamma",
    "Lambda",
    "Omega",
    "Phi",
    "Pi",
    "Sigma",
    "Theta",
    "Upsilon",
    "Xi",
}

BUILTIN_CALLEES = {
    "abs": (r"\left|{", r"}\right|"),
    "math.acos": (r"\arccos{\left({", r"}\right)}"),
    "math.acosh": (r"\mathrm{arccosh}{\left({", r"}\right)}"),
    "math.asin": (r"\arcsin{\left({", r"}\right)}"),
    "math.asinh": (r"\mathrm{arcsinh}{\left({", r"}\right)}"),
    "math.atan": (r"\arctan{\left({", r"}\right)}"),
    "math.atanh": (r"\mathrm{arctanh}{\left({", r"}\right)}"),
    "math.ceil": (r"\left\lceil{", r"}\right\rceil"),
    "math.cos": (r"\cos{\left({", r"}\right)}"),
    "math.cosh": (r"\cosh{\left({", r"}\right)}"),
    "math.exp": (r"\exp{\left({", r"}\right)}"),
    "math.fabs": (r"\left|{", r"}\right|"),
    "math.factorial": (r"\left({", r"}\right)!"),
    "math.floor": (r"\left\lfloor{", r"}\right\rfloor"),
    "math.fsum": (r"\sum\left({", r"}\right)"),
    "math.gamma": (r"\Gamma\left({", r"}\right)"),
    "math.log": (r"\log{\left({", r"}\right)}"),
    "math.log10": (r"\log_{10}{\left({", r"}\right)}"),
    "math.log2": (r"\log_{2}{\left({", r"}\right)}"),
    "math.prod": (r"\prod \left({", r"}\right)"),
    "math.sin": (r"\sin{\left({", r"}\right)}"),
    "math.sinh": (r"\sinh{\left({", r"}\right)}"),
    "math.sqrt": (r"\sqrt{", "}"),
    "math.tan": (r"\tan{\left({", r"}\right)}"),
    "math.tanh": (r"\tanh{\left({", r"}\right)}"),
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
