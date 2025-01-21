"""This module contains the EGraphService and a function to check expressions.

Classes:
    EGraphService

Functions:
    is_valid_expression
"""

import os
import json
from datetime import datetime
from EGraph import EGraph, apply_rules, export_egraph_to_file, \
    equality_saturation
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
    expression = expression.strip()
    try:
        ast = AbstractSyntaxTree(expression)
    except IndexError:
        return False

    return (
        expression == str(ast)
        and expression.startswith("(")
        and expression.endswith(")")
    )


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

    def save_rewrite_rules_to_file(self):
        """Saves all rewrite rules in a JSON file.

        :return: True if successful, False otherwise.
        """
        rules = dict()
        if self.dict_of_rules == dict():
            return False, "No rules to save."
        for k, v in self.dict_of_rules.items():
            rules[k] = [v.name, str(v.expr_lhs), str(v.expr_rhs)]
        try:
            with open(
                ("rules-" + datetime.now().isoformat() + ".json").replace(":", "_"),
                mode="w",
                encoding="utf-8",
            ) as file:
                json.dump({"RewriteRules": rules}, file)
        except OSError:
            return False, "Couldn't save file, OSError."
        path = str(os.getcwd())
        return True, "Downloaded rules in " + path[0:int(len(path)/2)] + " " + path[int(len(path)/2) + 1:len(path)] + "."

    def add_rewrite_rules_from_file(self, data):
        """Adds all rewrite rules from a file.

        :param data:
        :return: Boolean and msg
        """
        self.dict_of_rules = dict()
        try:
            d = data["RewriteRules"]
        except KeyError:
            return False, "Format is broken."

        if len(d.items()) < 1:
            return False, "No rewrite rules found."

        for k, v in d.items():
            if is_valid_expression(v[1]) and is_valid_expression(v[2]):
                self.add_rule(v[1], v[2])

        return True, "Added rewrite rules."

    def get_snapshot(self):
        """"""
        rules = dict()
        for k, v in self.dict_of_rules.items():
            rules[k] = [v.name, str(v.expr_lhs), str(v.expr_rhs)]
        return {"RewriteRules": rules, "graph": self.expr}

    def save_to_file(self):
        """"""
        try:
            with open(
                ("session-" + datetime.now().isoformat() + ".json").replace(":", "_"),
                mode="w",
                encoding="utf-8",
            ) as file:
                json.dump(self.get_snapshot(), file)
        except OSError:
            return False, "Couldn't save file, OSError."
        path = str(os.getcwd())
        return True, "Downloaded session in " + path[0:int(len(path)/2)] + " " + path[int(len(path)/2) + 1:len(path)] + "."

    def set_service(self, data):
        """

        :param data:
        :return:
        """
        try:
            d = data["graph"]
            e = data["RewriteRules"]
        except KeyError:
            return False, "Format is broken."
        self.create_egraph(d)
        self.rrc = 0
        for k, v in e.items():
            self.add_rule(v[1], v[2])
        return True, "Saved session."

    def add_rule(self, lhs, rhs):
        """"""
        if is_valid_expression(lhs) and is_valid_expression(rhs):
            self.dict_of_rules[self.rrc] = RewriteRule(str(self.rrc), lhs, rhs)
            self.rrc += 1
            return True, "Added rule.", self.rrc - 1
        return False, "No valid rule.", None

    def apply(self, rule):
        """Apply a rewrite rule to the egraph."""
        if rule not in self.dict_of_rules.keys():
            return False, "Couldn't apply rule."
        eg, dbg = apply_rules([self.dict_of_rules[rule]], self.egraph[0])
        self.egraph = (eg, self.egraph[1])
        self.egraphs.append(dbg)
        return True, "Applied rule."

    def extract(self):
        """"""
        eg, dbg, best = equality_saturation(list(self.dict_of_rules.values()), self.egraph[1], self.egraph[0])
        self.egraphs.append(dbg)
        self.egraph = (eg, self.egraph[1])

        return True, "Extracted best term. Use debug (>) output to watch extraction.", best

    def get_all_rules(self):
        """Returns all rules in dictionary format.

        :return: dictionary with rewrite rules
        """
        rules = dict()
        if self.dict_of_rules == dict():
            return False, "No rules to extract.", None
        for k, v in self.dict_of_rules.items():
            rules[k] = [v.name, str(v.expr_lhs), str(v.expr_rhs)]
        return True, "Added rules.", rules

    def create_egraph(self, expr):
        """Creates an EGraph.

        :param expr:
        :return:
        """
        if not is_valid_expression(expr):
            return False, "Invalid expression."
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
        return True, "Created EGraph."

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
            return False, "No EGraph there.", (None, None)
        else:
            return (
                True,
                "EGraph loaded.",
                self.egraphs[self.current_major][self.current_minor],
            )

    def export(self, extension_format):
        """
        Saves the currently selected EGraph into a chosen format.

        :param extension_format: Determines which format should be used (pdf, svg, png).
        :return: True if successful, False otherwise.
        """
        return export_egraph_to_file(
            self.get_current_egraph()[1], str(os.getcwd()), extension=extension_format
        )
