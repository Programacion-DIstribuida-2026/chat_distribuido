# 📋 Requerimientos del Sistema — Chat Privado

> **Institución:** COTECNOVA — Tecnología en Gestión de Sistemas de Información  
> **Semestre:** Séptimo | **Fecha:** Marzo 2026  
> **Equipo:** Kevin Villegas · Santiago Méndez · José David Zuluaga · Julián Andrés Caracas

---

## 1. Requerimientos Funcionales

| ID | Prioridad | Descripción | Endpoint / Recurso |
|----|-----------|-------------|-------------------|
| RF-001 | 🔴 ALTA | Registro de usuario con datos mínimos necesarios | `POST /usuarios` |
| RF-002 | 🔴 ALTA | Listado de todos los usuarios registrados | `GET /usuarios` |
| RF-003 | 🔴 ALTA | Obtener usuario específico por identificador único (ObjectId MongoDB, 24 hex) | `GET /usuarios/{id}` |
| RF-004 | 🔴 ALTA | Envío de mensajes entre usuarios (cuerpo JSON: `remitente_id`, `destinatario_id`, `contenido`) | `POST /mensajes` |
| RF-005 | 🔴 ALTA | Listado del historial completo de mensajes | `GET /mensajes` |
| RF-006 | 🔴 ALTA | Consulta de mensajes donde participa un usuario (ObjectId en la ruta) | `GET /mensajes/{id_usuario}` |
| RF-007 | 🔴 ALTA | Chat en tiempo real mediante WebSocket entre dos usuarios identificados | `WS /ws/chat/{user_id}/{receptor_id}` |
| RF-008 | 🟡 MEDIA | Validación de peticiones antes de persistir datos | Flujo interno del servidor |
| RF-009 | 🔴 ALTA | Almacenamiento mínimo y autorizado de datos | Base de datos |
| RF-010 | 🔴 ALTA | Respuesta de confirmación por cada operación | Todos los endpoints |

### RF-001 — Registro de Usuario
- **Prioridad:** ALTA
- **Descripción:** El sistema debe permitir crear un nuevo usuario proporcionando únicamente los datos estrictamente necesarios para su funcionamiento.
- **Endpoint:** `POST /usuarios` · Puerto `9000`
- **Validación:** El sistema debe verificar que los datos ingresados sean correctos antes de persistirlos en la base de datos.

### RF-002 — Consulta de Usuarios
- **Prioridad:** ALTA
- **Descripción:** El sistema debe permitir listar todos los usuarios registrados en la plataforma.
- **Endpoint:** `GET /usuarios` · Puerto `9000`

### RF-003 — Obtener Usuario por ID
- **Prioridad:** ALTA
- **Descripción:** El sistema debe permitir obtener la información de un usuario específico mediante su identificador único (`ObjectId` de MongoDB como cadena de 24 caracteres hexadecimales).
- **Endpoint:** `GET /usuarios/{id}` · Puerto `9000`

### RF-004 — Envío de Mensajes
- **Prioridad:** ALTA
- **Descripción:** El sistema debe permitir a un usuario autenticado enviar mensajes a otro usuario dentro de la plataforma. El cuerpo JSON incluye `remitente_id`, `destinatario_id` y `contenido` (ambos IDs con formato `ObjectId`).
- **Endpoint:** `POST /mensajes` · Puerto `9000`

### RF-005 — Listado de Mensajes
- **Prioridad:** ALTA
- **Descripción:** El sistema debe permitir consultar el historial de mensajes disponibles en la plataforma.
- **Endpoint:** `GET /mensajes` · Puerto `9000`

### RF-006 — Mensajes por Usuario
- **Prioridad:** ALTA
- **Descripción:** El sistema debe permitir obtener todos los mensajes asociados a un usuario específico mediante su identificador.
- **Endpoint:** `GET /mensajes/{id_usuario}` · Puerto `9000`

### RF-007 — Chat en Tiempo Real (WebSocket)
- **Prioridad:** ALTA
- **Descripción:** El sistema debe soportar comunicación bidireccional en tiempo real entre dos usuarios mediante WebSocket. La ruta identifica al usuario de la sesión y al interlocutor (`ObjectId` cada uno).
- **Endpoint:** `WS /ws/chat/{user_id}/{receptor_id}` · Puerto `9000`

### RF-008 — Flujo de Validación de Peticiones
- **Prioridad:** MEDIA
- **Descripción:** El sistema debe validar cada petición entrante antes de procesarla o persistir datos en la base de datos.
- **Flujo:**
  1. El usuario interactúa con el navegador.
  2. El navegador envía la petición de forma protegida.
  3. El sistema recibe y valida que los datos sean correctos.
  4. El servidor se conecta a la base de datos de forma segura.
  5. Se guarda únicamente la información necesaria.
  6. Se entrega una respuesta confirmando el proceso exitoso.

