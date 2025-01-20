"""This file includes multiple tests for making sure the server operates properly.

"""

from fastapi.testclient import TestClient
from server import app


def test_create_egraph_1():
    """"""
    client = TestClient(app)
    response = client.post("/createegraph", json={"payload": "(+ x 1)"})
    assert response.json() == {"response": "True", "msg": "Created EGraph."}


def test_create_egraph_2():
    """"""
    client = TestClient(app)
    response = client.post("/createegraph", json={"payload": "+ x 1)"})
    assert "'response': 'False'" in str(response.json())


def test_load_egraph_1():
    """"""
    client = TestClient(app)
    response = client.get("/loadegraph")
    assert response.status_code == 200


def test_load_egraph_2():
    """"""
    client = TestClient(app)
    client.post("/createegraph", json={"payload": "(+ x 1)"})
    response = client.get("/loadegraph")
    assert "'msg': 'EGraph loaded.'" in str(response.json())


def test_move_1():
    """"""
    client = TestClient(app)
    client.post("/createegraph", json={"payload": "(* x 1)"})
    response = client.post(
        "/move", json={"payload": "forward", "debugModeEnabled": "false"}
    )
    assert "'response': 'False'" in str(response.json())


def test_add_rule():
    """"""
    client = TestClient(app)
    client.post("/createegraph", json={"payload": "(+ x 1)"})
    response = client.post("/addrule", json={"lhs": "(* x 1)", "rhs": "(x)"})
    assert "'response': 'True'" in str(response.json())
    assert "'payload': 0" in str(response.json())


def test_apply_rule_1():
    """"""
    client = TestClient(app)
    client.post("/createegraph", json={"payload": "(+ x 1)"})
    client.post("/addrule", json={"lhs": "(* x 1)", "rhs": "(x)"})
    response = client.post("/applyrule", json={"payload": "0"})
    assert "'response': 'True'" in str(response.json())


def test_apply_rule_2():
    """"""
    client = TestClient(app)
    client.post("/createegraph", json={"payload": "(+ x 1)"})
    client.post("/addrule", json={"lhs": "(* x 1)", "rhs": "(x)"})
    client.post("/addrule", json={"lhs": "(* y 1)", "rhs": "(y)"})
    response = client.post("/applyrule", json={"payload": "1"})
    assert "'response': 'True'" in str(response.json())


def test_get_rules_1():
    """"""
    client = TestClient(app)
    client.post("/createegraph", json={"payload": "(+ x 1)"})
    client.post("/addrule", json={"lhs": "(* x 1)", "rhs": "(x)"})
    response = client.get("/getrules")
    assert "'response': 'True'" in str(response.json())
    assert "['0', '(* x 1)', '(x)']" in str(response.json())


def test_get_rules_2():
    """"""
    client = TestClient(app)
    client.post("/createegraph", json={"payload": "(+ x 1)"})
    client.post("/addrule", json={"lhs": "(* x 1)", "rhs": "(x)"})
    client.post("/addrule", json={"lhs": "(* y 1)", "rhs": "(y)"})
    response = client.get("/getrules")
    assert "'response': 'True'" in str(response.json())
    assert "['0', '(* x 1)', '(x)']" in str(response.json())
    assert "['1', '(* y 1)', '(y)']" in str(response.json())
