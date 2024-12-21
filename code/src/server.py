import json
from webbrowser import open_new
from fastapi import FastAPI
from fastapi import Request
from starlette.staticfiles import StaticFiles
from services.EGraphService import *
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
    a = egraphservice.get_egraph()
    if a is not None:
        return {"response": a}
    else:
        return {"response": "false"}


@app.post("/addrule")
async def add_rule(request: Request):
    payload = await request.body()
    pp = json.loads(payload)
    # print(pp)
    print(pp["payload1"])
    print(pp["payload2"])
    # egraphservice.add_rule()
    return {"response": "true"}


@app.get("/getrules")
async def getrules():
    """"""
    # egraphservice.get_rules()
    return ""


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


app.mount("/", StaticFiles(directory="static", html=True), name="static")
