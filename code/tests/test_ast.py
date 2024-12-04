import AbstractSyntaxTree

def test_ast_1():
    ast = AbstractSyntaxTree.AbstractSyntaxTree("(/ (* a 2) 2)")
    assert "(/ (* a 2) 2)" == str(ast)

def test_ast_2():
    ast = AbstractSyntaxTree.AbstractSyntaxTree("(+ a (* a 2) )")
    assert "(+ a (* a 2))" == str(ast)

def test_ast_3():
    ast = AbstractSyntaxTree.AbstractSyntaxTree("(- a (< a 2))")
    assert "(- a (< a 2))" == str(ast)

def test_ast_4():
    ast = AbstractSyntaxTree.AbstractSyntaxTree("(+ a b)")
    assert "(+ a b)" == str(ast)

def test_ast_5():
    ast = AbstractSyntaxTree.AbstractSyntaxTree("(* (> b 2) (/ c 3))")
    assert "(* (> b 2) (/ c 3))" == str(ast)

def test_ast_6():
    ast = AbstractSyntaxTree.AbstractSyntaxTree("(< a (* 2 b))")
    assert "(< a (* 2 b))" == str(ast)

def test_ast_7():
    ast = AbstractSyntaxTree.AbstractSyntaxTree("(* (/ (- a 3) a)(* 2 b))")
    assert "(* (/ (- a 3) a) (* 2 b))" == str(ast)

def test_ast_8():
    ast = AbstractSyntaxTree.AbstractSyntaxTree("(/ x x)")
    assert "(/ x x)" == str(ast)

def test_ast_9():
    ast = AbstractSyntaxTree.AbstractSyntaxTree("(x)")
    assert "(x)" == str(ast)

def test_ast_10():
    ast = AbstractSyntaxTree.AbstractSyntaxTree("(* (> (< 1 (- a 4)) c) (/ (* (+ 2 3) (- 3 4)) 4))")
    assert "(* (> (< 1 (- a 4)) c) (/ (* (+ 2 3) (- 3 4)) 4))" == str(ast)