# Chat Privado
## Documento de Problemática y Especificación de Requerimientos

> **Institución:** COTECNOVA — Tecnología en Gestión de Sistemas de Información  
> **Semestre:** Séptimo | **Fecha:** Marzo 2026  
> **Equipo:** Kevin Villegas · Santiago Méndez · José David Zuluaga · Julián Andrés Caracas

---

## 1. Introducción

El desarrollo de muchas aplicaciones digitales se basa en utilizar la información de las personas con fines comerciales. Como consecuencia, quien las usa pierde el control sobre sus datos y contactos.

El presente documento introduce un sistema de comunicación privada inspirado en la filosofía de Brave, enfocado puramente en proteger la privacidad del usuario. La herramienta solicita únicamente los datos estrictamente necesarios para funcionar de forma segura, garantizando un espacio digital sin rastreadores ni venta de información a terceros.

La protección del usuario es el único objetivo de este sistema.

---

## 2. Planteamiento del Problema

### 2.1 Contexto General

Muchas herramientas digitales de comunicación exigen información personal que termina en perfiles comerciales o es compartida con terceros sin el pleno conocimiento del usuario. Esto provoca que la persona pierda el control de sus propios datos.

Además, gran parte de estos sistemas rastrean la actividad del usuario en segundo plano, aunque dicho rastreo no sea necesario para el funcionamiento del servicio. En consecuencia, el respeto a la intimidad ha quedado relegado, generando una notable escasez de opciones seguras y transparentes.

### 2.2 Descripción del Problema

Se identifican tres problemas centrales que justifican el desarrollo del sistema:

- **Pérdida de control de datos personales:** Los usuarios no tienen visibilidad ni gobierno sobre qué información se recolecta, quién la procesa y con qué fines se utiliza.
- **Rastreo de actividad en segundo plano:** Las aplicaciones convencionales monitorizan el comportamiento del usuario sin su consentimiento explícito, generando perfiles de consumo sin autorización.
- **Ausencia de alternativas privadas accesibles:** La mayoría de las soluciones de mensajería existentes priorizan el modelo de negocio basado en datos sobre la privacidad del usuario, sin ofrecer una alternativa real y funcional.

### 2.3 Impacto del Problema

La ausencia de herramientas de mensajería que respeten la privacidad por diseño impacta directamente en:

- La autonomía digital de los usuarios sobre su información personal.
- La confianza en las plataformas de comunicación.
- La seguridad de las comunicaciones privadas frente a actores comerciales y terceros no autorizados.

### 2.4 Pregunta de Investigación

> ¿Cómo desarrollar un sistema de mensajería privada que garantice la protección de datos del usuario, elimine rastreadores ocultos y opere bajo una filosofía de mínimo dato necesario, sin comprometer la funcionalidad ni la experiencia de uso?

---

## 3. Justificación

Este sistema surge como una alternativa real inspirada en la filosofía de Brave: la información del usuario no debe ser una moneda de cambio. Para lograrlo, el desarrollo se basa en el sentido común al pedir únicamente los datos estrictamente necesarios para funcionar.

No existen rastreadores ocultos ni intereses comerciales en la venta de perfiles a terceros. El compromiso es directo: el control de lo que se comparte se queda siempre en manos de quien usa el sistema, logrando un espacio digital tranquilo donde la privacidad no es un negocio, sino un derecho.

---

## 4. Arquitectura del Sistema

### 4.1 Modelo Cliente-Servidor

El sistema se divide en dos partes principales que se comunican mediante una **API REST**. El lado del cliente permite al usuario interactuar con la aplicación, mientras que el servidor procesa cada solicitud de forma organizada. Se utiliza una **arquitectura en capas** para que cada nivel del programa cumpla una tarea distinta, protegiendo la privacidad en cada paso de la comunicación.

### 4.2 Componentes del Sistema

| Componente | Rol |
|-----------|-----|
| **Usuario + Navegador** | Puerta de entrada; interfaz directa con el usuario |
| **FastAPI** | Motor del servidor; recibe, procesa y organiza cada petición |
| **MongoDB** | Persiste únicamente la información autorizada por el usuario |
| **Redis** | Infraestructura para salud del sistema y extensiones (pub/sub, rate limit) |
| **WebSocket** | Canal de comunicación bidireccional en tiempo real |

### 4.3 Flujo del Sistema

```
Usuario
  │
  ▼
Navegador  ──(petición protegida)──►  FastAPI (puerto 9000)
                                           │
                                     Validación de datos
                                           │
                                           ▼
                                       MongoDB
                                    (mínimo dato)
                                           │
                                           ▼
                               Respuesta al cliente ◄──────┘
```

**Paso a paso:**

1. El usuario interactúa con el navegador.
2. El navegador envía la petición de forma protegida al servidor.
3. El sistema recibe la petición y valida que los datos sean correctos.
4. El servidor se conecta a la base de datos de forma segura.
5. Se guarda únicamente la información estrictamente necesaria.
6. Se entrega una respuesta al cliente confirmando el éxito de la operación.

### 4.4 Tabla de Endpoints

| Nombre | Ruta | Método | Puerto |
|--------|------|--------|--------|
| Crear Usuario | `/usuarios` | `POST` | 9000 |
| Listar Usuarios | `/usuarios` | `GET` | 9000 |
| Obtener Usuario | `/usuarios/{id}` | `GET` | 9000 |
| Enviar Mensaje | `/mensajes` | `POST` | 9000 |
| Listar Mensajes | `/mensajes` | `GET` | 9000 |
| Mensajes por usuario | `/mensajes/{id_usuario}` | `GET` | 9000 |
| Chat en tiempo real | `/ws/chat/{user_id}/{receptor_id}` | `WebSocket` | 9000 |

---

## 5. Bibliografía

- Brave. (s.f.). *Una comparación lado a lado: Chrome vs Brave*. Recuperado el 12 de marzo de 2026, de https://brave.com/es/compare/chrome-vs-brave/
- FastAPI. (s.f.). *Documentación oficial FastAPI*. Recuperado el 12 de marzo de 2026, de https://fastapi.tiangolo.com/
- Signal. (s.f.). *Signal Messenger*. Recuperado el 12 de marzo de 2026, de https://signal.org/es/
