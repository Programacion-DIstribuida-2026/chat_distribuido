import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

from fastapi import FastAPI
from fastapi.responses import FileResponse

from core.realtime_listener import start_redis_listener_task, stop_redis_listener_task
from core.redis_client import connect_redis, disconnect_redis, ping_redis
from database import create_tables, mongo_ping
from routes import chat_ws_router, grupos, mensajes, realtime_ws, usuarios


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    await connect_redis()
    start_redis_listener_task()
    try:
        yield
    finally:
        await stop_redis_listener_task()
        await disconnect_redis()


app = FastAPI(
    title="Chat Distribuido",
    description="API REST y WebSocket. Contrato: `docs/api_contract.md`. Tiempo real: `docs/chat_realtime.md`.",
    lifespan=lifespan,
)

app.include_router(usuarios.router)
app.include_router(grupos.router)
app.include_router(mensajes.router)
app.include_router(chat_ws_router.router)
app.include_router(realtime_ws.router)


@app.get("/")
async def root():
    return {"mensaje": "Bienvenido al Chat Distribuido"}


@app.get("/health")
async def health():
    mongo_ok = await mongo_ping()
    redis_url_set = bool(os.environ.get("REDIS_URL"))
    redis_ok = await ping_redis() if redis_url_set else None
    return {
        "mongodb": "ok" if mongo_ok else "error",
        "redis": (
            "ok"
            if redis_ok is True
            else ("disabled" if redis_ok is None else "error")
        ),
    }


@app.get("/chat")
async def chat_page():
    return FileResponse("static/chat.html")
