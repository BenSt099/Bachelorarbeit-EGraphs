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
from json import JSONDecodeError
from os.path import realpath
from webbrowser import open_new

from fastapi import FastAPI
from fastapi import Request
from starlette.staticfiles import StaticFiles

from EGraphService import *


@asynccontextmanager
async def lifespan(app: FastAPI):
    """This function is needed for FastAPI to open a browser tab with the
    corresponding address. It is executed before anything else.
    """
    open_new(r"http://127.0.0.1:8000")
    yield


app = FastAPI(lifespan=lifespan)
egraphService = EGraphService()


@app.get("/getrules")
def get_rules():
    """Returns all rules.

    :return:
    """
    result, msg, data = egraphService.get_all_rules()
    return {"response": str(result), "msg": msg, "payload": data}


@app.post("/addrule")
async def add_rule(request: Request):
    """Adds a new rule.

    :param request:
    :return:
    """
    payload = await request.body()
    pp = json.loads(payload)
    result, msg, data = egraphService.add_rule(pp["lhs"], pp["rhs"])
    return {"response": str(result), "msg": msg, "payload": data}


@app.post("/applyrule")
async def apply_rule(request: Request):
    """Applies rule.

    :param request:
    :return:
    """
    payload = await request.body()
    pp = json.loads(payload)
    result, msg = egraphService.apply(pp["payload"])
    return {"response": str(result), "msg": msg}


@app.post("/applyallrandomly")
async def apply_rule():
    """Apply all rules

    :param request:
    :return:
    """
    result, msg = egraphService.apply_all_rules_randomly()
    return {"response": str(result), "msg": msg}


@app.post("/downloadrules")
async def download_rules():
    """Save rewrite rules in a JSON file.

    :return: {"response": result, "msg": msg}
    """
    result, msg = egraphService.save_rewrite_rules_to_file()
    return {"response": str(result), "msg": msg}


@app.post("/uploadrules")
async def upload_rules(request: Request):
    """Processes the uploaded rules.

    :param request: JSON string with rules.
    :return:
    """
    payload = await request.body()
    try:
        pp = json.loads(payload)
    except JSONDecodeError:
        return {"response": "False", "msg": "Failed to decode JSON."}
    result, msg = egraphService.add_rewrite_rules_from_file(json.loads(pp["payload"]))
    return {"response": str(result), "msg": msg}


@app.post("/createegraph")
async def create_egraph(request: Request):
    """

    :param request:
    :return: Success of EGraph creation in JSON format
    """
    payload = await request.body()
    pp = json.loads(payload)
    result, msg = egraphService.create_egraph(pp["payload"])
    return {"response": str(result), "msg": msg}


@app.get("/loadegraph")
def load_egraph():
    """Returns the currently selected EGraph.

    :return:
    """
    result, msg, data = egraphService.get_current_egraph()
    return {
        "response": str(result),
        "msg": msg,
        "payload1": data[0],
        "payload2": data[1],
    }


@app.post("/move")
async def move(request: Request):
    """Moves in debug information.

    :param request:
    :return:
    """
    payload = await request.body()
    pp = json.loads(payload)
    if pp["payload"] == "backward" and pp["debugModeEnabled"] == "false":
        return {
            "response": "False",
            "msg": "Could NOT load debug output - switch from standard to debug mode?",
        }
    elif pp["payload"] == "backward" and pp["debugModeEnabled"] != "false":
        egraphService.move_backward()
    elif pp["payload"] == "forward" and pp["debugModeEnabled"] == "false":
        return {
            "response": "False",
            "msg": "Could NOT load debug output - switch from standard to debug mode?",
        }
    elif pp["payload"] == "forward" and pp["debugModeEnabled"] != "false":
        egraphService.move_forward()
    elif pp["payload"] == "fastbackward":
        egraphService.move_fastbackward()
    elif pp["payload"] == "fastforward":
        egraphService.move_fastforward()
    else:
        return {"response": "False", "msg": "Failed to move."}
    return {"response": "True", "msg": pp["payload"] + "."}


@app.post("/extractterm")
async def extract_term():
    """

    :param request:
    :return:
    """
    result, msg, data = egraphService.extract()
    return {"response": str(result), "msg": msg, "payload": data}


@app.post("/exportegraph")
async def export_egraph(request: Request):
    """Exports current EGraph into one format.

    :param request:
    :return:
    """
    payload = await request.body()
    pp = json.loads(payload)
    result, msg = egraphService.export(pp["payload"])
    return {"response": str(result), "msg": msg}


@app.post("/savetofile")
async def download_session():
    """Saves the current session to a file.

    :return:
    """
    result, msg = egraphService.save_to_file()
    return {"response": str(result), "msg": msg}


@app.post("/loadfromfile")
async def upload_session(request: Request):
    """Processes the uploaded session file.

    :param request:
    :return:
    """
    payload = await request.body()
    pp = json.loads(payload)
    result, msg = egraphService.set_service(json.loads(pp["payload"]))
    return {"response": str(result), "msg": msg}


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
