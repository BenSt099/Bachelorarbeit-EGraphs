import json
from contextlib import asynccontextmanager
from webbrowser import open_new

from fastapi import FastAPI
from fastapi import Request
from starlette.staticfiles import StaticFiles

from EGraphService import *


@asynccontextmanager
async def lifespan(app: FastAPI):
    open_new(r"http://127.0.0.1:8000")
    yield


app = FastAPI(lifespan=lifespan)
egraphservice = EGraphService()


@app.post("/createegraph")
async def create_egraph(request: Request):
    payload = await request.body()
    pp = json.loads(payload)
    if is_valid_expression(pp["payload"]):
        egraphservice.create_egraph(pp["payload"])
        return {"response": "true"}
    return {"response": "false"}


@app.get("/loadegraph")
def load_egraph():
    a = egraphservice.get_current_egraph()
    if a is None:
        return {"response": "false"}
    else:
        return {"response": "true", "p1": a[0], "p2": a[1]}


@app.post("/addrule")
async def add_rule(request: Request):
    payload = await request.body()
    pp = json.loads(payload)
    c = egraphservice.add_rule(pp["lhs"], pp["rhs"])
    if c is False:
        return {"response": "false"}
    else:
        return {"response": str(c)}


@app.post("/move")
async def move(request: Request):
    """"""
    payload = await request.body()
    pp = json.loads(payload)
    if pp["payload"] == "backward" and pp["p1"] == "false":
        return {"response": "false"}
    elif pp["payload"] == "backward" and pp["p1"] != "false":
        egraphservice.move_backward()
    elif pp["payload"] == "forward" and pp["p1"] == "false":
        return {"response": "false"}
    elif pp["payload"] == "forward" and pp["p1"] != "false":
        egraphservice.move_forward()
    elif pp["payload"] == "fastbackward":
        egraphservice.move_fastbackward()
    elif pp["payload"] == "fastforward":
        egraphservice.move_fastforward()
    else:
        return {"response": "false"}
    return {"response": "true"}


@app.post("/exportegraph")
async def export_egraph(request: Request):
    """"""

    return ""


@app.post("/savetofile")
async def save_egraph(request: Request):
    """"""

    # egraphservice.get_snapshot()

    return {"response": "true"}


@app.post("/loadfromfile")
async def loadfromfile(request: Request):
    """"""
    payload = await request.body()
    pp = json.loads(payload)
    if egraphservice.set_service(json.loads(pp["p1"])):
        return {"response": "true"}
    return {"response": "false"}


@app.post("/applyrule")
async def apply_rule(request: Request):
    """"""
    payload = await request.body()
    pp = json.loads(payload)
    if int(pp["payload"]) in egraphservice.dict_of_rules.keys():
        egraphservice.apply(int(pp["payload"]))
        return {"response": "true"}
    return {"response": "false"}


app.mount("/", StaticFiles(directory="static", html=True), name="static")
