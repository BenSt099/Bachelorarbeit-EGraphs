import AST


class RewriteRule:
    def __init__(self, name, expr1, expr2):
        self.name = name
        self.expr_lhs = AST.AST(expr1)
        self.expr_rhs = AST.AST(expr2)

    def to_string(self):
        return (
            f"[{self.name}: {self.expr_lhs.to_string()} => {self.expr_rhs.to_string()}]"
        )
