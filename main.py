from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from database import create_tables
from routes import usuarios, mensajes, chat_ws_router

STATIC_DIR = Path(__file__).resolve().parent / "static"

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield

app = FastAPI(title="Chat Distribuido", lifespan=lifespan)

app.include_router(usuarios.router)
app.include_router(mensajes.router)
app.include_router(chat_ws_router.router)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/chat", include_in_schema=False)
async def chat_page():
    return FileResponse(STATIC_DIR / "chat.html")

@app.get("/")
async def root():
    return {
        "mensaje": "Bienvenido al Chat Distribuido",
        "chat_ui": "/chat",
        "docs": "/docs",
    }