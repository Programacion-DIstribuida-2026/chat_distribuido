from database import db
from bson import ObjectId # <--- ESTO es lo que traduce los IDs de Mongo

async def crear_usuario(nombre: str):
    usuario = {"nombre": nombre}
    result = await db.usuarios.insert_one(usuario)
    return {"id": str(result.inserted_id), "nombre": nombre}

async def listar_usuarios():
    usuarios = []
    async for user in db.usuarios.find():
        user["_id"] = str(user["_id"])
        usuarios.append(user)
    return usuarios

# ESTA ES LA FUNCIÓN QUE CAUSABA EL ERROR DE UVICORN
async def obtener_usuario(id: str):
    try:
        # Convertimos el string en un objeto BSON para buscarlo
        usuario = await db.usuarios.find_one({"_id": ObjectId(id)})
        if usuario:
            usuario["_id"] = str(usuario["_id"])
        return usuario
    except Exception:
        return None