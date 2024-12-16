from egraph.EGraph import EGraph
from egraph.AbstractSyntaxTree import AbstractSyntaxTree

class EGraphService:
    def __init__(self):
        """"""
        self.mode = 0  # 0 = normal,  1 = debug
        self.rrc = 0  # rewrite rule counter
        self.dict_of_rules = {}
        self.egraphs = []

    def set_mode(self, mode):
        self.mode = mode

    def add_rule(self, rule):
        self.dict_of_rules[self.rrc] = rule
        self.rrc += 1

    def delete_rule(self, rule):
        self.dict_of_rules.pop(rule)

    def create_egraph(self, expr):
        """"""
        eg = EGraph()
        eterm_id = eg.add_node(AbstractSyntaxTree(expr).root_node)
        self.egraphs.append((eg, eterm_id))

    def get_egraph(self):
        """"""
        return self.egraphs[-1][0].egraph_to_dot()
