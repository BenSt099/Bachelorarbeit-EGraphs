from collections import deque
import re


class ASTNode:
    left = ""
    key = ""
    right = ""


representation = str()


def to_string(node):
    global representation
    preorder(node)
    representation = representation.strip()
    return representation


def preorder(node):
    global representation
    if node.left == "" and node.right == "":
        representation += str(node.key) + " "
        return
    else:
        representation += str(node.key) + " "
    preorder(node.left)
    preorder(node.right)


def process(expr):
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
