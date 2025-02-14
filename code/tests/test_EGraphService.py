"""This file contains tests to ensure the capability and correctness of EGraphService.py
The tests are separated into groups to test different aspects of EGraphService.py.

- Number of Tests: 20

"""

import EGraphService
import pytest


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

"""The test below this comment will create a pdf file in the current directory.
Therefore, it requires manual execution.
"""


def test_service_general_1():
    service = EGraphService.EGraphService()
    service.create_egraph("(* 0 (* (+ a (* a 2)) 1))")
    service.add_rule("(<< x 1)", "(* x 2)")
    _, _, term = service.extract()
    assert term == "(* 0 (* (+ a (<< a 1)) 1))"


################################################################################
# Export e-graph                        ########################################
################################################################################


@pytest.mark.skip(
    reason="Run this test manually. For more information, read comment above method <test_service_export>."
)
def test_service_export():
    service = EGraphService.EGraphService()
    service.create_egraph("(* 0 (* (+ a (* a 2)) 1))")
    service.export("pdf")
    assert True


################################################################################
# Add rule                              ########################################
################################################################################


def test_service_add_rule_1():
    service = EGraphService.EGraphService()
    result, msg = service.add_rule("(* x 1)", "ii")
    assert result == False


def test_service_add_rule_2():
    service = EGraphService.EGraphService()
    service.add_rule("(+ x y)", "(+ y x)")
    rule = "(+ x y)" + " => " + "(+ y x)"
    rule_reversed = "(+ y x)" + " => " + "(+ x y)"
    rules_str = [
        str(rule.expr_lhs) + " => " + str(rule.expr_rhs)
        for rule in service.dict_of_rules.values()
    ]
    assert rule in rules_str
    assert rule_reversed in rules_str


def test_service_add_rule_3():
    service = EGraphService.EGraphService()
    service.add_rule("(* x 1)", "(x)")
    service.add_rule("(* x 1)", "(x)")
    assert len(service.dict_of_rules) == 2


################################################################################
# Apply rule                            ########################################
################################################################################


def test_service_apply_1():
    service = EGraphService.EGraphService()
    service.create_egraph("(+ a 1)")
    service.add_rule("(+ x 1)", "(x)")
    result, msg = service.apply([0])
    assert result == True


def test_service_apply_2():
    service = EGraphService.EGraphService()
    service.create_egraph("(+ a 1)")
    service.add_rule("(+ x 1)", "(x)")
    result, msg = service.apply([0, 1])
    assert msg == "Applied rule(s): 0, 1"


################################################################################
# Add rules from file                   ########################################
################################################################################


def test_service_add_rewrite_rules_from_file():
    service = EGraphService.EGraphService()
    service.add_rule("(* x 1)", "(x)")
    data = {
        "RewriteRules": {0: ["0", "(* x 1)", "(x)"], 1: ["1", "(* x 2)", "(<< x 1)"]}
    }
    result, msg = service.add_rewrite_rules_from_file(data)
    assert result == True


################################################################################
# Get snapshot                          ########################################
################################################################################


def test_service_get_snapshot_1():
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


def test_service_get_snapshot_2():
    service = EGraphService.EGraphService()
    service.create_egraph("(* a 1)")
    service.add_rule("(* x 1)", "(x)")
    service.add_rule("(* x 2)", "(<< x 1)")
    service.apply([0, 1, 2, 3])
    result = service.get_snapshot()
    assert "'optimalTerm': 'a'" in str(result)


################################################################################
# Set service                           ########################################
################################################################################


def test_service_set_service_1():
    service = EGraphService.EGraphService()
    result, msg = service.set_session_from_file(dict())
    assert result == False


def test_service_set_service_2():
    service = EGraphService.EGraphService()
    result, msg = service.set_session_from_file(
        dict(
            {
                "RewriteRules": {
                    "0": ["0", "(* x 2)", "(<< x 1)"],
                    "1": ["1", "(/ x x)", "(1)"],
                },
                "Applied": ["0"],
                "graph": "(+ a (* a 2))",
                "optimalTerm": "",
            }
        )
    )
    assert result == True


################################################################################
# Move                                  ########################################
################################################################################


def test_service_move_forward_1():
    service = EGraphService.EGraphService()
    service.create_egraph("(+ a 1)")
    service.add_rule("(+ x 1)", "(x)")
    service.apply([0, 1])
    service.move_fastforward()
    service.move_forward()
    _, _, eg = service.get_current_egraph()
    assert eg != (None, None)


def test_service_move_forward_2():
    service = EGraphService.EGraphService()
    service.move_forward()
    _, _, eg = service.get_current_egraph()
    assert eg == (None, None)


def test_service_move_backward_1():
    service = EGraphService.EGraphService()
    service.create_egraph("(+ a 1)")
    service.add_rule("(+ x 1)", "(x)")
    service.apply([0, 1])
    service.move_fastbackward()
    service.move_fastbackward()
    service.move_fastbackward()
    service.move_backward()
    dbg = service.egraphs[service.current_major][service.current_minor]
    assert dbg[0] == "EGraph created."


def test_service_move_backward_2():
    service = EGraphService.EGraphService()
    service.create_egraph("(+ a 1)")
    service.add_rule("(+ x 1)", "(x)")
    service.apply([0, 1])
    major = service.current_major
    minor = service.current_minor
    service.move_forward()
    service.move_backward()
    assert service.current_major == major and service.current_minor == minor
