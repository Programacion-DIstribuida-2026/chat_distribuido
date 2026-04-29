# Casos de uso — Chat Distribuido (Chat privado)

> **Institución:** COTECNOVA — Tecnología en Gestión de Sistemas de Información  
> **Alcance:** API FastAPI + MongoDB + Redis + WebSockets  
> **Versión del documento:** Abril 2026

---

## 1. Lista de actores

| Actor | Descripción |
|-------|-------------|
| **Visitante** | Persona que aún no tiene cuenta en el sistema; no invoca endpoints protegidos por autenticación (en la versión actual la API es mayormente pública salvo evolución futura con tokens). |
| **Usuario registrado** | Persona con registro en el sistema (`usuarios` en MongoDB); utiliza REST y/o WebSocket para enviar y consultar mensajes. |
| **Cliente HTTP / WebSocket** | Aplicación (navegador, Postman, script) que consume la API. |
| **Sistema (FastAPI)** | Servidor que valida entradas, orquesta servicios y devuelve respuestas. |
| **Servicio de persistencia (MongoDB)** | Almacena usuarios y mensajes con modelo mínimo necesario. |
| **Servicio Redis** | Infraestructura para conectividad auxiliar (p. ej. healthcheck, futuro pub/sub o rate limiting); en la versión base se verifica disponibilidad en arranque y en `/health`. |
| **Administrador de plataforma** (opcional) | Rol futuro para operación de instancia (backups, configuración); no expuesto en los endpoints actuales. |

---

## 2. Casos de uso principales

| ID | Nombre | Prioridad |
|----|--------|-----------|
| CU-01 | Registrar usuario mínimo | Alta |
| CU-02 | Consultar listado de usuarios | Alta |
| CU-03 | Consultar perfil por identificador | Alta |
| CU-04 | Enviar mensaje (REST) entre dos usuarios | Alta |
| CU-05 | Consultar historial global de mensajes | Media |
| CU-06 | Consultar mensajes donde participa un usuario | Alta |
| CU-07 | Conectar sesión WebSocket de chat | Alta |
| CU-08 | Enviar mensaje en tiempo real vía WebSocket | Alta |
| CU-09 | Recuperar conversación paginada | Media (evolución / RF-014) |
| CU-10 | Cerrar sesión WebSocket | Alta |

---

## 3. CU-01 — Registrar usuario mínimo

**Objetivo:** Crear un usuario con los datos mínimos requeridos (nombre) y obtener su identificador único (`ObjectId` en MongoDB).

**Actores:** Usuario registrado (o Visitante que se registra), Cliente HTTP, Sistema, MongoDB.

**Precondiciones:**

- El cliente puede alcanzar el servidor FastAPI (puerto configurado, p. ej. 9000).
- MongoDB está disponible y la aplicación completó el arranque (`lifespan`).

**Postcondiciones:**

- Existe un documento en la colección `usuarios` con al menos el campo `nombre`.
- El cliente recibe una respuesta JSON con `id` (cadena hexadecimal de 24 caracteres) y `nombre`.

**Flujo principal:**

1. El actor solicita `POST /usuarios` con cuerpo JSON `{"nombre": "<texto no vacío>"}`.
2. El Sistema valida el cuerpo con el esquema Pydantic.
3. El Sistema invoca la capa de servicio para insertar el documento en MongoDB.
4. MongoDB confirma la inserción y devuelve el `_id` generado.
5. El Sistema responde `200` con `{"id": "...", "nombre": "..."}`.

**Flujos alternativos:**

- **A1 — Validación fallida:** Si `nombre` falta o no cumple reglas del modelo, el Sistema responde `422` con detalle de validación.
- **A2 — Base de datos no disponible:** Si la inserción falla por error de conexión, el Sistema responde `500` (comportamiento estándar de FastAPI/exception handlers si se configuran).

---

## 4. CU-02 — Consultar listado de usuarios

