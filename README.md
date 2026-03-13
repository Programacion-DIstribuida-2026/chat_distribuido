# Chat distribuido (Grupo 1)

API en **Python + FastAPI** para un chat centralizado tipo “servidor de sala”.

## Requisitos (según entrega)
- **POST `/usuarios`**
- **GET `/usuarios`**
- **POST `/mensajes`**
- **GET `/mensajes`**

Incluye también:
- **GET `/usuarios/{id}`**
- **GET `/mensajes/{id_usuario}`**

## Configuración
La conexión a MySQL se configura en `database.py` (por defecto):
- host: `localhost`
- port: `3380`
- user: `user`
- password: `123`
- db: `chat_db`

## Instalación

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Ejecución

```bash
uvicorn main:app --reload
```

Al iniciar, la app crea las tablas `usuarios` y `mensajes` si no existen.

## Evidencia rápida (ejemplos)

Crear usuario:

```bash
curl -X POST "http://127.0.0.1:8000/usuarios" ^
  -H "Content-Type: application/json" ^
  -d "{\"nombre\":\"Kevin\"}"
```

Enviar mensaje:

```bash
curl -X POST "http://127.0.0.1:8000/mensajes" ^
  -H "Content-Type: application/json" ^
  -d "{\"id_usuario\":1,\"contenido\":\"Hola\"}"
```

Listar mensajes:

```bash
curl "http://127.0.0.1:8000/mensajes"
```
