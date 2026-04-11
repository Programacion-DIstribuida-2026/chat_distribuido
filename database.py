# database.py
import os
from motor.motor_asyncio import AsyncIOMotorClient

# Esta es la IP que SI funcionará desde WSL hacia tu Docker de Windows
MONGO_URL = "mongodb://admin:123@172.24.224.1:27017"

client = AsyncIOMotorClient(MONGO_URL)
db = client.chat_db

async def create_tables():
    """Verifica la conexión al iniciar la API"""
    try:
        await client.admin.command('ping')
        print(" MongoDB conectado exitosamente")
    except Exception as e:
        print(f" Error de conexión: {e}")