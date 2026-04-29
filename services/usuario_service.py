from bson import ObjectId

from database import db


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


async def obtener_usuario(id: str):
    try:
        usuario = await db.usuarios.find_one({"_id": ObjectId(id)})
        if usuario:
            usuario["_id"] = str(usuario["_id"])
        return usuario
    except Exception:
        return None


async def actualizar_usuario(id: str, nombre: str):
    if not ObjectId.is_valid(id):
        raise ValueError("id no es un ObjectId válido de MongoDB.")
    oid = ObjectId(id)
    result = await db.usuarios.update_one({"_id": oid}, {"$set": {"nombre": nombre}})
    if result.matched_count == 0:
        return None
    return await obtener_usuario(id)


async def eliminar_usuario(id: str) -> bool:
    if not ObjectId.is_valid(id):
        return False
    oid = ObjectId(id)
    exists = await db.usuarios.find_one({"_id": oid}, projection={"_id": 1})
    if not exists:
        return False
    await db.mensajes.delete_many(
        {
            "$or": [
                {"remitente_id": id},
                {"destinatario_id": id},
                {"id_usuario": id},
            ]
        }
    )
    await db.usuarios.delete_one({"_id": oid})
    return True
