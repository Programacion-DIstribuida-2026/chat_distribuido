# Chat Distribuido

API REST y WebSocket para un chat con enfoque en datos mínimos, construida con **FastAPI**, **MongoDB** (Motor) y **Redis** (conexión opcional para healthcheck y extensiones futuras).

## Requisitos

- Python 3.12+
- Docker (recomendado) para MongoDB, Redis y mongo-express

## Puesta en marcha

### 1. Clonar e instalar

```bash
git clone https://github.com/Programacion-Distribuida-2026/chat_distribuido.git
cd chat_distribuido
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Variables de entorno

Copia `.env.example` a `.env` y ajusta URLs si tu red es distinta:

| Variable     | Descripción |
|-------------|-------------|
| `MONGO_URL` | URI de MongoDB (por defecto `127.0.0.1:37117`; usuario `admin` / `123`, `authSource=admin`). Debe usar el mismo puerto que `MONGO_HOST_PORT` del compose. |
| `MONGO_HOST_PORT` | Solo para **Docker Compose**: puerto en el host donde se publica Mongo (default **37117**). Si al hacer `docker compose up` aparece error al publicar el puerto, cámbialo (p. ej. `47117`) y alinea `MONGO_URL`. |
| `MONGO_DB_NAME` | Nombre de la base (default `chat_db`). La suite de tests usa `chat_test` vía `tests/conftest.py`. |
| `REDIS_URL` | URI de Redis (p. ej. `redis://127.0.0.1:6379/0`). Si no se define, la app arranca sin cliente Redis y `/health` mostrará `redis: disabled`. |
| `JWT_SECRET` | Obligatoria para `/auth/register` y `/auth/login` (mínimo 16 caracteres). Ver `.env.example`. |
| `JWT_EXPIRE_MINUTES` | Opcional; validez del access token (por defecto 10080 = 7 días). |
| `CORS_ORIGINS` | Opcional; URLs separadas por coma para el middleware CORS (front en Vercel, etc.). |

### 3. Base de datos con Docker Compose

```bash
docker compose up -d
```

Esto levanta **MongoDB** en el host (por defecto puerto **37117** → `27017` en el contenedor), **Redis** (6379) y **mongo-express** (8081). En la raíz del repo debe existir un archivo **`.env`** (puedes copiar `.env.example`: `cp .env.example .env`). **Docker Compose** usa `MONGO_HOST_PORT` del `.env` para publicar Mongo; **Uvicorn** carga el mismo `.env` al inicio (`python-dotenv` en `main.py`) para `MONGO_URL` y `REDIS_URL`. Si ves contenedores huérfanos de otro compose: `docker compose down --remove-orphans`.

### 4. Ejecutar la API

```bash
uvicorn main:app --host 0.0.0.0 --port 9000 --reload
```

- Documentación interactiva: `http://127.0.0.1:9000/docs`
- Estado de dependencias: `GET /health`
- Cliente de prueba WebSocket (HTML): `http://127.0.0.1:9000/chat`

Los identificadores de usuario en la API son **ObjectId de MongoDB** (cadena hexadecimal de 24 caracteres), no enteros secuenciales.

### 5. Tests (pytest)

Requiere **MongoDB accesible** con la misma `MONGO_URL` que uses en local (p. ej. `docker compose up -d`). Redis no es obligatorio para los tests REST.

```bash
pip install -r requirements-dev.txt
pytest -q
```

Los tests usan la base `chat_test` (variable `MONGO_DB_NAME` definida en `tests/conftest.py` antes de cargar la app).

## Endpoints principales

Las listas de mensajes devuelven `{"items": [...], "next_before_id": ..., "limit": ...}`. Paginación: repetir la petición con query `before_id=<next_before_id>` (ObjectId del último mensaje de la página actual). Detalle en [docs/api_contract.md](docs/api_contract.md).

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/auth/register` | Registro (mockup): nombre, username, email, teléfono, contraseña; devuelve JWT + usuario. |
| POST | `/auth/login` | Inicio de sesión con email y contraseña; devuelve JWT + usuario. |
| POST | `/usuarios` | Crear usuario (`nombre`). |
| GET | `/usuarios` | Listar usuarios. |
| GET | `/usuarios/{id}` | Obtener usuario por ObjectId. |
| PATCH | `/usuarios/{id}` | Actualizar `nombre`. |
| DELETE | `/usuarios/{id}` | Borrar usuario y sus mensajes asociados (`204`). |
| POST | `/mensajes` | Enviar mensaje (`remitente_id`, `destinatario_id`, `contenido`). |
| GET | `/mensajes` | Historial global paginado (`limit`, `before_id`). |
| GET | `/mensajes/conversacion/{usuario_a}/{usuario_b}` | Mensajes 1:1 entre dos usuarios. |
| GET | `/mensajes/{id_usuario}` | Mensajes donde participa el usuario (paginado). |
| POST | `/grupos` | Crear grupo (`nombre`, `creado_por`). |
| GET | `/grupos?usuario_id=...` | Grupos de un usuario. |
| GET/POST | `/grupos/{id}/miembros`, `DELETE .../miembros/{uid}` | Miembros (admin añade/expulsa). |
| GET/POST | `/grupos/{id}/mensajes` | Historial y envío en grupo. |
| WS | `/ws/realtime` | Tiempo real JSON (DM + grupos, Redis Pub/Sub). Ver `docs/chat_realtime.md`. |
| WS | `/ws/chat/{user_id}/{receptor_id}` | Legacy 1:1 texto plano. |

## Stack

- **FastAPI** + **Uvicorn**
- **MongoDB** + **Motor**
- **Redis** (`redis` asyncio; uso ampliable a pub/sub o rate limiting)
- **WebSockets** para entrega en tiempo real cuando el destinatario está conectado

## Documentación del proyecto

- Tiempo real (DM + grupos, Redis, eventos): [docs/chat_realtime.md](docs/chat_realtime.md)
- Casos de uso tiempo real: [docs/casos_de_uso_tiempo_real.md](docs/casos_de_uso_tiempo_real.md)
- Contrato de API: [docs/api_contract.md](docs/api_contract.md)
- Contexto operacional: [docs/contexto_operacional.md](docs/contexto_operacional.md)
- Problema (resumen): [docs/problema.md](docs/problema.md)
- Requisitos funcionales: [.requirements/chat_privado.requirements.md](.requirements/chat_privado.requirements.md)
- Casos de uso: [docs/casos_de_uso.md](docs/casos_de_uso.md)
- Arquitectura y ADRs: [docs/arquitectura.md](docs/arquitectura.md), [docs/decisiones_tecnicas.md](docs/decisiones_tecnicas.md)
