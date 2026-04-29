# Contexto operacional

Guía breve para desarrollar y operar **Chat Distribuido** en local o en servidores de prueba.

## Variables de entorno

| Variable | Obligatoriedad | Descripción |
|----------|------------------|-------------|
| `MONGO_URL` | Recomendada | URI MongoDB (ver `.env.example`; puerto alineado con `MONGO_HOST_PORT` del compose). |
| `MONGO_HOST_PORT` | Solo Docker Compose | Puerto publicado en el host para Mongo (default **37117** en `docker-compose.yml`). |
| `MONGO_DB_NAME` | Opcional | Nombre de la base de datos (default `chat_db`). Los tests (`pytest`) fijan `chat_test` en `tests/conftest.py` para no mezclar datos con desarrollo. |
| `REDIS_URL` | **Recomendada en producción** | Sin ella, `/health` marca `redis: disabled` y el **Pub/Sub entre instancias de Uvicorn no funciona**; el tiempo real queda limitado a un solo proceso. |

## Arranque típico (local)

1. `docker compose up -d` (MongoDB, Redis, mongo-express).
2. Entorno virtual e `pip install -r requirements.txt`.
3. Copiar `.env.example` a `.env`. El compose usa `MONGO_HOST_PORT` (default **37117**); `MONGO_URL` debe usar ese mismo puerto en el host.
4. `uvicorn main:app --host 0.0.0.0 --port 9000 --reload`.

## Multi-instancia (Pub/Sub)

Para probar fan-out entre workers:

```bash
# Terminal 1
REDIS_URL=redis://127.0.0.1:6379/0 uvicorn main:app --port 9000

# Terminal 2
REDIS_URL=redis://127.0.0.1:6379/0 uvicorn main:app --port 9001
```

Los clientes deben conectarse al puerto correspondiente; Redis debe ser **compartido** por ambos procesos.

## Troubleshooting

| Síntoma | Causa probable |
|---------|----------------|
| WebSocket sin eventos cruzados entre puertos | `REDIS_URL` no definida o Redis caído. |
| `session:auth` rechazado | `user_id` no es un ObjectId válido de 24 hex. |
| `group:join` falla | Usuario no está en `grupo_miembros`. |
| Mongo “error” en `/health` | Credenciales o red; revisar `MONGO_URL` y que el contenedor escuche en el host correcto (WSL/Docker Desktop). |
| Docker: `ports are not available` / `expose returned unexpected status: 500` | Suele ser el proxy de puertos de **Docker Desktop** (WSL2), no solo ocupación. Prueba: otro `MONGO_HOST_PORT` en `.env`, `docker compose down --remove-orphans`, reiniciar Docker Desktop o `wsl --shutdown` y volver a abrir. |

## Enlaces

- [chat_realtime.md](chat_realtime.md) — diseño de salas y Redis.
- [api_contract.md](api_contract.md) — rutas REST y WebSockets.
