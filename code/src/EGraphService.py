from EGraph import EGraph
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
        self.egraphs = []
        self.current_major = 0
        self.current_minor = 0

    def set_service(self, rrc, dict_of_rules):
        """"""
        self.rrc = rrc
        self.dict_of_rules = dict_of_rules

    def add_rule(self, lhs, rhs):
        if is_valid_expression(lhs) and is_valid_expression(rhs):
            self.dict_of_rules[self.rrc] = RewriteRule(str(self.rrc), lhs, rhs)
            self.rrc += 1
            return self.rrc - 1
        return False

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
        self.egraphs = []
        self.egraphs.append(["EGraph created.", eg.egraph_to_dot()])
        self.rrc = 0
        self.dict_of_rules = {}

    def move_backward(self, mode):
        """"""
        if mode == "false":
            return False
        else:
            if self.current_minor == 0:
                return False
            self.current_minor -= 1
            return True

    def move_forward(self, mode):
        """"""
        if mode == "false":
            return False
        else:
            if len(self.egraphs[self.current_major]) - 1 == self.current_minor:
                return False
            self.current_minor += 1
            return True

    def move_fastbackward(self):
        """"""
        if self.current_major == 0:
            return False
        self.current_major -= 1
        return True

    def move_fastforward(self):
        """"""
        if self.current_major == len(self.egraphs) - 1:
            return False
        self.current_major += 1
        return True

    def get_current_egraph(self):
        """"""
        if len(self.egraphs) == 0:
            return None
        else:
            return self.egraphs[self.current_major][self.current_minor]