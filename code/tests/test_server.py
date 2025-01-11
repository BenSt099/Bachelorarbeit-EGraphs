"""This file includes multiple tests for making sure the server operates properly.

"""

from fastapi.testclient import TestClient
from server import app

def test_load_egraph():
    """"""
    client = TestClient(app)
    response = client.get("/loadegraph")
    assert response.status_code == 200

