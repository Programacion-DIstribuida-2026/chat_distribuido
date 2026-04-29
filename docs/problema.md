# Problema (resumen ejecutivo)

Las plataformas de mensajería habituales suelen explotar datos personales o priorizar modelos de negocio sobre la privacidad. Este proyecto busca un **chat con datos mínimos** y control del usuario.

## Qué construimos

Un backend **FastAPI** con **MongoDB** (historial), **Redis** (tiempo real entre instancias, presencia y typing) y **WebSockets** para **mensajes 1:1 y de grupo**.

## Documentación relacionada

- Planteamiento extendido: [chat_privado_problematica.md](chat_privado_problematica.md)
- Requisitos: [../.requirements/chat_privado.requirements.md](../.requirements/chat_privado.requirements.md)
- Arquitectura y tiempo real: [arquitectura.md](arquitectura.md), [chat_realtime.md](chat_realtime.md)
- Contrato HTTP/WS: [api_contract.md](api_contract.md)
