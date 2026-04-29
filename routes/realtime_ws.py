"""WebSocket unificado: JSON events para DM y grupos (session:auth, join, message, typing)."""

from __future__ import annotations

import json
import logging
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from core.realtime_channels import dm_room_key, grupo_room_key
from core.realtime_hub import get_realtime_hub
from core.redis_client import redis_client
from core.realtime_publish import publish_or_local
from services.grupo_service import es_miembro
from services.mensaje_service import enviar_mensaje, enviar_mensaje_grupo

logger = logging.getLogger(__name__)

router = APIRouter()


def _oid(label: str, value: str) -> str:
    v = value.strip().lower()
    if len(v) != 24 or any(c not in "0123456789abcdef" for c in v):
        raise ValueError(f"{label} debe ser un ObjectId hexadecimal de 24 caracteres.")
    return v


async def _send(ws: WebSocket, event: str, payload: dict[str, Any]) -> None:
    await ws.send_text(json.dumps({"event": event, "payload": payload}, ensure_ascii=False))


async def _send_error(ws: WebSocket, message: str, code: str = "bad_request") -> None:
    await _send(ws, "error", {"code": code, "message": message})


async def _presence_touch(user_id: str) -> None:
    r = redis_client()
    if r is None:
        return
    try:
        await r.setex(f"presence:user:{user_id}", 60, "1")
    except Exception as exc:
        logger.debug("presence setex: %s", exc)


@router.websocket("/ws/realtime")
async def realtime_ws(websocket: WebSocket):
    await websocket.accept()
    hub = get_realtime_hub()
    try:
        while True:
            raw = await websocket.receive_text()
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                await _send_error(websocket, "JSON inválido")
                continue
            event = data.get("event")
            payload = data.get("payload") or {}
            if not isinstance(payload, dict):
                payload = {}

            try:
                if event == "session:auth":
                    uid = _oid("user_id", str(payload.get("user_id", "")))
                    await hub.bind_user(websocket, uid)
                    await _presence_touch(uid)
                    await _send(websocket, "session:ok", {"user_id": uid})
                    continue

                user = hub.get_user_for_ws(websocket)
                if not user:
                    await _send_error(websocket, "Autentique primero con session:auth", "unauthorized")
                    continue

                if event == "dm:join":
                    peer = _oid("peer_id", str(payload.get("peer_id", "")))
                    rk = dm_room_key(user, peer)
                    await hub.join_room(websocket, rk)
                    await _send(websocket, "dm:joined", {"room": rk, "peer_id": peer})
                    continue

                if event == "dm:leave":
                    peer = _oid("peer_id", str(payload.get("peer_id", "")))
                    rk = dm_room_key(user, peer)
                    await hub.leave_room(websocket, rk)
                    await _send(websocket, "dm:left", {"room": rk})
                    continue

                if event == "group:join":
                    gid = _oid("grupo_id", str(payload.get("grupo_id", "")))
                    if not await es_miembro(gid, user):
                        await _send_error(websocket, "No eres miembro del grupo", "forbidden")
                        continue
                    rk = grupo_room_key(gid)
                    await hub.join_room(websocket, rk)
                    await _send(websocket, "group:joined", {"room": rk, "grupo_id": gid})
                    continue

                if event == "group:leave":
                    gid = _oid("grupo_id", str(payload.get("grupo_id", "")))
                    rk = grupo_room_key(gid)
                    await hub.leave_room(websocket, rk)
                    await _send(websocket, "group:left", {"room": rk})
                    continue

                if event == "message:new":
                    scope = str(payload.get("scope", "")).lower()
                    texto = str(payload.get("texto", "")).strip()
                    if not texto:
                        await _send_error(websocket, "texto vacío")
                        continue
                    if scope == "dm":
                        peer = _oid("peer_id", str(payload.get("peer_id", "")))
                        if peer == user:
                            await _send_error(websocket, "peer_id no puede ser igual a tu usuario")
                            continue
                        await enviar_mensaje(user, peer, texto)
                        rk = dm_room_key(user, peer)
                        await hub.join_room(websocket, rk)
                        continue
                    if scope == "group":
                        gid = _oid("grupo_id", str(payload.get("grupo_id", "")))
                        await enviar_mensaje_grupo(user, gid, texto)
                        rk = grupo_room_key(gid)
                        await hub.join_room(websocket, rk)
                        continue
                    await _send_error(websocket, "scope debe ser dm o group")
                    continue

                if event in ("typing:start", "typing:stop"):
                    active = event == "typing:start"
                    scope = str(payload.get("scope", "")).lower()
                    r = redis_client()
                    if scope == "dm":
                        peer = _oid("peer_id", str(payload.get("peer_id", "")))
                        rk = dm_room_key(user, peer)
                        if r:
                            tkey = f"typing:{rk}:{user}"
                            if active:
                                await r.setex(tkey, 5, "1")
                            else:
                                await r.delete(tkey)
                        await publish_or_local(
                            rk,
                            {
                                "event": "user:typing",
                                "payload": {
                                    "scope": "dm",
                                    "peer_id": peer,
                                    "usuario_id": user,
                                    "activo": active,
                                },
                            },
                        )
                        continue
                    if scope == "group":
                        gid = _oid("grupo_id", str(payload.get("grupo_id", "")))
                        rk = grupo_room_key(gid)
                        if r:
                            tkey = f"typing:{rk}:{user}"
                            if active:
                                await r.setex(tkey, 5, "1")
                            else:
                                await r.delete(tkey)
                        await publish_or_local(
                            rk,
                            {
                                "event": "user:typing",
                                "payload": {
                                    "scope": "group",
                                    "grupo_id": gid,
                                    "usuario_id": user,
                                    "activo": active,
                                },
                            },
                        )
                        continue
                    await _send_error(websocket, "scope inválido para typing")
                    continue

                if event == "heartbeat":
                    await _presence_touch(user)
                    await _send(websocket, "heartbeat:ok", {})
                    continue

                await _send_error(websocket, f"Evento desconocido: {event}", "unknown_event")
            except ValueError as e:
                await _send_error(websocket, str(e))
            except PermissionError as e:
                await _send_error(websocket, str(e), "forbidden")

    except WebSocketDisconnect:
        pass
    finally:
        await hub.disconnect(websocket)
