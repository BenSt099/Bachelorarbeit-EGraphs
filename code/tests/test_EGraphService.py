"""This file contains tests to ensure the capability and correctness of EGraphService.py
The tests are separated into groups to test different aspects of EGraphService.py.

- Number of Tests: 20

"""

import EGraphService

################################################################################
# Validation of Expression              ########################################
################################################################################


def test_valid_expression_1():
    assert EGraphService.is_valid_expression("(<< (* aa (+ 1 ss)) ww)")


def test_valid_expression_2():
    assert not EGraphService.is_valid_expression("(<< a +)")


def test_valid_expression_3():
    assert EGraphService.is_valid_expression("(- b (/ x y))")


def test_valid_expression_4():
    assert EGraphService.is_valid_expression("(>> 7 (* x (/ y aa)))")


def test_valid_expression_5():
    assert EGraphService.is_valid_expression("(/ (* var 23) 2)")


def test_valid_expression_6():
    assert not EGraphService.is_valid_expression("(<< (a aa (+ 1 ss)) ww)")


def test_valid_expression_7():
    assert not EGraphService.is_valid_expression("(<< ")


def test_valid_expression_8():
    assert not EGraphService.is_valid_expression("-- b (/ x y))")


def test_valid_expression_9():
    assert not EGraphService.is_valid_expression("(>> 7 (x * (/ y aa)))")


def test_valid_expression_10():
    assert not EGraphService.is_valid_expression("(/ (* var (- )) 2)")


################################################################################
# General functionality                 ########################################
################################################################################


def test_service_add_rule():
    service = EGraphService.EGraphService()
    result, msg = service.add_rule("(* x 1)", "ii")
    assert result == False


def test_service_get_snapshot():
    service = EGraphService.EGraphService()
    service.create_egraph("(+ a 1)")
    service.add_rule("(* x 1)", "(x)")
    service.add_rule("(* x 2)", "(<< x 1)")
    result = service.get_snapshot()
    assert "'graph': '(+ a 1)'" in str(result)
    assert (
        "'RewriteRules': {0: ['0', '(* x 1)', '(x)'], 1: ['1', '(x)', '(* x 1)'], 2: ['2', '(* x 2)', '(<< x 1)'], 3: ['3', '(<< x 1)', '(* x 2)']}"
        in str(result)
    )


def test_service_set_service():
    service = EGraphService.EGraphService()
    result, msg, data = service.set_session_from_file(dict())
    assert result == False


def test_service_apply():
    service = EGraphService.EGraphService()
    service.create_egraph("(+ a 1)")
    service.add_rule("(+ x 1)", "(x)")
    result, msg = service.apply([0])
    assert result == True


def test_service_add_rewrite_rules_from_file():
    service = EGraphService.EGraphService()
    service.add_rule("(* x 1)", "(x)")
    data = {
        "RewriteRules": {0: ["0", "(* x 1)", "(x)"], 1: ["1", "(* x 2)", "(<< x 1)"]}
    }
    result, msg = service.add_rewrite_rules_from_file(data)
    assert result == True
