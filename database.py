import os
from motor.motor_asyncio import AsyncIOMotorClient

DEFAULT_MONGO_URL = (
    "mongodb://admin:123@127.0.0.1:37117/?authSource=admin"
)

MONGO_URL = os.environ.get("MONGO_URL", DEFAULT_MONGO_URL)
MONGO_DB_NAME = os.environ.get("MONGO_DB_NAME", "chat_db")

client = AsyncIOMotorClient(MONGO_URL)
db = client[MONGO_DB_NAME]


async def mongo_ping() -> bool:
    try:
        await client.admin.command("ping")
        return True
    except Exception:
        return False


async def create_tables():
    """Verifica MongoDB al iniciar y crea índices."""
    try:
        await client.admin.command("ping")
        print(" MongoDB conectado exitosamente")
    except Exception as e:
        print(f" Error de conexión MongoDB: {e}")
        return

    try:
        await db.mensajes.create_index(
            [("destinatario_id", 1), ("fecha_hora", -1)]
        )
        await db.mensajes.create_index(
            [("remitente_id", 1), ("fecha_hora", -1)]
        )
        await db.mensajes.create_index(
            [("remitente_id", 1), ("destinatario_id", 1), ("_id", -1)]
        )
        await db.mensajes.create_index(
            [("tipo", 1), ("grupo_id", 1), ("_id", -1)]
        )
        await db.grupos.create_index([("creado_por", 1)])
        await db.grupo_miembros.create_index(
            [("grupo_id", 1), ("usuario_id", 1)], unique=True
        )
        await db.grupo_miembros.create_index([("usuario_id", 1)])
    except Exception as e:
        print(f" Aviso: índices: {e}")
