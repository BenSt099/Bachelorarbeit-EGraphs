import AbstractSyntaxTree
import EGraph

def test_egraph_1():
    ast = AbstractSyntaxTree.AbstractSyntaxTree("(/ (* a 2) 2)")
    g = EGraph.EGraph()
    g.add_node(ast.root_node)
    assert len(g.u.subsets()) == 4

def test_egraph_2():
    ast = AbstractSyntaxTree.AbstractSyntaxTree("(/ (* a 2) 2)")
    ast2 = AbstractSyntaxTree.AbstractSyntaxTree("(* a 2)")
    ast3 = AbstractSyntaxTree.AbstractSyntaxTree("(< a 2)")
    g = EGraph.EGraph()
    g.add_node(ast.root_node)
    id1 = g.add_node(ast2.root_node)
    id2 = g.add_node(ast3.root_node)
    g.merge(id1, id2)
    g.rebuild()
    assert g._find(id1) == g._find(id2)