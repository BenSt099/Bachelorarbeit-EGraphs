import re
from src.egraph import AbstractSyntaxTree


def validate_expression(expression):
    """"""

    ast = AbstractSyntaxTree.AbstractSyntaxTree("(/ (* a 22) 2)")

    expression_parts = True
    for c in expression:
        if c in ("/", "*", "+", "-", "<<", ">>", " ") or re.search("[a-zA-Z0-9]", c):
            expression_parts += True
        else:
            expression_parts += False

    return (
        expression.startswith("(") and expression.endswith(")") and expression_parts
    )
