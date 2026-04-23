from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
import asyncio
import json
from loguru import logger

from runtime.memory.tag_access import set_tag_by_path, get_tag_by_path

app = FastAPI()

plc = None
clients = set()


def set_plc(plc_instance):
    global plc
    plc = plc_instance

@app.get("/")
def index():
    return FileResponse("web_hmi/hmi.html")

@app.get("/state")
def get_state():
    tags = plc.tags.to_dict()
    state = plc.state

    #logger.info(f"tags: {tags}")
    #logger.info(f"state: {state}")

    return {
        "tags": tags,
        "state": state
    }

# =========================
# REST - READ ALL TAGS
# =========================
@app.get("/tags")
def get_tags():
    return plc.tags.to_dict()


# =========================
# Start PLC
# =========================
@app.post("/plcstate/start")
def start_plc():
    plc.start()
    return {"status": "ok", "message": "PLC started"}

# =========================
# Stop PLC
# =========================
@app.post("/plcstate/stop")
def stop_plc():
    plc.stop()
    return {"status": "ok", "message": "PLC stopped"}

# =========================
# Sim Fail PLC
# =========================
@app.post("/plcstate/simfail")
def simfail_plc():
    plc.fault()
    return {"status": "ok", "message": "PLC fault simulated"}


# =========================
# HMI
# =========================
@app.post("/plc/command")
def plc_command(data: dict):

    cmd = data.get("cmd")
    path = data.get("path")
    value = data.get("value")

    logger.info("cmd: " + str(cmd))
    logger.info("path: " + str(path))
    logger.info("value: " + str(value))

    current = get_tag_by_path(plc.tags, path)

    # =========================
    # SET
    # =========================
    if cmd == "set":
        set_tag_by_path(plc.tags, path, value)

    # =========================
    # TOGGLE
    # =========================
    elif cmd == "toggle":
        set_tag_by_path(plc.tags, path, not current)

    # =========================
    # RESET BOOL
    # =========================
    elif cmd == "resetbool":        
        set_tag_by_path(plc.tags, path, False)
       
    # =========================
    # RESET OTHER
    # =========================
    elif cmd == "resetother":        
        set_tag_by_path(plc.tags, path, 0)        

    else:
        return {
            "status": "error",
            "message": f"Unknown cmd: {cmd}"
        }

    return {
        "status": "ok",
        "cmd": cmd,
        "path": path,
        "value": value
    }

@app.post("/plc/setvalue")
def plc_command(data: dict):
    
    path = data.get("path")
    value = data.get("value")
    
    logger.info("path: " + str(path))
    logger.info("value: " + str(value))

    # =========================
    # SET VALUE
    # =========================       
    set_tag_by_path(plc.tags, path, value)        
    
    return {
        "status": "ok",        
        "path": path,
        "value": value
    }




# =========================
# WEB SOCKET - LIVE HMI
# =========================
@app.websocket("/ws")
async def ws_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.add(websocket)

    try:
        while True:
            await asyncio.sleep(0.2)

            payload = {
                "tags": plc.tags.to_dict(),
                "state": plc.state
            }

            await websocket.send_text(json.dumps(payload))

    except WebSocketDisconnect:
        clients.remove(websocket)