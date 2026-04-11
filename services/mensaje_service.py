from database import db
from bson import ObjectId
from datetime import datetime

async def enviar_mensaje(id_usuario: str, contenido: str):
    # En MongoDB creamos un documento con la fecha actual
    nuevo_mensaje = {
        "id_usuario": id_usuario,
        "contenido": contenido,
        "fecha_hora": datetime.utcnow()
    }
    result = await db.mensajes.insert_one(nuevo_mensaje)
    return {"message": "Mensaje enviado", "id": str(result.inserted_id)}

async def listar_mensajes():
    mensajes = []
    # Usamos .sort() para traer los más recientes primero
    cursor = db.mensajes.find().sort("fecha_hora", -1)
    async for msg in cursor:
        msg["_id"] = str(msg["_id"])
        mensajes.append(msg)
    return mensajes

async def mensajes_por_usuario(id_usuario: str):
    mensajes = []
    cursor = db.mensajes.find({"id_usuario": id_usuario})
    async for msg in cursor:
        msg["_id"] = str(msg["_id"])
        mensajes.append(msg)
    return mensajes