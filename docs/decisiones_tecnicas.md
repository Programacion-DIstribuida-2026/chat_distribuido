# Decisiones técnicas (ADR) — Chat Distribuido

Formato breve: **Contexto → Decisión → Consecuencias**.

---

## ADR-001 — MongoDB como almacén principal

**Contexto:** Se requiere persistencia flexible para usuarios y mensajes en un proyecto académico con stack Python.

**Decisión:** Usar **MongoDB** con el driver asíncrono **Motor**.

**Consecuencias:** Los identificadores de usuario son **ObjectId** (24 caracteres hex). Las consultas y índices deben alinearse con ese modelo. No hay RLS como en Postgres; la autorización debe implementarse en la aplicación cuando exista autenticación.

---

## ADR-002 — Redis en el stack con conexión opcional

**Contexto:** Se desea infraestructura para escalar o añadir rate limiting / pub/sub sin rediseñar el despliegue más adelante.

**Decisión:** Incluir **Redis** en `docker-compose` y un cliente **async** (`redis` + `hiredis`) que se activa solo si existe `REDIS_URL`. El endpoint `/health` refleja `ok`, `error` o `disabled`.

**Consecuencias:** Los entornos sin Redis pueden omitir la variable y seguir desarrollando. Cuando se requiera fan-out entre varias instancias de FastAPI, se puede publicar en canales Redis sin cambiar el contrato REST.

---

## ADR-003 — Identificadores string (ObjectId) en REST y WebSocket

**Contexto:** Las rutas usaban `int` mientras Mongo generaba ObjectId; había incoherencia y fallos en tiempo de ejecución.

**Decisión:** Unificar **todos** los IDs expuestos en API y WebSocket como cadena de 24 hex, validada con regex en rutas y Pydantic.

**Consecuencias:** Los clientes dejan de usar “1, 2, 3” secuenciales; deben crear usuarios vía `POST /usuarios` y copiar el `id` devuelto. El HTML de demostración en `static/chat.html` se actualizó en consecuencia.

---

## ADR-004 — Modelo de mensaje con remitente y destinatario

**Contexto:** RF-004 exige mensajería entre usuarios; el modelo anterior solo guardaba `id_usuario` sin destinatario claro.

**Decisión:** Persistir `remitente_id`, `destinatario_id`, `contenido`, `fecha_hora`. Las consultas por usuario usan `$or` con campos nuevos y, si aplica, el campo legacy `id_usuario` para no romper datos antiguos.

**Consecuencias:** `POST /mensajes` cambia el cuerpo JSON respecto a versiones previas del curso.

---

## ADR-005 — WebSocket con dos parámetros de ruta

**Contexto:** La documentación académica inicial citaba `WS /ws/chat/{user_id}`; el producto necesita saber el interlocutor al conectar.

**Decisión:** Exponer `WS /ws/chat/{user_id}/{receptor_id}` con ambos ObjectId validados al aceptar la conexión.

**Consecuencias:** Los requisitos en `.requirements/chat_privado.requirements.md` se alinearon con esta ruta. Los clientes deben construir la URL con dos IDs.

---

## ADR-006 — ConnectionManager en proceso vs Redis pub/sub

**Contexto:** Entrega inmediata al destinatario conectado en la misma instancia.

**Decisión:** Mantener un **diccionario en memoria** por proceso para WebSockets activos.

**Consecuencias:** Varias réplicas de Uvicorn no comparten el mapa; la mitigación futura es publicar eventos en Redis y suscribir cada worker, o sticky sessions en el balanceador (menos elegante).

---

## ADR-007 — Imágenes Docker con etiqueta fija mayor

**Contexto:** `latest` dificulta reproducir entornos entre equipos.

**Decisión:** Fijar versiones mayor de **Mongo 7.0** y **Redis 7.4-alpine** en `docker-compose.yml`.

**Consecuencias:** Actualizar etiquetas cuando se requiera parche de seguridad o nueva major.

---

## ADR-008 — Listas de mensajes paginadas y envelope JSON

**Contexto:** `GET /mensajes` y `GET /mensajes/{id_usuario}` devolvían arreglos sin límite; con muchos documentos la respuesta crece sin control.

**Decisión:** Devolver siempre `{"items", "next_before_id", "limit}` y ordenar por `_id` descendente. El cliente pide la siguiente página con query `before_id` igual al `next_before_id` de la página anterior (clave compuesta simple, sin cursor opaco).

**Consecuencias:** Cambio incompatible para clientes que esperaban un arreglo en la raíz; queda documentado en [api_contract.md](api_contract.md).

---

## ADR-009 — Recurso de conversación 1:1 y `routes/deps`

**Contexto:** Hacía falta consultar solo el hilo entre dos usuarios sin mezclar otras conversaciones; además se duplicaba la definición de `ObjectIdPath` en varios routers.

**Decisión:** Añadir `GET /mensajes/conversacion/{usuario_a}/{usuario_b}` (ruta estática antes del parámetro `{id_usuario}`) y centralizar `ObjectIdPath` en [routes/deps.py](../routes/deps.py).

**Consecuencias:** Las rutas de mensajes deben mantener el orden: conversación antes que `/{id_usuario}` para evitar colisiones de path.

---

## ADR-010 — Actualización y borrado de usuario

**Contexto:** Solo existía creación y lectura; operación y privacidad por diseño sugieren poder corregir nombre o eliminar cuenta y datos asociados.

**Decisión:** `PATCH /usuarios/{id}` para `nombre` y `DELETE /usuarios/{id}` que borra mensajes donde el usuario es remitente, destinatario o campo legacy `id_usuario`, luego el documento de usuario.

**Consecuencias:** `DELETE` es destructivo y devuelve `204` sin cuerpo; el cliente debe manejar ausencia de JSON.

---

## ADR-011 — Mensajes con `tipo` directo vs grupo

**Contexto:** Se añadieron grupos sin romper el modelo 1:1 existente.

**Decisión:** Campo `tipo`: `"directo"` (por defecto en nuevos DM) y `"grupo"` con `grupo_id`. Las listas globales de mensajes excluyen `tipo: grupo` donde aplica; `GET /mensajes/{usuario}` incluye mensajes de grupo si el usuario es miembro.

**Consecuencias:** Consultas deben filtrar explícitamente por `tipo` cuando el producto lo requiera.

---

## ADR-012 — WebSocket unificado `/ws/realtime`

**Contexto:** Un socket por ruta 1:1 no escala a varios chats ni a grupos.

**Decisión:** Nuevo endpoint con mensajes JSON (`event` + `payload`), salas `dm:join` / `group:join` y eventos `message:new` con `scope`.

**Consecuencias:** El cliente legacy puede seguir usando `/ws/chat/...`; la UI nueva debería migrar a `/ws/realtime`.

---

## ADR-013 — Redis Pub/Sub para fan-out multi-instancia

**Contexto:** `ConnectionManager` solo cubre procesos locales.

**Decisión:** Tras persistir, `PUBLISH` a `grupo:{id}` o `dm:{min}:{max}`. Una tarea asyncio por proceso ejecuta `PSUBSCRIBE grupo:* dm:*` y reenvía al `RealtimeHub`.

**Consecuencias:** Sin `REDIS_URL` no hay sincronización entre puertos; el `publish_or_local` hace broadcast solo en la instancia actual.
