from AST import *

def test_ast():
    ast = AST("(/ (* a 2) 2)")
    assert "/ * a 2 2" == ast.to_string()

def test_ast_2():
    ast2 = AST("(+ a (* a 2) )")
    assert "+ a * a 2" == ast2.to_string()