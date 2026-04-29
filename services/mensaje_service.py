from datetime import datetime, timezone
from typing import Any

from bson import ObjectId

from database import db

TIPO_DIRECTO = "directo"
TIPO_GRUPO = "grupo"


def _require_oid(value: str, field: str) -> None:
    if not ObjectId.is_valid(value):
        raise ValueError(f"{field} no es un ObjectId válido de MongoDB.")


def _clamp_limit(limit: int) -> int:
    return max(1, min(int(limit), 200))


def _serialize_doc(doc: dict[str, Any]) -> dict[str, Any]:
    out = dict(doc)
    out["_id"] = str(out["_id"])
    return out


def _filtro_no_grupo() -> dict[str, Any]:
    return {"$or": [{"tipo": {"$ne": TIPO_GRUPO}}, {"tipo": {"$exists": False}}]}


async def _broadcast_dm_message(doc: dict[str, Any]) -> None:
    from core.realtime_channels import dm_room_key
    from core.realtime_publish import publish_or_local

    ser = _serialize_doc(doc)
    event = {
        "event": "message:new",
        "payload": {
            "scope": "dm",
            "id": ser["_id"],
            "remitente_id": doc.get("remitente_id"),
            "destinatario_id": doc.get("destinatario_id"),
            "contenido": doc.get("contenido"),
            "fecha_hora": doc.get("fecha_hora").isoformat()
            if doc.get("fecha_hora")
            else None,
        },
    }
    room = dm_room_key(str(doc["remitente_id"]), str(doc["destinatario_id"]))
    await publish_or_local(room, event)


async def _broadcast_grupo_message(doc: dict[str, Any]) -> None:
    from core.realtime_channels import grupo_room_key
    from core.realtime_publish import publish_or_local

    ser = _serialize_doc(doc)
    gid = str(doc.get("grupo_id", ""))
    event = {
        "event": "message:new",
        "payload": {
            "scope": "group",
            "id": ser["_id"],
            "grupo_id": gid,
            "remitente_id": doc.get("remitente_id"),
            "contenido": doc.get("contenido"),
            "fecha_hora": doc.get("fecha_hora").isoformat()
            if doc.get("fecha_hora")
            else None,
        },
    }
    await publish_or_local(grupo_room_key(gid), event)


async def enviar_mensaje(remitente_id: str, destinatario_id: str, contenido: str):
    _require_oid(remitente_id, "remitente_id")
    _require_oid(destinatario_id, "destinatario_id")

    nuevo_mensaje: dict[str, Any] = {
        "tipo": TIPO_DIRECTO,
        "remitente_id": remitente_id,
        "destinatario_id": destinatario_id,
        "contenido": contenido,
        "fecha_hora": datetime.now(timezone.utc),
    }
    result = await db.mensajes.insert_one(nuevo_mensaje)
    doc = await db.mensajes.find_one({"_id": result.inserted_id})
    if doc:
        await _broadcast_dm_message(doc)
    return {"message": "Mensaje enviado", "id": str(result.inserted_id)}


async def enviar_mensaje_grupo(remitente_id: str, grupo_id: str, contenido: str):
    from services.grupo_service import es_miembro

    _require_oid(remitente_id, "remitente_id")
    _require_oid(grupo_id, "grupo_id")
    if not await es_miembro(grupo_id, remitente_id):
        raise PermissionError("El remitente no es miembro del grupo.")

    nuevo: dict[str, Any] = {
        "tipo": TIPO_GRUPO,
        "grupo_id": grupo_id,
        "remitente_id": remitente_id,
        "contenido": contenido,
        "fecha_hora": datetime.now(timezone.utc),
    }
    result = await db.mensajes.insert_one(nuevo)
    doc = await db.mensajes.find_one({"_id": result.inserted_id})
    if doc:
        await _broadcast_grupo_message(doc)
    return {"message": "Mensaje de grupo enviado", "id": str(result.inserted_id)}


