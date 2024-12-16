from fastapi import FastAPI
from fastapi import Request
# from fastapi import Response
from starlette.staticfiles import StaticFiles
import json
from services.EGraphService import *


app = FastAPI()

egraphservice = EGraphService()


@app.post("/createegraph")
async def create_egraph(request: Request):
    payload = await request.body()
    pp = json.loads(payload)
    # print(pp)
    egraphservice.create_egraph(pp['payload'])
    return {"response": "true"}

@app.post("/loadegraph")
async def load_egraph(request: Request):
    a = egraphservice.get_egraph()
    return {"response": a}

@app.post("/addrule")
async def add_rule():
    return ""

app.mount("/", StaticFiles(directory="static", html=True), name="static")
