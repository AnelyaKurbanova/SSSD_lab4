from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse, JSONResponse
import pickle, base64, yaml, os, logging

app = FastAPI()
logging.basicConfig(level=logging.DEBUG)

HARD_CODED_SECRET = "sk_live_SUPERSECRET_123"

DB_CONF = yaml.safe_load(open("config.yml"))

@app.get("/")
async def index():
    return PlainTextResponse("OK - vulnerable app")

@app.get("/crash")
async def crash():
    1 / 0  
    return PlainTextResponse("never")

@app.get("/deserialize")
async def deserialize(data: str = ""):
    """
    Пример опасного эндпоинта.
    Ожидает base64-строку с pickle-данными и делает pickle.loads.
    """
    if not data:
        return JSONResponse({"error": "no data"}, status_code=400)
    try:
        raw = base64.b64decode(data)
        obj = pickle.loads(raw)  
        return JSONResponse({"result": str(obj)})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/show-config")
async def show_config():
    return JSONResponse(DB_CONF)
