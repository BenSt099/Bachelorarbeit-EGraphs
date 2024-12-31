from EGraph import EGraph, apply_rules
from RewriteRule import RewriteRule
from AbstractSyntaxTree import AbstractSyntaxTree


def is_valid_expression(expression):
    """Returns True if the expression is valid, False otherwise.

    :param expression: A string in prefix-notation
    :return: Boolean
    """
    try:
        ast = AbstractSyntaxTree(expression)
    except IndexError:
        return False

    return expression == str(ast)


class EGraphService:
    def __init__(self):
        """"""
        self.rrc = 0  # rewrite rule counter
        self.dict_of_rules = {}
        self.egraph = None
        self.expr = None
        self.egraphs = [[]]
        self.current_major = 0
        self.current_minor = 0

    def get_snapshot(self):
        """"""
        return {'rrc': self.rrc, 'dor': self.dict_of_rules, 'graph': self.expr}

    def set_service(self, data):
        """"""
        # TODO
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
        """"""
        if self.egraphs == [[]]:
            return None
        else:
            return self.egraphs[self.current_major][self.current_minor]