### RF-009 — Almacenamiento Mínimo de Datos
- **Prioridad:** ALTA
- **Descripción:** El sistema debe almacenar únicamente la información estrictamente necesaria para su funcionamiento, sin recolectar datos adicionales con fines comerciales o de rastreo.

### RF-010 — Respuesta de Confirmación
- **Prioridad:** ALTA
- **Descripción:** El sistema debe retornar una respuesta al cliente confirmando el éxito o fallo de cada operación solicitada.

---

## 2. Requerimientos No Funcionales

| ID | Prioridad | Descripción |
|----|-----------|-------------|
| RNF-001 | 🔴 ALTA | Privacidad por diseño: sin rastreadores ni compartición con terceros |
| RNF-002 | 🔴 ALTA | Comunicación protegida entre cliente y servidor |
| RNF-003 | 🔴 ALTA | Arquitectura en capas con responsabilidades separadas |
| RNF-004 | 🔴 ALTA | Modelo cliente-servidor con API REST |
| RNF-005 | 🟡 MEDIA | Procesamiento delegado al servidor para fluidez en el cliente |
| RNF-006 | 🔴 ALTA | Sin publicidad ni venta de perfiles de usuario |
| RNF-007 | 🔴 ALTA | Servidor FastAPI operando en el puerto `9000` |
| RNF-008 | 🟡 MEDIA | Componentes escalables de forma independiente |
| RNF-009 | 🔴 ALTA | Integridad y consistencia de los datos almacenados |
| RNF-010 | 🟢 BAJA | Accesible desde navegadores en PC y dispositivos móviles |

---

## 3. Requerimientos de Arquitectura

| ID | Componente | Tecnología | Detalle |
|----|-----------|------------|---------|
| RA-001 | Backend | FastAPI (Python) | Puerto `9000` · REST + WebSocket |
| RA-002 | Base de Datos | MongoDB | Conexión desde el servidor (variable `MONGO_URL`) |
| RA-003 | Caché / mensajería | Redis | Variable `REDIS_URL`; uso base healthcheck y extensible a pub/sub |
| RA-004 | Cliente | Navegador web | PC y dispositivos móviles |
| RA-005 | Patrón | Arquitectura en Capas | Separación de rutas, servicios y persistencia |

### Componentes del Sistema

| Componente | Rol |
|-----------|-----|
| Usuario + Navegador | Puerta de entrada; interfaz directa con el usuario |
| FastAPI | Motor del servidor; recibe, procesa y organiza cada petición |
| MongoDB | Persiste únicamente la información autorizada por el usuario |
| Redis | Infraestructura para salud del sistema y extensiones (pub/sub, rate limit) |
| WebSocket | Canal de comunicación bidireccional en tiempo real |

---

## 4. Tabla de Endpoints

| Nombre | Ruta | Método | Puerto | Req. |
|--------|------|--------|--------|------|
| Crear Usuario | `/usuarios` | `POST` | 9000 | RF-001 |
| Listar Usuarios | `/usuarios` | `GET` | 9000 | RF-002 |
| Obtener Usuario | `/usuarios/{id}` | `GET` | 9000 | RF-003 |
| Actualizar nombre | `/usuarios/{id}` | `PATCH` | 9000 | RF-003 (evolución) |
| Eliminar usuario y mensajes | `/usuarios/{id}` | `DELETE` | 9000 | RF-009 (evolución) |
| Enviar Mensaje | `/mensajes` | `POST` | 9000 | RF-004 |
| Listar Mensajes | `/mensajes` | `GET` | 9000 | RF-005, RF-014 (paginación `limit` / `before_id`) |
| Mensajes por usuario | `/mensajes/{id_usuario}` | `GET` | 9000 | RF-006, RF-014 |
| Conversación entre dos usuarios | `/mensajes/conversacion/{usuario_a}/{usuario_b}` | `GET` | 9000 | RF-005/006 (evolución) |
| Chat en tiempo real | `/ws/chat/{user_id}/{receptor_id}` | `WebSocket` | 9000 | RF-007 |

---

## 5. Bibliografía

- Brave. (s.f.). *Una comparación lado a lado: Chrome vs Brave*. https://brave.com/es/compare/chrome-vs-brave/
- FastAPI. (s.f.). *Documentación oficial FastAPI*. https://fastapi.tiangolo.com/
- Signal. (s.f.). *Signal Messenger*. https://signal.org/es/