**Objetivo:** Obtener la lista de todos los usuarios registrados para selección de interlocutor o depuración controlada.

**Actores:** Usuario registrado, Cliente HTTP, Sistema, MongoDB.

**Precondiciones:** Misma conectividad que CU-01.

**Postcondiciones:** El cliente recibe un arreglo JSON de usuarios; cada elemento incluye `_id` como cadena.

**Flujo principal:**

1. El actor solicita `GET /usuarios`.
2. El Sistema consulta la colección `usuarios`.
3. El Sistema serializa cada `_id` como cadena y responde `200` con la lista.

**Flujos alternativos:**

- **A1 — Lista vacía:** Respuesta `200` con `[]`.

---

## 5. CU-03 — Consultar perfil por identificador

**Objetivo:** Obtener un único usuario por su identificador MongoDB (`ObjectId` como string).

**Actores:** Usuario registrado, Cliente HTTP, Sistema, MongoDB.

**Precondiciones:** El `id` proporcionado es una cadena de 24 caracteres hexadecimales válidos para `ObjectId`.

**Postcondiciones:** El cliente recibe el documento del usuario o un error coherente.

**Flujo principal:**

1. El actor solicita `GET /usuarios/{id}` donde `{id}` es el string del `ObjectId`.
2. El Sistema busca en MongoDB por `_id`.
3. Si existe, responde `200` con el documento (`_id` como string).

**Flujos alternativos:**

- **A1 — Identificador inválido:** Si el formato no es un `ObjectId` válido, el Sistema responde `422` (validación de path).
- **A2 — Usuario inexistente:** El Sistema responde `404` con mensaje claro.

---

## 6. CU-04 — Enviar mensaje (REST) entre dos usuarios

**Objetivo:** Persistir un mensaje con **remitente** y **destinatario** explícitos más contenido y marca temporal.

**Actores:** Usuario registrado, Cliente HTTP, Sistema, MongoDB.

**Precondiciones:** Identificadores de remitente y destinatario válidos (`ObjectId` string). En la versión académica actual no se exige token; en evolución (RF-011) el remitente se tomaría de la sesión.

**Postcondiciones:** Documento insertado en `mensajes` con `remitente_id`, `destinatario_id`, `contenido`, `fecha_hora`.

**Flujo principal:**

1. El actor envía `POST /mensajes` con JSON:  
   `{"remitente_id": "<ObjectId>", "destinatario_id": "<ObjectId>", "contenido": "<texto>"}`.
2. El Sistema valida el esquema y los `ObjectId`.
3. El Sistema inserta el mensaje en MongoDB.
4. El Sistema responde `200` con confirmación e `id` del mensaje insertado.

**Flujos alternativos:**

- **A1 — ObjectId inválido:** Respuesta `422` con mensaje descriptivo.
- **A2 — Contenido vacío o inválido:** Respuesta `422` por validación Pydantic.

---

## 7. CU-05 — Consultar historial global de mensajes

**Objetivo:** Obtener todos los mensajes persistidos ordenados (p. ej. más recientes primero) para auditoría o vista global.

**Actores:** Usuario registrado, Cliente HTTP, Sistema, MongoDB.

**Precondiciones:** Ninguna adicional.

**Postcondiciones:** Respuesta `200` con cuerpo JSON `items`, `next_before_id` y `limit`; `items` puede incluir documentos legacy con `id_usuario`. La ordenación implementada es por `_id` descendente (aproximación a “más reciente primero”).

**Flujo principal:**

1. El actor solicita `GET /mensajes` con query opcional `limit` (1–200, por defecto 50) y `before_id` (ObjectId de anclaje para la página siguiente).
2. El Sistema ejecuta la consulta paginada.
3. Responde `200` con el envelope JSON.

**Flujos alternativos:**

- **A1 — `before_id` inválido:** Respuesta `422`.
- **A2 — Páginas adicionales:** Si `next_before_id` no es nulo, el cliente puede repetir la petición con `before_id=<next_before_id>` (alineado con CU-09 / RF-014).

