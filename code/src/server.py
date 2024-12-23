import json
from webbrowser import open_new
from fastapi import FastAPI
from fastapi import Request
from starlette.staticfiles import StaticFiles
from EGraphService import *
from contextlib import asynccontextmanager


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
    if egraphservice.egraph is None:
        return {"response": "false"}
    a = egraphservice.egraph[0].egraph_to_dot()
    if a is not None:
        return {"response": a}
    else:
        return {"response": "false"}


@app.post("/addrule")
async def add_rule(request: Request):
    payload = await request.body()
    pp = json.loads(payload)
    c = egraphservice.add_rule(pp["lhs"], pp["rhs"])
    if c is False:
        return {"response": "false"}
    else:
        return {"response": str(c)}


@app.post("/exportegraph")
async def export_egraph(request: Request):
    """"""

    return ""


@app.post("/savetofile")
async def save_egraph(request: Request):
    """"""

    return ""


@app.post("/loadfromfile")
async def loadfromfile(request: Request):
    """"""

    return ""


@app.post("/applyrule")
async def apply_rule(request: Request):
    """"""
    payload = await request.body()
    pp = json.loads(payload)
    if int(pp["payload"]) in egraphservice.dict_of_rules.keys():
        return {"response": "true"}
    return {"response": "false"}


app.mount("/", StaticFiles(directory="static", html=True), name="static")
