from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import PlainTextResponse, JSONResponse
from pydantic import BaseModel, BaseSettings, ValidationError
from dotenv import load_dotenv
import logging
import os

load_dotenv() 

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sssd_lab4")

class Settings(BaseSettings):
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 5432
    DATABASE_USER: str = "appuser"
    DATABASE_PASSWORD: str
    SECRET_KEY: str
    API_KEY: str | None = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

try:
    settings = Settings()
except ValidationError as e:
    logger.error("Settings validation error: %s", e)
    raise

app = FastAPI(title="SSSD Lab4 - fixed")

@app.get("/")
async def index():
    return PlainTextResponse("OK - fixed app")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception")
    return JSONResponse({"error": "Internal Server Error"}, status_code=500)

@app.get("/show-config-safe")
async def show_config_safe():
    return {
        "database_host": settings.DATABASE_HOST,
        "database_port": settings.DATABASE_PORT,
        "database_user": settings.DATABASE_USER,
    
    }

class Payload(BaseModel):
    name: str
    amount: int

@app.post("/safe-accept")
async def safe_accept(payload: Payload):
    return {"result": payload.dict()}

def require_api_key(request: Request):
    api_key = settings.API_KEY
    if not api_key:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="API key not configured")
    key = request.headers.get("x-api-key")
    if key != api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")

@app.get("/admin/show-config")
async def admin_show_config(request: Request):
    require_api_key(request)
    return await show_config_safe()
