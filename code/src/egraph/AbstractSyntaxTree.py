"""This module creates an AbstractSyntaxTree from a given expression.

Classes:
    AbstractSyntaxTree: Class used for generating AST from expression.
    AbstractSyntaxTreeNode: Class used for representing nodes in AST.
"""

from collections import deque


class AbstractSyntaxTreeNode:
    """Class that represents a node in an AST.

    Please also see class 'AbstractSyntaxTree'.

    Attributes:
        left: Another ASTNode.
        key: A string to store information
        right: Another ASTNode.
    """

    def __init__(self):
        """Initialises class. Takes no arguments."""
        self.left = None
        self.key = str()
        self.right = None


class AbstractSyntaxTree:
    """Turns expression in an AST.

    Attributes:
        root_node: Another ASTNode.
        string_representation: A string to store information
    """

    def __init__(self, expression):
        """Initializes class. Takes one argument.

        Arguments:
          expression: A string representing an expression in prefix-notation.
        """
        self.root_node = self._process_expression(expression)
        self.string_representation = str()

    def to_string(self):
        """Returns the string representation of the AST."""
        self._preorder(self.root_node)
        self.string_representation = self.string_representation.strip()
        return self.string_representation

    def _preorder(self, ast_node):
        """Traverse the AST (preorder) and write to 'representation'."""
        if ast_node is not None:
            self.string_representation += str(ast_node.key) + " "
            self._preorder(ast_node.left)
            self._preorder(ast_node.right)

    def _process_expression(self, expression):
        """Turn given expression into AST.

        Loops over expression, thereby processing one character at a time.
        Character can be: '+', '*', '-', '/', '<', '>', '(', ')', ' ' or
        a variable.

        Arguments:
            expression -- an expression in prefix-notation
        """
        root_ast_node = None
        stack = deque()
        for character in expression:
            if character == "(":
                if not stack:
                    ast_node = AbstractSyntaxTreeNode()
                    stack.append(ast_node)
                    root_ast_node = ast_node
                else:
                    last_ast_node = stack[-1]
                    ast_node = AbstractSyntaxTreeNode()
                    if last_ast_node.left is None and last_ast_node.right is None:
                        last_ast_node.left = ast_node
                    elif last_ast_node.left is None:
                        last_ast_node.left = ast_node
                    else:
                        last_ast_node.right = ast_node
                    stack.append(ast_node)
            elif character == ")":
                stack.pop()
            elif character in ("/", "*", "+", "-", "<", ">"):
                last_ast_node = stack[-1]
                last_ast_node.key = character
            elif character == " ":
                pass
            else:
                last_ast_node = stack[-1]
                if last_ast_node.left is None and last_ast_node.right is None:
                    ast_node = AbstractSyntaxTreeNode()
                    ast_node.key = character
                    last_ast_node.left = ast_node
                elif last_ast_node.left is None:
                    ast_node = AbstractSyntaxTreeNode()
                    ast_node.key = character
                    last_ast_node.left = ast_node
                else:
                    ast_node = AbstractSyntaxTreeNode()
                    ast_node.key = character
                    last_ast_node.right = ast_node
        return root_ast_node
