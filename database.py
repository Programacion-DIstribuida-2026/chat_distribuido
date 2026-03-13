import aiomysql

DB_CONFIG = {
    "host": "localhost",
    "port": 3380,
    "user": "user",
    "password": "123",
    "db": "chat_db"
}

async def get_connection():
    return await aiomysql.connect(cursorclass=aiomysql.DictCursor, **DB_CONFIG)

async def create_tables():
    conn = await get_connection()
    cursor = await conn.cursor()

    await cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL
        )
    """)

    await cursor.execute("""
        CREATE TABLE IF NOT EXISTS mensajes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            id_usuario INT NOT NULL,
            contenido TEXT NOT NULL,
            fecha_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_usuario) REFERENCES usuarios(id)
        )
    """)

    await conn.commit()
    await cursor.close()
    conn.close()