---

## 8. CU-06 — Consultar mensajes donde participa un usuario

**Objetivo:** Listar mensajes en los que el usuario es **remitente** o **destinatario** (y, si aplica, coincidencias legacy con `id_usuario`).

**Actores:** Usuario registrado, Cliente HTTP, Sistema, MongoDB.

**Precondiciones:** `id_usuario` en la ruta es un `ObjectId` válido en formato string.

**Postcondiciones:** Mismo envelope que CU-05 (`items`, `next_before_id`, `limit`).

**Flujo principal:**

1. El actor solicita `GET /mensajes/{id_usuario}` con los mismos query params de paginación que en CU-05.
2. El Sistema consulta con criterio OR sobre `remitente_id`, `destinatario_id` e histórico `id_usuario` si existe.
3. Responde `200` con el envelope JSON.

**Flujos alternativos:**

- **A1 — ObjectId inválido:** Respuesta `422`.

**Extensión:** Para un hilo estrictamente entre dos usuarios sin otros participantes, el sistema expone `GET /mensajes/conversacion/{usuario_a}/{usuario_b}` con la misma semántica de paginación.

---

## 9. CU-07 — Conectar sesión WebSocket de chat

**Objetivo:** Abrir un canal WebSocket identificando al usuario local y al interlocutor para mensajería en tiempo real.

**Actores:** Usuario registrado, Cliente WebSocket, Sistema, `ConnectionManager`.

**Precondiciones:** Ruta `WS /ws/chat/{user_id}/{receptor_id}` con **strings** de `ObjectId` válidos para ambos segmentos.

**Postcondiciones:** Conexión aceptada; si el mismo `user_id` ya tenía socket, la conexión anterior se cierra y se reemplaza por la nueva.

**Flujo principal:**

1. El cliente abre WebSocket contra la URL con ambos IDs.
2. El Sistema acepta la conexión y registra el socket en `ConnectionManager` bajo `user_id`.
3. El cliente queda en espera de envío/recepción de tramas de texto.

**Flujos alternativos:**

- **A1 — Parámetros inválidos:** Cierre con error de protocolo o rechazo según validación implementada en el servidor.
- **A2 — Mismo usuario como receptor:** El cliente debería evitarlo; si ocurre, el negocio puede definirse como no-op o error (definición de producto).

---

## 10. CU-08 — Enviar mensaje en tiempo real vía WebSocket

**Objetivo:** Al recibir texto por WebSocket, persistir el mensaje (remitente = `user_id`, destinatario = `receptor_id`) y notificar al destinatario si está conectado.

**Actores:** Usuario registrado, Cliente WebSocket, Sistema, MongoDB, `ConnectionManager`.

**Precondiciones:** WebSocket abierto (CU-07). Trama de texto no vacía tras `strip`.

**Postcondiciones:** Mensaje guardado; el destinatario recibe texto formateado; el emisor puede recibir confirmación `enviado`.

**Flujo principal:**

1. El cliente envía una cadena de texto por el WebSocket.
2. El Sistema ignora mensajes vacíos.
3. El Sistema persiste con `remitente_id=user_id`, `destinatario_id=receptor_id`.
4. El Sistema intenta `send_to_user(receptor_id, "<user_id>: <contenido>")`.
5. El Sistema envía al emisor la confirmación `enviado`.

**Flujos alternativos:**

- **A1 — Destinatario desconectado:** El paso de envío en tiempo real no entrega al peer; el mensaje **sí queda persistido** en MongoDB para consulta posterior (CU-06).
- **A2 — Error al enviar al destinatario:** El `ConnectionManager` desregistra sockets fallidos tras log de advertencia.

---

## 11. CU-09 — Recuperar conversación paginada (evolución)

**Objetivo:** Obtener mensajes entre dos usuarios con paginación estable (cursor / `before`–`after`) para cumplir RF-014.

