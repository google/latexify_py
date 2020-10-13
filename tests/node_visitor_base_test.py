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
"""Tests for node_visitor_base."""

import pytest

from latexify import node_visitor_base


class MockVisitor(node_visitor_base.NodeVisitorBase):
  """Mock visitor class."""

  def __init__(self):
    # Dummy member to fail visitor invocation.
    self.visit_Baz = None  # pylint: disable=invalid-name

  def generic_visit(self, node, action):
    return 'generic_visit: {}, {}'.format(node.__class__.__name__, action)

  def visit_Foo(self, node, action):  # pylint: disable=invalid-name
    del node
    return 'visit_Foo: {}'.format(action)

  def visit_Foo_abc(self, node):  # pylint: disable=invalid-name
    del node
    return 'visit_Foo_abc'

  def visit_Foo_xyz(self, node):  # pylint: disable=invalid-name
    del node
    return 'visit_Foo_xyz'


class Foo:
  pass


class Bar:
  pass


class Baz:
  pass


def test_generic_visit():
  visitor = MockVisitor()
  assert visitor.visit(Bar()) == 'generic_visit: Bar, None'
  assert visitor.visit(Bar(), 'unknown') == 'generic_visit: Bar, unknown'
  assert visitor.visit(Bar(), '123') == 'generic_visit: Bar, 123'


def test_visit_node():
  visitor = MockVisitor()
  assert visitor.visit(Foo()) == 'visit_Foo: None'
  assert visitor.visit(Foo(), 'unknown') == 'visit_Foo: unknown'
  assert visitor.visit(Foo(), '123') == 'visit_Foo: 123'


def test_visit_node_action():
  visitor = MockVisitor()
  assert visitor.visit(Foo(), 'abc') == 'visit_Foo_abc'
  assert visitor.visit(Foo(), 'xyz') == 'visit_Foo_xyz'


def test_invalid_visit():
  visitor = MockVisitor()
  with pytest.raises(AttributeError, match='visit_Baz is not callable'):
    visitor.visit(Baz())
