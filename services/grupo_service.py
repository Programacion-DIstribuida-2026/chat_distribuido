from datetime import datetime, timezone
from typing import Any

from bson import ObjectId

from database import db

ROL_ADMIN = "admin"
ROL_MIEMBRO = "miembro"


def _require_oid(value: str, field: str) -> None:
    if not ObjectId.is_valid(value):
        raise ValueError(f"{field} no es un ObjectId válido de MongoDB.")


def _serialize_grupo(doc: dict[str, Any]) -> dict[str, Any]:
    out = dict(doc)
    out["_id"] = str(out["_id"])
    return out


async def es_miembro(grupo_id: str, usuario_id: str) -> bool:
    _require_oid(grupo_id, "grupo_id")
    _require_oid(usuario_id, "usuario_id")
    doc = await db.grupo_miembros.find_one(
        {"grupo_id": grupo_id, "usuario_id": usuario_id}
    )
    return doc is not None


async def es_admin(grupo_id: str, usuario_id: str) -> bool:
    doc = await db.grupo_miembros.find_one(
        {"grupo_id": grupo_id, "usuario_id": usuario_id}
    )
    return bool(doc and doc.get("rol") == ROL_ADMIN)


async def crear_grupo(nombre: str, creado_por: str) -> dict[str, Any]:
    _require_oid(creado_por, "creado_por")
    now = datetime.now(timezone.utc)
    doc = {
        "nombre": nombre.strip(),
        "creado_por": creado_por,
        "creado_en": now,
    }
    res = await db.grupos.insert_one(doc)
    gid = str(res.inserted_id)
    await db.grupo_miembros.insert_one(
        {
            "grupo_id": gid,
            "usuario_id": creado_por,
            "rol": ROL_ADMIN,
            "unido_en": now,
        }
    )
    return {"id": gid, "nombre": doc["nombre"], "creado_por": creado_por}


async def obtener_grupo(grupo_id: str) -> dict[str, Any] | None:
    _require_oid(grupo_id, "grupo_id")
    g = await db.grupos.find_one({"_id": ObjectId(grupo_id)})
    if not g:
        return None
    return _serialize_grupo(g)


async def listar_grupos_por_usuario(usuario_id: str) -> list[dict[str, Any]]:
    _require_oid(usuario_id, "usuario_id")
    cursor = db.grupo_miembros.find({"usuario_id": usuario_id})
    gids: list[str] = []
    async for m in cursor:
        gids.append(m["grupo_id"])
    if not gids:
        return []
    oids = [ObjectId(g) for g in gids if ObjectId.is_valid(g)]
    out: list[dict[str, Any]] = []
    async for g in db.grupos.find({"_id": {"$in": oids}}):
        out.append(_serialize_grupo(g))
    return out


async def listar_miembros(grupo_id: str) -> list[dict[str, Any]]:
    _require_oid(grupo_id, "grupo_id")
    miembros: list[dict[str, Any]] = []
    async for m in db.grupo_miembros.find({"grupo_id": grupo_id}):
        m2 = dict(m)
        m2["_id"] = str(m2["_id"])
        miembros.append(m2)
    return miembros


async def agregar_miembro(
    grupo_id: str, usuario_nuevo: str, actor_id: str
) -> dict[str, Any]:
    _require_oid(grupo_id, "grupo_id")
    _require_oid(usuario_nuevo, "usuario_id")
    _require_oid(actor_id, "actor_id")
    if not await es_admin(grupo_id, actor_id):
        raise PermissionError("Solo un administrador del grupo puede añadir miembros.")
    if await es_miembro(grupo_id, usuario_nuevo):
        raise ValueError("El usuario ya es miembro del grupo.")
    now = datetime.now(timezone.utc)
    res = await db.grupo_miembros.insert_one(
        {
            "grupo_id": grupo_id,
            "usuario_id": usuario_nuevo,
            "rol": ROL_MIEMBRO,
            "unido_en": now,
        }
    )
    return {"id": str(res.inserted_id), "grupo_id": grupo_id, "usuario_id": usuario_nuevo}


async def eliminar_miembro(grupo_id: str, objetivo_usuario_id: str, actor_id: str) -> bool:
    _require_oid(grupo_id, "grupo_id")
    _require_oid(objetivo_usuario_id, "usuario_id")
    _require_oid(actor_id, "actor_id")
    if actor_id == objetivo_usuario_id:
        if await es_admin(grupo_id, actor_id):
            admins = await db.grupo_miembros.count_documents(
                {"grupo_id": grupo_id, "rol": ROL_ADMIN}
            )
            if admins <= 1:
                raise ValueError(
                    "No puedes salir siendo el único administrador; asigna otro admin primero."
                )
        r = await db.grupo_miembros.delete_one(
            {"grupo_id": grupo_id, "usuario_id": objetivo_usuario_id}
        )
        return r.deleted_count > 0
    if not await es_admin(grupo_id, actor_id):
        raise PermissionError("Solo un administrador puede expulsar miembros.")
    r = await db.grupo_miembros.delete_one(
        {"grupo_id": grupo_id, "usuario_id": objetivo_usuario_id}
    )
    return r.deleted_count > 0


async def ids_grupos_de_usuario(usuario_id: str) -> list[str]:
    if not ObjectId.is_valid(usuario_id):
        return []
    cursor = db.grupo_miembros.find({"usuario_id": usuario_id}, projection={"grupo_id": 1})
    return [m["grupo_id"] async for m in cursor]
