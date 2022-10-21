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
"""Tests for core."""

import pytest

from latexify import with_latex

@with_latex
def list_comp():
    return [x for x in range(1, 5) if x > 2]

def test_list_comps():
    assert str(list_comp) == r"\mathrm{list_comp}() \triangleq [3, 4]"

@with_latex
def set_comp():
    return {x for x in range(1, 5) if x > 2}

def test_set_comps():
    assert str(set_comp) == r"\mathrm{set_comp}() \triangleq {3, 4}"

@with_latex
def dict_comp():
    return {x: x + 1 for x in range(1, 5) if x > 2}

def test_dict_comps():
    assert str(dict_comp) == r"\mathrm{dict_comp}() \triangleq {3: 4, 4: 5}"

@with_latex
def set_or():
    return {1} | {2, 3}

def test_set_ops():
    assert str(set_or) == r"\mathrm{set_or}() \triangleq \left\{ 1\right\}  \cup \left\{ 2\space,\space 3\right\} "

@with_latex
def set_union():
    return {1} & {1, 2}

def test_set_union():
    assert str(set_union) == r"\mathrm{set_union}() \triangleq \left\{ 1\right\}  \cap \left\{ 1\space,\space 2\right\} "

@with_latex
def set_xor():
    return {1} ^ {1, 2}

def test_set_xor():
    assert str(set_xor) == r"\mathrm{set_xor}() \triangleq \left\{ 1\right\}  \triangle \left\{ 1\space,\space 2\right\} "

@with_latex
def set_sub():
    return {1, 2} - {1}

def test_set_sub():
    print(set_sub)
    assert str(set_sub) == r"\mathrm{set_sub}() \triangleq \left\{ 1\space,\space 2\right\}  \setminus \left\{ 1\right\} "
