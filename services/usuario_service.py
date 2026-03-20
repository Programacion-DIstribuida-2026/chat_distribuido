from database import get_connection

async def crear_usuario(nombre: str):
    conn = await get_connection()
    cursor = await conn.cursor()
    query = "INSERT INTO usuarios (nombre) VALUES (%s)"
    await cursor.execute(query, (nombre,))
    await conn.commit()
    new_id = cursor.lastrowid
    await cursor.close()
    conn.close()
    return {"id": new_id, "message": "Usuario creado correctamente"}

async def listar_usuarios():
    conn = await get_connection()
    cursor = await conn.cursor()
    query = "SELECT * FROM usuarios"
    await cursor.execute(query)
    usuarios = await cursor.fetchall()
    await cursor.close()
    conn.close()
    return usuarios

async def obtener_usuario(id: int):
    conn = await get_connection()
    cursor = await conn.cursor()
    query = "SELECT * FROM usuarios WHERE id = %s"
    await cursor.execute(query, (id,))
    usuario = await cursor.fetchone()
    await cursor.close()
    conn.close()
    return usuario