# Chat en tiempo real — 1:1 y grupal (FastAPI + MongoDB + Redis)

Este documento describe la arquitectura de tiempo real del **Chat Distribuido**: mensajes directos (DM) y grupos, **WebSocket unificado** (`/ws/realtime`), **Redis Pub/Sub** para múltiples instancias de Uvicorn y persistencia en **MongoDB**.

---

## 1. Objetivos

| Objetivo | Mecanismo |
|----------|-----------|
| Baja latencia en salas | Broadcast local a sockets suscritos; Redis solo cruza instancias. |
| Escalado horizontal | Cada worker Uvicorn se suscribe a `grupo:*` y `dm:*`; al publicar, todas las instancias entregan a sus clientes locales en esa sala. |
| Historial fiable | Fuente de verdad: MongoDB. Tras reconexión, el cliente usa REST paginado (`before_id`). |
| DM y grupo unificados | Mismo formato JSON de eventos; el campo `scope` distingue `dm` y `group`. |

---

## 2. Flujo de datos (6 pasos)

1. El **cliente** envía un mensaje por WebSocket (`message:new`) o usa REST (`POST /mensajes` o `POST /grupos/{id}/mensajes`).
2. El **backend** valida autenticación mínima de sesión WS (`session:auth`) y permisos (membresía en grupo o DM).
3. Se **persiste** el documento en MongoDB (`mensajes` con `tipo: "directo"` o `"grupo"`).
4. El backend **publica** en Redis en el canal de la sala: `grupo:{grupoId}` o `dm:{minUserId}:{maxUserId}`.
5. **Todas las instancias** que ejecutan el listener Redis reciben el mensaje y lo reenvían a los WebSocket **suscritos localmente** a esa sala (`group:join` / `dm:join`).
6. Los clientes actualizan la UI; los que se **reconectaron** sincronizan con REST.

```text
Cliente_A --WS--> Instancia_1 --PUBLISH--> Redis
                              --> Mongo
                    Redis --PUBLISH--> Instancia_2 --WS--> Cliente_B
```

Si **Redis no está configurado** (`REDIS_URL` vacío), el paso 4–5 se omiten y el broadcast se hace **solo en la instancia actual** (adecuado para desarrollo con un solo worker).

---

## 3. Canales y claves Redis

| Uso | Canal o clave | Ejemplo |
|-----|-----------------|---------|
| Pub/Sub grupo | `grupo:{grupoObjectId}` | `grupo:674a1b2c3d4e5f60789a0bcd` |
| Pub/Sub DM | `dm:{min}:{max}` | `dm:674a...b:674a...c` (ObjectIds en hex minúsculos ordenados) |
| Presencia global | `presence:user:{userId}` | Valor `1`, TTL ~60 s (renovar con heartbeat) |
| Typing grupo | `typing:grupo:{grupoId}:{userId}` | TTL 5 s |
| Typing DM | `typing:dm:{min}:{max}:{userId}` | TTL 5 s |

Los mensajes publicados en Pub/Sub son **cadenas JSON** con al menos `event` y `payload` (mismo contrato que en WebSocket).

---

## 4. Contrato WebSocket — `GET ws://host/ws/realtime`

Tras conectar, el cliente envía **líneas JSON** (text frame) con:

```json
{"event":"<nombre>","payload":{...}}
```

### Cliente → servidor

| Evento | Payload | Descripción |
|--------|---------|-------------|
| `session:auth` | `user_id` (ObjectId) | Registra la conexión como ese usuario (MVP sin JWT; en producción sustituir por token). |
| `dm:join` | `peer_id` | Suscribe el socket a la sala DM con el par `(user_id autenticado, peer_id)`. |
| `dm:leave` | `peer_id` | Deja la sala DM. |
| `group:join` | `grupo_id` | Verifica membresía en Mongo y suscribe a `grupo:{id}`. |
| `group:leave` | `grupo_id` | Deja la sala. |
| `message:new` | `scope`, `texto`, y `peer_id` o `grupo_id` | Persiste y publica en la sala correspondiente. |
| `typing:start` / `typing:stop` | `scope`, `peer_id` o `grupo_id` | Actualiza Redis y notifica a la sala. |

### Servidor → cliente

| Evento | Payload típico |
|--------|----------------|
| `session:ok` | `{"user_id":"..."}` |
| `message:new` | Incluye `id` (Mongo), `scope`, remitente, texto, fechas según tipo. |
| `user:typing` | `scope`, `usuario_id`, `activo`, `peer_id` o `grupo_id`. |
| `user:online` / `user:offline` | `usuario_id` (broadcast opcional a salas suscritas). |
| `error` | `code`, `message` |

---

## 5. Esquema Mongo (resumen)

| Colección | Uso |
|-----------|-----|
| `usuarios` | Usuarios existentes. |
| `grupos` | Metadatos del grupo (`nombre`, `creado_por`, `creado_en`). |
| `grupo_miembros` | Membresía (`grupo_id`, `usuario_id`, `rol`: `admin` \| `miembro`). |
| `mensajes` | `tipo: "directo"`: `remitente_id`, `destinatario_id`. `tipo: "grupo"`: `remitente_id`, `grupo_id`, sin `destinatario_id`. |

---

## 6. WebSocket legacy

`WS /ws/chat/{user_id}/{receptor_id}` se mantiene por compatibilidad (texto plano). Los clientes nuevos deberían usar **`/ws/realtime`** con el contrato JSON.

---

## 7. Reconexión del cliente

1. Detectar cierre o error del WebSocket.
2. Esperar backoff exponencial (p. ej. 1s, 2s, 4s… con tope).
3. Abrir de nuevo `/ws/realtime`.
4. Enviar `session:auth`, luego todos los `dm:join` y `group:join` necesarios.
5. Solicitar historial vía REST con el último `_id` conocido como `before_id`.

---

## 8. Referencias

- [api_contract.md](api_contract.md)
- [casos_de_uso_tiempo_real.md](casos_de_uso_tiempo_real.md)
- [arquitectura.md](arquitectura.md)
- [decisiones_tecnicas.md](decisiones_tecnicas.md)
