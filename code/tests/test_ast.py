from AST import *

def test_ast_1():
    ast = AST("(/ (* a 2) 2)")
    assert "/ * a 2 2" == ast.to_string()

def test_ast_2():
    ast2 = AST("(+ a (* a 2) )")
    assert "+ a * a 2" == ast2.to_string()

def test_ast_3():
    ast2 = AST("(- a (< a 2))")
    assert "- a < a 2" == ast2.to_string()

def test_ast_4():
    ast2 = AST("(+ a b)")
    assert "+ a b" == ast2.to_string()

def test_ast_5():
    ast2 = AST("(* (> b 2) (/ c 3))")
    assert "* > b 2 / c 3" == ast2.to_string()

def test_ast_6():
    ast2 = AST("(< a (* 2 b))")
    assert "< a * 2 b" == ast2.to_string()

def test_ast_7():
    ast2 = AST("(* (/ (- a 3) a) (* 2 b))")
    assert "* / - a 3 a * 2 b" == ast2.to_string()