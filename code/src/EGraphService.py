"""This module contains the EGraphService and a function to check expressions.

Classes:
    EGraphService

Functions:
    is_valid_expression
"""

import os
import json
from datetime import datetime
from EGraph import EGraph, apply_rules, export_egraph_to_file
from RewriteRule import RewriteRule
from AbstractSyntaxTree import AbstractSyntaxTree


def is_valid_expression(expression):
    """This function checks if the given expression is a valid expression.
    This is done by trying to create an AST. If it works, the expression could
    still be invalid. Therefore, the string representation is compared to the
    original expression.

    :param expression: A string in prefix-notation
    :return: Returns True if the expression is valid, False otherwise.
    """
    try:
        ast = AbstractSyntaxTree(expression)
    except IndexError:
        return False

    return expression == str(ast)


class EGraphService:
    """Class that represents the EGraphService.

    Attributes:
        - rrc: rewrite rule counter
        - dict_of_rules: Dictionary of rules
        - egraph:
        - expr: The expression to the corresponding EGraph
        - egraphs: List with debug strings
        - current_major: pointer
        - current_minor: pointer
    """

    def __init__(self):
        """Initialises class. Takes no arguments.

        :returns: None.
        """
        self.rrc = 0
        self.dict_of_rules = {}
        self.egraph = None
        self.expr = None
        self.egraphs = [[]]
        self.current_major = 0
        self.current_minor = 0

    def save_rr_to_file(self):
        """"""
        rules = dict()
        for k, v in self.dict_of_rules.items():
            rules[k] = [v.name, str(v.expr_lhs), str(v.expr_rhs)]
        with open(
            ("rules-" + datetime.now().isoformat() + ".json").replace(":", "_"),
            mode="w",
            encoding="utf-8",
        ) as file:
            json.dump({"dor": rules}, file)
        return True

    def set_rules(self, data):
        """"""

        return True

    def get_snapshot(self):
        """"""
        rules = dict()
        for k, v in self.dict_of_rules.items():
            rules[k] = [v.name, str(v.expr_lhs), str(v.expr_rhs)]
        return {"dor": rules, "graph": self.expr}

    def save_to_file(self):
        """"""
        with open(
            ("egraphs-" + datetime.now().isoformat() + ".json").replace(":", "_"),
            mode="w",
            encoding="utf-8",
        ) as file:
            json.dump(self.get_snapshot(), file)
        return True

    def set_service(self, data):
        """"""
        self.create_egraph(data["graph"])
        self.rrc = 0
        for k, v in data["dor"].items():
            self.add_rule(v[1], v[2])
        return True

    def add_rule(self, lhs, rhs):
        if is_valid_expression(lhs) and is_valid_expression(rhs):
            self.dict_of_rules[self.rrc] = RewriteRule(str(self.rrc), lhs, rhs)
            self.rrc += 1
            return self.rrc - 1
        return False

    def apply(self, rule):
        """Apply a rewrite rule to the egraph."""
        eg, dbg = apply_rules([self.dict_of_rules[rule]], self.egraph[0])
        self.egraph = (eg, self.egraph[1])
        self.egraphs.append(dbg)

    def extract(self):
        """"""
        # self.egraph[0].equality_saturation()

        # self.egraphs.append()
        return ""

    def get_all_rules(self):
        """"""
        return self.dict_of_rules

    def delete_rule(self, rule):
        self.dict_of_rules.pop(rule)

    def create_egraph(self, expr):
        """"""
        eg = EGraph()
        eterm_id = eg.add_node(AbstractSyntaxTree(expr).root_node)
        self.egraph = (eg, eterm_id)
        self.expr = expr
        self.egraphs = [[]]
        self.current_major = 0
        self.current_minor = 0
        self.egraphs[self.current_major].append(["EGraph created.", eg.egraph_to_dot()])
        self.rrc = 0
        self.dict_of_rules = {}

    def move_backward(self):
        """"""
        if self.current_minor == 0:
            if self.current_major == 0:
                pass
            else:
                self.current_major -= 1
                self.current_minor = len(self.egraphs[self.current_major]) - 1
        else:
            self.current_minor -= 1

    def move_forward(self):
        """"""
        if len(self.egraphs[self.current_major]) - 1 == self.current_minor:
            if self.current_major == len(self.egraphs) - 1:
                pass
            else:
                self.current_minor = 0
                self.current_major += 1
        else:
            self.current_minor += 1

    def move_fastbackward(self):
        """"""
        if self.current_major != 0:
            self.current_major -= 1
            self.current_minor = len(self.egraphs[self.current_major]) - 1

    def move_fastforward(self):
        """"""
        if self.current_major != len(self.egraphs) - 1:
            self.current_major += 1
            self.current_minor = len(self.egraphs[self.current_major]) - 1

    def get_current_egraph(self):
        """Returns the egraph that is currently selected by the minor and
        major pointers.

        :return: String representation of the egraph in DOT format.
        """
        if self.egraphs == [[]]:
            return None
        else:
            return self.egraphs[self.current_major][self.current_minor]

    def export(self, ext_format):
        """"""
        return export_egraph_to_file(
            self.get_current_egraph()[1], str(os.getcwd()), extension=ext_format
        )
