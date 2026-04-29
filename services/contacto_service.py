"""Agenda de contactos por propietario (`owner_id`)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from bson import ObjectId
from pymongo.errors import DuplicateKeyError

from database import db
from models.schemas import ContactoActualizar, ContactoCrear
from services.phone_utils import normalizar_telefono_e164


class ContactoDuplicateError(Exception):
    """Mismo teléfono ya en la agenda del propietario."""

    pass


def _serialize(doc: dict[str, Any]) -> dict[str, Any]:
    out = dict(doc)
    out["_id"] = str(out["_id"])
    return out


async def crear_contacto(owner_id: str, body: ContactoCrear) -> dict[str, Any]:
    if not ObjectId.is_valid(owner_id):
        raise ValueError("owner_id no es un ObjectId válido de MongoDB.")
    owner = await db.usuarios.find_one({"_id": ObjectId(owner_id)}, projection={"_id": 1})
    if not owner:
        raise LookupError("Usuario propietario no encontrado.")

    telefono_e164 = normalizar_telefono_e164(body.codigo_pais, body.numero)
    doc = {
        "owner_id": owner_id,
        "nombre": body.nombre.strip(),
        "telefono_e164": telefono_e164,
        "creado_en": datetime.now(timezone.utc),
    }
    try:
        res = await db.contactos.insert_one(doc)
    except DuplicateKeyError as e:
        raise ContactoDuplicateError(
            "Ya existe un contacto con ese número en tu agenda."
        ) from e
    doc["_id"] = res.inserted_id
    return _serialize(doc)


async def actualizar_contacto(
    owner_id: str, contacto_id: str, body: ContactoActualizar
) -> dict[str, Any] | None:
    if not ObjectId.is_valid(owner_id) or not ObjectId.is_valid(contacto_id):
        raise ValueError("Identificador no es un ObjectId válido de MongoDB.")
    cid = ObjectId(contacto_id)
    existing = await db.contactos.find_one({"_id": cid, "owner_id": owner_id})
    if not existing:
        return None

    updates: dict[str, Any] = {}
    if body.nombre is not None:
        updates["nombre"] = body.nombre.strip()
    if body.codigo_pais is not None and body.numero is not None:
        updates["telefono_e164"] = normalizar_telefono_e164(
            body.codigo_pais, body.numero
        )
    if not updates:
        return _serialize(existing)

    try:
        result = await db.contactos.update_one(
            {"_id": cid, "owner_id": owner_id}, {"$set": updates}
        )
    except DuplicateKeyError as e:
        raise ContactoDuplicateError(
            "Ya existe un contacto con ese número en tu agenda."
        ) from e
    if result.matched_count == 0:
        return None
    doc = await db.contactos.find_one({"_id": cid})
    if not doc:
        return None
    return _serialize(doc)


async def listar_por_owner(owner_id: str) -> list[dict[str, Any]]:
    if not ObjectId.is_valid(owner_id):
        raise ValueError("owner_id no es un ObjectId válido de MongoDB.")
    out: list[dict[str, Any]] = []
    cursor = db.contactos.find({"owner_id": owner_id}).sort(
        [("creado_en", -1), ("_id", -1)]
    )
    async for doc in cursor:
        out.append(_serialize(doc))
    return out


async def eliminar_contacto(owner_id: str, contacto_id: str) -> bool:
    if not ObjectId.is_valid(owner_id) or not ObjectId.is_valid(contacto_id):
        raise ValueError("Identificador no es un ObjectId válido de MongoDB.")
    result = await db.contactos.delete_one(
        {"_id": ObjectId(contacto_id), "owner_id": owner_id}
    )
    return result.deleted_count > 0
