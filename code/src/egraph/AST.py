from collections import deque
import re


class ASTNode:
    left = ""
    key = ""
    right = ""


class AST:

    def __init__(self, expression):
        self.rootNode = self.process(expression)

    representation = str()
    rootNode = None

    def to_string(self):
        self.preorder(self.rootNode)
        self.representation = self.representation.strip()
        return self.representation

    def preorder(self, node):
        if node.left == "" and node.right == "":
            self.representation += str(node.key) + " "
            return
        else:
            self.representation += str(node.key) + " "
        self.preorder(node.left)
        self.preorder(node.right)

    def process(self, expr):
        root = ""
        stack = deque()
        for c in expr:
            if c == "(":
                if not stack:
                    k = ASTNode()
                    stack.append(k)
                    root = k
                else:
                    s = stack[-1]
                    k = ASTNode()
                    if s.left == "" and s.right == "":
                        s.left = k
                    elif s.left == "":
                        s.left = k
                    else:
                        s.right = k
                    stack.append(k)
            elif c == ")":
                stack.pop()
            elif re.search("[0-9]+", c):
                s = stack[-1]
                if s.left == "" and s.right == "":
                    k = ASTNode()
                    k.key = c
                    s.left = k
                elif s.left == "":
                    k = ASTNode()
                    k.key = c
                    s.left = k
                else:
                    k = ASTNode()
                    k.key = c
                    s.right = k
            elif c == "/" or c == "*" or c == "+" or c == "-" or c == "<<" or c == ">>":
                s = stack[-1]
                s.key = c
            elif c == " ":
                pass
            else:
                s = stack[-1]
                if s.left == "" and s.right == "":
                    k = ASTNode()
                    k.key = c
                    s.left = k
                elif s.left == "":
                    k = ASTNode()
                    k.key = c
                    s.left = k
                else:
                    k = ASTNode()
                    k.key = c
                    s.right = k
        return root
