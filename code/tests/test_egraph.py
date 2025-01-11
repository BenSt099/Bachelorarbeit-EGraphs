import AbstractSyntaxTree
import EGraph
import RewriteRule


def test_egraph_1():
    ast = AbstractSyntaxTree.AbstractSyntaxTree("(/ (* a 2) 2)")
    g = EGraph.EGraph()
    g.add_node(ast.root_node)
    assert len(g.u.subsets()) == 4


def test_egraph_2():
    ast = AbstractSyntaxTree.AbstractSyntaxTree("(/ (* a 2) 2)")
    ast2 = AbstractSyntaxTree.AbstractSyntaxTree("(* a 2)")
    ast3 = AbstractSyntaxTree.AbstractSyntaxTree("(<< a 2)")
    g = EGraph.EGraph()
    g.add_node(ast.root_node)
    id1 = g.add_node(ast2.root_node)
    id2 = g.add_node(ast3.root_node)
    g.merge(id1, id2)
    g.rebuild()
    assert g._find(id1) == g._find(id2)


def test_egraph_3():
    ast = AbstractSyntaxTree.AbstractSyntaxTree("(/ (* a 2) 2)")
    g = EGraph.EGraph()
    g.add_node(ast.root_node)
    eclasses = g.get_eclasses()
    r = RewriteRule.RewriteRule("reassociate", "(/ (* x y) z)", "(* x (/ y z))")
    list_of_matches = g._ematch(eclasses, r.expr_lhs.root_node)
    print(list_of_matches[0][1].keys())
    assert (
        "x" in list_of_matches[0][1].keys()
        and "y" in list_of_matches[0][1].keys()
        and "z" in list_of_matches[0][1].keys()
    )


def test_egraph_4():
    ast = AbstractSyntaxTree.AbstractSyntaxTree("(+ a 2)")
    g = EGraph.EGraph()
    g.add_node(ast.root_node)
    eclasses = g.get_eclasses()
    r = RewriteRule.RewriteRule("switch", "(+ x y)", "(+ y x)")
    list_of_matches = g._ematch(eclasses, r.expr_lhs.root_node)
    print(list_of_matches[0][1].keys())
    assert "x" in list_of_matches[0][1].keys() and "y" in list_of_matches[0][1].keys()