**Actores:** Usuario registrado, Cliente HTTP, Sistema, MongoDB.

**Precondiciones:** Autenticación futura definida; endpoint dedicado acordado (no implementado en la versión mínima actual).

**Postcondiciones:** Página de resultados y token de cursor para la siguiente página.

**Flujo principal (diseño):**

1. El cliente solicita `GET /conversaciones/{id}/mensajes?limit=20&cursor=...`.
2. El Sistema valida permisos (el solicitante debe ser parte de la conversación).
3. El Sistema devuelve mensajes ordenados y metadatos de paginación.

**Flujos alternativos:**

- **A1 — Cursor inválido:** `400` o `422` con mensaje de cliente.
- **A2 — Sin permiso:** `403`.

---

## 12. CU-10 — Cerrar sesión WebSocket

**Objetivo:** Liberar el recurso de conexión y eliminar al usuario del mapa de conexiones activas.

**Actores:** Usuario registrado, Cliente WebSocket, Sistema, `ConnectionManager`.

**Precondiciones:** Existía una sesión WebSocket activa para ese `user_id`.

**Postcondiciones:** Entrada removida de `active_connections` (o equivalente).

**Flujo principal:**

1. El cliente cierra el WebSocket explícitamente o se interrumpe la red.
2. El Sistema captura `WebSocketDisconnect` (o error de recepción) y llama a `disconnect(user_id)`.
3. No se persisten eventos adicionales salvo diseño futuro de “última vez visto”.

**Flujos alternativos:**

- **A1 — Cierre anómalo:** El mismo tratamiento que limpia el registro en el mapa de conexiones.

---

## 13. Trazabilidad con requerimientos

| Caso de uso | Requerimientos relacionados |
|-------------|----------------------------|
| CU-01 | RF-001, RF-008, RF-009, RF-010 |
| CU-02 | RF-002, RF-010 |
| CU-03 | RF-003, RF-010 |
| CU-04 | RF-004, RF-008, RF-009, RF-010 |
| CU-05 | RF-005, RF-010 |
| CU-06 | RF-006, RF-010 |
| CU-07, CU-08, CU-10 | RF-007, RF-004 (persistencia), RF-010 |
| CU-09 | RF-014 (evolución) |

---

## 14. Referencias

- [.requirements/chat_privado.requirements.md](../.requirements/chat_privado.requirements.md)
- [docs/arquitectura.md](arquitectura.md) (stack y despliegue)
- [docs/decisiones_tecnicas.md](decisiones_tecnicas.md) (ADRs)
- [docs/api_contract.md](api_contract.md) (contrato REST alineado con el código)
- [docs/chat_realtime.md](chat_realtime.md) y [docs/casos_de_uso_tiempo_real.md](casos_de_uso_tiempo_real.md) (DM + grupos, WebSocket `/ws/realtime`, Redis)

---

## 15. Mapeo a endpoints implementados (evolución)

| Caso de uso | Endpoint / notas |
|-------------|------------------|
| CU-01 | `POST /usuarios` |
| CU-02 | `GET /usuarios` |
| CU-03 | `GET /usuarios/{id}` |
| CU-04 | `POST /mensajes` |
| CU-05 | `GET /mensajes` con `limit` y `before_id` (paginación, ver [api_contract.md](api_contract.md)) |
| CU-06 | `GET /mensajes/{id_usuario}` con los mismos query params |
| CU-07–CU-08, CU-10 | `WS /ws/chat/{user_id}/{receptor_id}` |
| CU-09 (diseño) | Parcialmente cubierto por la paginación por `before_id`; un recurso dedicado por `conversation_id` puede añadirse después. |
| Actualización de perfil mínimo | `PATCH /usuarios/{id}` |
| Baja de usuario y datos de mensajes asociados | `DELETE /usuarios/{id}` |
| Conversación 1:1 explícita | `GET /mensajes/conversacion/{usuario_a}/{usuario_b}` |
