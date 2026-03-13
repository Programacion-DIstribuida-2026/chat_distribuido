from fastapi import FastAPI
from contextlib import asynccontextmanager
from database import create_tables
from routes import usuarios, mensajes

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield

app = FastAPI(title="Chat Distribuido", lifespan=lifespan)

app.include_router(usuarios.router)
app.include_router(mensajes.router)

@app.get("/")
async def root():
    return {"mensaje": "Bienvenido al Chat Distribuido"}