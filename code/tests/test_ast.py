from AST import *

def test_ast():
    ast = process("(/ (* a 2) 2)")
    ast_str = to_string(ast)
    assert ast_str == "/ * a 2 2"

def test_ast_2():
    ast2 = process("(+ a (* a 2) )")
    ast_str2 = to_string(ast2)
    assert ast_str2 == "+ a * a 2"