# Casos de uso — Tiempo real (1:1 y grupos)

> Complemento de [casos_de_uso.md](casos_de_uso.md). Actores: **Usuario**, **Admin de grupo**, **Sistema (FastAPI)**, **Redis**, **MongoDB**, **Cliente WebSocket**.

---

## Actores

| Actor | Rol |
|-------|-----|
| Usuario | Usa REST y/o WebSocket; envía y recibe mensajes DM o de grupo. |
| Admin de grupo | Miembro con `rol: admin` en `grupo_miembros`; puede añadir miembros (según reglas implementadas). |
| Sistema | Valida, persiste, publica en Redis y hace broadcast WS. |
| Redis | Pub/Sub entre instancias; typing y presencia con TTL. |
| MongoDB | Historial y membresías. |

---

## CU-RT-01 — Autenticar sesión WebSocket (MVP)

**Descripción:** Asociar el socket a un `user_id` conocido para poder unirse a salas y enviar mensajes.

**Precondiciones:** Conexión WebSocket abierta a `/ws/realtime`.

**Postcondiciones:** El servidor conoce el `user_id` de esa conexión y responde `session:ok`.

**Flujo principal:**

1. El cliente envía `{"event":"session:auth","payload":{"user_id":"<ObjectId>"}}`.
2. El Sistema valida el formato ObjectId.
3. El Sistema registra la conexión y responde `session:ok`.

**Flujos alternativos:**

- **A1 — ObjectId inválido:** respuesta `error` y cierre opcional del socket.

---

## CU-RT-02 — Unirse a sala DM (1:1)

**Descripción:** Suscribir el socket a la sala estable entre dos usuarios (`dm:min:max`).

**Precondiciones:** `session:auth` completado; `peer_id` distinto del usuario autenticado.

**Postcondiciones:** El socket recibe eventos publicados en esa sala DM.

**Flujo principal:**

1. El cliente envía `dm:join` con `peer_id`.
2. El Sistema calcula la clave de sala y registra la suscripción local.

**Flujos alternativos:**

- **A1 — Sin auth previa:** `error`.

---

## CU-RT-03 — Unirse a sala de grupo

**Descripción:** Suscribirse a los eventos en tiempo real de un grupo.

**Precondiciones:** `session:auth` hecho; el usuario es miembro del grupo en MongoDB.

**Postcondiciones:** Suscripción a `grupo:{grupo_id}` en el hub local.

**Flujo principal:**

1. El cliente envía `group:join` con `grupo_id`.
2. El Sistema verifica membresía en `grupo_miembros`.
3. En caso afirmativo, registra la suscripción.

**Flujos alternativos:**

- **A1 — No miembro:** `error` (no autorizado).
- **A2 — Redis caído:** la suscripción local sigue funcionando en esa instancia; no hay fan-out remoto.

---

## CU-RT-04 — Enviar mensaje DM en tiempo real

**Descripción:** Persistir un DM y notificar a ambos lados de la conversación vía Pub/Sub y WS.

**Precondiciones:** Auth WS; idealmente ambos en `dm:join` (el remitente puede auto-unirse al enviar).

**Postcondiciones:** Documento en `mensajes` con `tipo: "directo"`; evento `message:new` en la sala DM.

**Flujo principal:**

1. Cliente envía `message:new` con `scope:"dm"`, `peer_id`, `texto`.
2. Sistema persiste en Mongo.
3. Sistema publica en Redis `dm:{min}:{max}` (o broadcast local si no hay Redis).
4. Listeners y/o hub entregan el JSON a sockets suscritos.

**Flujos alternativos:**

- **A1 — Peer no conectado:** el mensaje queda guardado; al reconectar, el cliente usa REST paginado.

---

## CU-RT-05 — Enviar mensaje de grupo en tiempo real

**Descripción:** Persistir mensaje de grupo y notificar a todos los miembros suscritos en cualquier instancia.

**Precondiciones:** Usuario miembro del grupo.

**Postcondiciones:** Documento `tipo: "grupo"` con `grupo_id`; evento en canal `grupo:{id}`.

**Flujo principal:** Análogo a CU-RT-04 con `scope:"group"` y validación de membresía.

**Flujos alternativos:**

- **A1 — Usuario expulsado:** `error` al enviar.

---

## CU-RT-06 — Ver usuarios en línea (MVP)

**Descripción:** Presencia aproximada vía Redis `presence:user:{id}` con TTL renovado por heartbeat o eventos WS.

**Precondiciones:** Redis disponible para TTL de presencia.

**Postcondiciones:** Otros clientes pueden mostrar estado en línea (según consultas o eventos `user:online`/`user:offline` emitidos por el servidor).

**Flujos alternativos:**

- **A1 — Sin Redis:** presencia limitada a la instancia actual o deshabilitada.

---

## CU-RT-07 — Indicador “escribiendo…”

**Descripción:** Notificar typing en la sala DM o de grupo.

**Precondiciones:** Sala unida (`dm:join` / `group:join`).

**Flujo principal:**

1. Cliente envía `typing:start` o `typing:stop` con `scope` y destino.
2. Servidor escribe clave Redis con TTL corto y publica `user:typing` en la misma sala Pub/Sub.

**Flujos alternativos:**

- **A1 — Flood:** rate limit sugerido en servidor (fase posterior).

---

## CU-RT-08 — Crear grupo (REST)

**Descripción:** Crear un grupo y al creador como `admin`.

**Precondiciones:** `creado_por` usuario existente.

**Postcondiciones:** Documentos en `grupos` y `grupo_miembros`.

**Flujo principal:** `POST /grupos` con `nombre` y `creado_por`.

**Flujos alternativos:** validación 422, usuario inexistente 404.

---

## CU-RT-09 — Añadir miembro a grupo (REST)

**Descripción:** Un admin añade un `usuario_id` al grupo.

**Precondiciones:** Actor con rol admin en `grupo_miembros`.

**Flujo principal:** `POST /grupos/{id}/miembros` con cuerpo según API.

**Flujos alternativos:** 403 si no admin; 409 si ya miembro.

---

## CU-RT-10 — Salir o ser expulsado del grupo (REST)

**Descripción:** Eliminar fila de `grupo_miembros` (salida voluntaria o expulsión por admin).

**Flujo principal:** `DELETE /grupos/{id}/miembros/{usuario_id}` con reglas de permiso.

**Flujos alternativos:** último admin no puede salir sin transferir rol (regla opcional; MVP puede permitir).

---

## Referencias

- [chat_realtime.md](chat_realtime.md)
- [api_contract.md](api_contract.md)
