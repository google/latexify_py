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
"""Definition of NodeVisitorBase class."""


class NodeVisitorBase:
    """Base class of LaTeXify's AST visitor.

    Unlike `ast.NodeVisitor`, this pattern accepts also an additional argument
    `action` for each method, allowing us to control behavior of the methods by
    their caller. This is useful to choose which LaTeX representation is generated
    according to its surrounding environment.

    There are several examples below:

    node = <ast.Foobar>
    visitor = <MyVisitor extends NodeVisitorBase>

    # Calls the top existing method of following:
    # 1. visitor.visit_Foobar(node, None)
    # 2. visitor.generic_visit(node, None)
    visitor.visit(node)

    # Calls the top existing method of following:
    # 1. visitor.visit_Foobar_baz(node)
    # 2. visitor.visit_Foobar(node, 'baz')
    # 3. visitor.generic_visit(node, 'baz')
    visitor.visit(node, 'baz')

    # Calls the top existing method of following:
    # 1. visitor.visit_Foobar(node, '123abc')
    # 2. visitor.generic_visit(node, '123abc')
    visitor.visit(node, '123abc')
    """

    def visit(self, node, action: str = None):
        """Visits a node with specified action.

        Args:
          node: An AST node object to visit.
          action: Optional string argument to control the visitor's behavior.

        Returns:
          Implementation depended.
        """
        if action is not None:
            method = "visit_{}_{}".format(node.__class__.__name__, action)
            visitor = getattr(self, method, None)
            if callable(visitor):
                return visitor(node)  # pylint: disable=not-callable

        method = "visit_{}".format(node.__class__.__name__)
        visitor = getattr(self, method, self.generic_visit)
        if callable(visitor):
            return visitor(node, action)  # pylint: disable=not-callable

        raise AttributeError("{} is not callable.".format(method))

    def generic_visit(self, node, action):
        """Visitor method for all nodes without specific visitors."""
        raise NotImplementedError("LatexifyVisitorBase.generic_visit")
