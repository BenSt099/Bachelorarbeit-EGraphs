"""This file implements a FastAPI server.

Paths:
    - ``/createegraph``: POST
    - ``/loadegraph``: GET
    - ``/addrule``: POST
    - ``/move``: POST
    - ``/applyrule``: POST

Documentation:
    The API documentation is available at: ``http://127.0.0.1:8000/dokumentation.html``

FastAPI:
    FastAPI is used as Backend Server (url: https://fastapi.tiangolo.com/)
"""

from contextlib import asynccontextmanager
from os.path import realpath
from webbrowser import open_new

from fastapi import FastAPI
from fastapi import Request
from starlette.staticfiles import StaticFiles

from EGraphService import *


@asynccontextmanager
async def lifespan(app: FastAPI):
    """This function is needed for FastAPI to open a browser tab with the corresponding
    address. It is executed before anything else.
    """
    open_new(r"http://127.0.0.1:8000")
    yield


app = FastAPI(lifespan=lifespan)
egraphService = EGraphService()


@app.post("/addrule")
async def add_rule(request: Request):
    payload = await request.body()
    pp = json.loads(payload)
    c = egraphService.add_rule(pp["lhs"], pp["rhs"])
    if c is False:
        return {"response": "false"}
    else:
        return {"response": str(c)}


@app.post("/applyrule")
async def apply_rule(request: Request):
    """"""
    payload = await request.body()
    pp = json.loads(payload)
    if int(pp["payload"]) in egraphService.dict_of_rules.keys():
        egraphService.apply(int(pp["payload"]))
        return {"response": "true"}
    return {"response": "false"}


@app.post("/downloadrules")
async def download_rules():
    """"""
    egraphService.save_rr_to_file()
    return {"response": "true"}


@app.post("/uploadrules")
async def upload_rules(request: Request):
    """"""
    payload = await request.body()
    pp = json.loads(payload)
    if egraphService.set_rules(json.loads(pp["p1"])):
        return {"response": "true"}
    return {"response": "false"}


@app.post("/createegraph")
async def create_egraph(request: Request):
    """

    :param request:
    :return: Success of EGraph creation in JSON format
    """
    payload = await request.body()
    pp = json.loads(payload)
    if is_valid_expression(pp["payload"]):
        egraphService.create_egraph(pp["payload"])
        return {"response": "true"}
    return {"response": "false"}


@app.get("/loadegraph")
def load_egraph():
    a = egraphService.get_current_egraph()
    if a is None:
        return {"response": "false"}
    else:
        return {"response": "true", "p1": a[0], "p2": a[1]}


@app.post("/move")
async def move(request: Request):
    """"""
    payload = await request.body()
    pp = json.loads(payload)
    if pp["payload"] == "backward" and pp["p1"] == "false":
        return {"response": "false"}
    elif pp["payload"] == "backward" and pp["p1"] != "false":
        egraphService.move_backward()
    elif pp["payload"] == "forward" and pp["p1"] == "false":
        return {"response": "false"}
    elif pp["payload"] == "forward" and pp["p1"] != "false":
        egraphService.move_forward()
    elif pp["payload"] == "fastbackward":
        egraphService.move_fastbackward()
    elif pp["payload"] == "fastforward":
        egraphService.move_fastforward()
    else:
        return {"response": "false"}
    return {"response": "true"}


@app.post("/extractterm")
async def extract_term(request: Request):
    """"""
    a = egraphService.extract()
    return {"response": str(a)}


@app.post("/exportegraph")
async def export_egraph(request: Request):
    """"""
    payload = await request.body()
    pp = json.loads(payload)
    a, b = egraphService.export(pp["payload"])
    if a:
        return {"response": b}
    return {"response": "false"}


@app.post("/savetofile")
async def save_egraph():
    """"""
    a = egraphService.save_to_file()
    if a:
        return {"response": "true"}
    return {"response": "false"}


@app.post("/loadfromfile")
async def load_from_file(request: Request):
    """"""
    payload = await request.body()
    pp = json.loads(payload)
    if egraphService.set_service(json.loads(pp["p1"])):
        return {"response": "true"}
    return {"response": "false"}


"""
This last line enables the app to access all content in the static/ folder.
Due to issues with testing the above methods, a fix was applied. For more
information, please visit: https://github.com/fastapi/fastapi/issues/3550
"""
app.mount(
    "/",
    StaticFiles(directory=realpath(f"{realpath(__file__)}/../static"), html=True),
    name="static",
)
