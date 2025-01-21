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
    assert "x" in list_of_matches[0][1].keys() and "y" in list_of_matches[0][1].keys()


def test_egraph_5():
    ast = AbstractSyntaxTree.AbstractSyntaxTree("(/ (* a 2) 2)")
    g = EGraph.EGraph()
    etermid = g.add_node(ast.root_node)
    rules = [
        RewriteRule.RewriteRule("reassociate", "(/ (* x y) z)", "(* x (/ y z))"),
        RewriteRule.RewriteRule("shift", "(* x 2)", "(<< x 1)"),
        RewriteRule.RewriteRule("simplify", "(/ x x)", "(1)"),
        RewriteRule.RewriteRule("simp", "(* x 1)", "(x)"),
    ]
    egraph, dbg, best = EGraph.equality_saturation(rules, etermid, g)
    assert best == "a"


def test_egraph_6():
    ast = AbstractSyntaxTree.AbstractSyntaxTree("(* a 1)")
    g = EGraph.EGraph()
    etermid = g.add_node(ast.root_node)
    rules = [RewriteRule.RewriteRule("simp", "(* x 1)", "(x)")]
    egraph, dbg, best = EGraph.equality_saturation(rules, etermid, g)
    assert best == "a"


def test_egraph_7():
    ast = AbstractSyntaxTree.AbstractSyntaxTree("(* a 2)")
    g = EGraph.EGraph()
    etermid = g.add_node(ast.root_node)
    rules = [
        RewriteRule.RewriteRule("reassociate", "(/ (* x y) z)", "(* x (/ y z))"),
        RewriteRule.RewriteRule("shift", "(* x 2)", "(<< x 1)"),
        RewriteRule.RewriteRule("simplify", "(/ x x)", "(1)"),
        RewriteRule.RewriteRule("simp", "(* x 1)", "(x)"),
    ]
    egraph, dbg, best = EGraph.equality_saturation(rules, etermid, g)
    assert best == "(<< a 1)"


def test_egraph_8():
    ast = AbstractSyntaxTree.AbstractSyntaxTree("(* a 2)")
    g = EGraph.EGraph()
    etermid = g.add_node(ast.root_node)
    rules = [
        RewriteRule.RewriteRule("reassociate", "(/ (* x y) z)", "(* x (/ y z))"),
        RewriteRule.RewriteRule("shift", "(* x 2)", "(<< x 1)"),
        RewriteRule.RewriteRule("simplify", "(/ x x)", "(1)"),
        RewriteRule.RewriteRule("simp", "(* x 1)", "(x)"),
    ]
    g, dbg, best = EGraph.equality_saturation(rules, etermid, g)
    egraph, dbg, best = EGraph.equality_saturation(rules, etermid, g)
    assert best == "(<< a 1)"


def test_egraph_9():
    ast = AbstractSyntaxTree.AbstractSyntaxTree("(+ a 2)")
    g = EGraph.EGraph()
    g.add_node(ast.root_node)
    eclasses = g.get_eclasses()
    rule = RewriteRule.RewriteRule("switch", "(+ x y)", "(+ y x)")
    list_of_matches = g._ematch(eclasses, rule.expr_lhs.root_node)
    eclass_id, environment = list_of_matches[0]
    new_eclass_id = g._substitute(rule.expr_rhs.root_node, environment)
    assert g._find(new_eclass_id)


def test_egraph_10():
    ast = AbstractSyntaxTree.AbstractSyntaxTree("(+ a 2)")
    g = EGraph.EGraph()
    etermid = g.add_node(ast.root_node)
    assert "(+ a 2)" == EGraph._extract_term(etermid, g)
