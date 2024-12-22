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
        self.mode = 0  # 0 = normal,  1 = debug
        self.rrc = 0  # rewrite rule counter
        self.dict_of_rules = {}
        self.egraphs = []

    def set_service(self, mode, rrc, dict_of_rules):
        """"""
        self.mode = mode
        self.rrc = rrc
        self.dict_of_rules = dict_of_rules

    def set_mode(self, mode):
        self.mode = mode

    def add_rule(self, lhs, rhs):
        if is_valid_expression(lhs) and is_valid_expression(rhs):
            self.dict_of_rules[self.rrc] = RewriteRule(
                str(self.rrc), lhs, rhs
            )
            self.rrc += 1
            return True
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
        self.egraphs.append((eg, eterm_id))

    def get_egraph(self):
        """"""
        if len(self.egraphs) != 0:
            return self.egraphs[-1][0].egraph_to_dot()
        else:
            return None
