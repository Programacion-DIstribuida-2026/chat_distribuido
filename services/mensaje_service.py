from database import get_connection

async def enviar_mensaje(id_usuario: int, contenido: str):
    conn = await get_connection()
    cursor = await conn.cursor()
    
    query = "INSERT INTO mensajes (id_usuario, contenido) VALUES (%s, %s)"
    await cursor.execute(query, (id_usuario, contenido))
    
    await conn.commit()
    await cursor.close()
    conn.close()
    return {"mensaje": "Mensaje enviado correctamente"}

async def listar_mensajes():
    conn = await get_connection()
    cursor = await conn.cursor()
    
    query = "SELECT * FROM mensajes"
    await cursor.execute(query)
    mensajes = await cursor.fetchall()
    
    await cursor.close()
    conn.close()
    return mensajes

async def mensajes_por_usuario(id_usuario: int):
    conn = await get_connection()
    cursor = await conn.cursor()
    
    query = "SELECT * FROM mensajes WHERE id_usuario = %s"
    await cursor.execute(query, (id_usuario,))
    mensajes = await cursor.fetchall()
    
    await cursor.close()
    conn.close()
    return mensajes