async def listar_mensajes(limit: int = 50, before_id: str | None = None):
    lim = _clamp_limit(limit)
    parts: list[dict[str, Any]] = [_filtro_no_grupo()]
    if before_id is not None:
        _require_oid(before_id, "before_id")
        parts.append({"_id": {"$lt": ObjectId(before_id)}})
    query: dict[str, Any] = {"$and": parts} if len(parts) > 1 else parts[0]

    mensajes: list[dict[str, Any]] = []
    cursor = db.mensajes.find(query).sort("_id", -1).limit(lim)
    async for msg in cursor:
        mensajes.append(_serialize_doc(msg))

    next_before = mensajes[-1]["_id"] if len(mensajes) == lim else None
    return {"items": mensajes, "next_before_id": next_before, "limit": lim}


async def mensajes_por_usuario(id_usuario: str, limit: int = 50, before_id: str | None = None):
    if not ObjectId.is_valid(id_usuario):
        raise ValueError("id_usuario no es un ObjectId válido de MongoDB.")

    from services.grupo_service import ids_grupos_de_usuario

    lim = _clamp_limit(limit)
    grupo_ids = await ids_grupos_de_usuario(id_usuario)
    or_parts: list[dict[str, Any]] = [
        {"remitente_id": id_usuario},
        {"destinatario_id": id_usuario},
        {"id_usuario": id_usuario},
    ]
    if grupo_ids:
        or_parts.append({"tipo": TIPO_GRUPO, "grupo_id": {"$in": grupo_ids}})
    filtro: dict[str, Any] = {"$or": or_parts}
    if before_id is not None:
        _require_oid(before_id, "before_id")
        filtro = {"$and": [filtro, {"_id": {"$lt": ObjectId(before_id)}}]}

    mensajes: list[dict[str, Any]] = []
    cursor = db.mensajes.find(filtro).sort("_id", -1).limit(lim)
    async for msg in cursor:
        mensajes.append(_serialize_doc(msg))

    next_before = mensajes[-1]["_id"] if len(mensajes) == lim else None
    return {"items": mensajes, "next_before_id": next_before, "limit": lim}


async def mensajes_entre_usuarios(
    usuario_a: str,
    usuario_b: str,
    limit: int = 50,
    before_id: str | None = None,
):
    _require_oid(usuario_a, "usuario_a")
    _require_oid(usuario_b, "usuario_b")

    lim = _clamp_limit(limit)
    dir_dm = {
        "$or": [
            {"remitente_id": usuario_a, "destinatario_id": usuario_b},
            {"remitente_id": usuario_b, "destinatario_id": usuario_a},
        ]
    }
    parts: list[dict[str, Any]] = [_filtro_no_grupo(), dir_dm]
    if before_id is not None:
        _require_oid(before_id, "before_id")
        parts.append({"_id": {"$lt": ObjectId(before_id)}})
    filtro: dict[str, Any] = {"$and": parts}

    mensajes: list[dict[str, Any]] = []
    cursor = db.mensajes.find(filtro).sort("_id", -1).limit(lim)
    async for msg in cursor:
        mensajes.append(_serialize_doc(msg))

    next_before = mensajes[-1]["_id"] if len(mensajes) == lim else None
    return {"items": mensajes, "next_before_id": next_before, "limit": lim}


async def mensajes_por_grupo(
    grupo_id: str, limit: int = 50, before_id: str | None = None
):
    _require_oid(grupo_id, "grupo_id")
    lim = _clamp_limit(limit)
    filtro: dict[str, Any] = {"tipo": TIPO_GRUPO, "grupo_id": grupo_id}
    if before_id is not None:
        _require_oid(before_id, "before_id")
        filtro = {"$and": [filtro, {"_id": {"$lt": ObjectId(before_id)}}]}

    mensajes: list[dict[str, Any]] = []
    cursor = db.mensajes.find(filtro).sort("_id", -1).limit(lim)
    async for msg in cursor:
        mensajes.append(_serialize_doc(msg))

    next_before = mensajes[-1]["_id"] if len(mensajes) == lim else None
    return {"items": mensajes, "next_before_id": next_before, "limit": lim}
