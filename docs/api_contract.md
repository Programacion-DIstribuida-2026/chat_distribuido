# Contrato de API — Chat Distribuido

Documentación alineada con el código (FastAPI). La referencia canónica interactiva sigue siendo **`/docs`** (OpenAPI).

**Base URL de ejemplo:** `http://127.0.0.1:9000`  
**Identificadores:** todos los IDs de usuario y cursores de paginación de mensajes son **ObjectId de MongoDB** (24 caracteres hexadecimales, mayúsculas o minúsculas según el cliente).

---

## Convenciones

| Aspecto | Detalle |
|---------|---------|
| Content-Type | `application/json` en cuerpos de petición y respuestas JSON. |
| Errores | `401` credenciales inválidas; `404` recurso no encontrado; `409` conflicto (p. ej. registro duplicado); `422` validación; `503` servicio no configurado (p. ej. `JWT_SECRET`). |
| Paginación de listas de mensajes | Respuesta envuelta: `items`, `next_before_id`, `limit`. Repite la petición pasando `before_id=<next_before_id>` para la página siguiente (mensajes más antiguos). |

---

## Raíz y utilidades

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/` | Mensaje de bienvenida JSON. |
| GET | `/health` | Estado de MongoDB y Redis (`ok`, `error`, `disabled`). |
| GET | `/chat` | Página HTML de demostración WebSocket. |

---

## Auth (registro e inicio de sesión)

Requieren `JWT_SECRET` en el entorno (mínimo 16 caracteres). El token es **JWT** HS256; `sub` = ObjectId del usuario (mismo id que el resto de la API).

| Método | Ruta | Cuerpo | Respuesta |
|--------|------|--------|------------|
| POST | `/auth/register` | `nombre`, `username` (solo letras, números, `_`), `email`, `codigo_pais` (ej. `+57`), `numero` (dígitos; se normaliza a E.164), `password` (8–72 caracteres) | `201`: `access_token`, `token_type` (`bearer`), `user`: `{ id, nombre, username, email, telefono_e164 }`. |
| POST | `/auth/login` | `email`, `password` | `200`: mismo envelope que registro. |

Errores: `409` correo, usuario o teléfono ya usados; `422` datos inválidos (teléfono, formato, etc.); `401` login fallido.

CORS: si defines `CORS_ORIGINS` (URLs separadas por coma) en el servidor, se permiten esos orígenes en navegador.

---

## Usuarios

| Método | Ruta | Cuerpo / parámetros | Respuesta |
|--------|------|---------------------|-----------|
| POST | `/usuarios` | `{"nombre": "..."}` | `200`: `{"id","nombre"}`. Útil en desarrollo; el flujo del mockup usa **`/auth/register`**. |
| GET | `/usuarios` | — | Lista de documentos con `_id` string. |
| GET | `/usuarios/{id}` | `id` ObjectId | Documento usuario o `404`. |
| PATCH | `/usuarios/{id}` | `{"nombre": "..."}` | Usuario actualizado o `404`. |
| DELETE | `/usuarios/{id}` | — | `204` sin cuerpo; elimina mensajes asociados (remitente/destinatario o `id_usuario` legacy) y el usuario. `404` si no existe. |

---

## Mensajes (REST)

| Método | Ruta | Query | Respuesta |
|--------|------|-------|-----------|
| POST | `/mensajes` | — | Cuerpo: `{"remitente_id","destinatario_id","contenido"}`. Éxito: `{"message","id"}`. |
| GET | `/mensajes` | `limit` (1–200, default 50), `before_id` (ObjectId opcional) | `{"items":[],"next_before_id":null\|string,"limit":N}`. |
| GET | `/mensajes/conversacion/{usuario_a}/{usuario_b}` | mismo query | Mensajes entre A y B en ambas direcciones; mismo envelope. |
| GET | `/mensajes/{id_usuario}` | mismo query | Mensajes donde el usuario participa (remitente, destinatario o legacy `id_usuario`). |

**Orden:** los ítems van de **más reciente a más antiguo** (orden por `_id` descendente).

---

## Grupos (REST)

Requieren `usuario_id` / `actor_id` como ObjectId string (24 hex).

| Método | Ruta | Descripción |
|--------|------|---------------|
| POST | `/grupos` | Cuerpo `{"nombre","creado_por"}`. Crea grupo y al creador como `admin`. |
| GET | `/grupos?usuario_id={ObjectId}` | Lista grupos en los que participa el usuario. |
| GET | `/grupos/{grupo_id}` | Detalle del grupo. |
| GET | `/grupos/{grupo_id}/miembros` | Lista `grupo_miembros`. |
| POST | `/grupos/{grupo_id}/miembros` | Cuerpo `{"usuario_id","actor_id"}`. Solo un **admin** puede añadir. |
| DELETE | `/grupos/{grupo_id}/miembros/{usuario_id}?actor_id={ObjectId}` | Salir (`actor_id` = `usuario_id`) o expulsar (admin). El único admin no puede salir sin otro admin. |
| GET | `/grupos/{grupo_id}/mensajes` | Historial de mensajes `tipo: grupo` (paginación `limit` / `before_id`). |
| POST | `/grupos/{grupo_id}/mensajes` | Cuerpo `{"remitente_id","contenido"}`. El remitente debe ser miembro. |

---

## WebSocket

| Protocolo | Ruta | Uso |
|-----------|------|-----|
| WS | `/ws/realtime` | **Recomendado:** frames de texto JSON, línea a línea. Ver [chat_realtime.md](chat_realtime.md) (eventos `session:auth`, `dm:join`, `group:join`, `message:new`, `typing:*`, `heartbeat`). |
| WS | `/ws/chat/{user_id}/{receptor_id}` | Legacy: texto plano 1:1; sigue publicando en Redis `dm:min:max` vía la misma capa de mensajes. |

---

## Cambios respecto a versiones anteriores del curso

- `GET /mensajes` y `GET /mensajes/{id_usuario}` devolvían un arreglo plano; ahora devuelven el **objeto paginado** descrito arriba.
- Nuevos: `PATCH` / `DELETE` en usuarios, `GET .../conversacion/.../...`, query `limit` / `before_id`.
- Grupos REST, mensajes `tipo: grupo`, WebSocket `/ws/realtime` y Pub/Sub Redis (`grupo:*`, `dm:*`).

---

## Referencias

- [README.md](../README.md)
- [arquitectura.md](arquitectura.md)
- [chat_realtime.md](chat_realtime.md)
- [casos_de_uso_tiempo_real.md](casos_de_uso_tiempo_real.md)
- [decisiones_tecnicas.md](decisiones_tecnicas.md)
