from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
import jwt
from pymongo.errors import DuplicateKeyError
from bson import ObjectId

from database import db
from models.schemas import RegistroUsuario
from services.phone_utils import normalizar_telefono_e164

_BCRYPT_MAX = 72


# =========================
# ERRORS
# =========================

class AuthConflictError(Exception):
    pass


class AuthInvalidTokenError(Exception):
    pass


class AuthUserNotFoundError(Exception):
    pass


# =========================
# JWT
# =========================

def _jwt_secret() -> str:
    secret = os.environ.get("JWT_SECRET", "").strip()
    if len(secret) < 16:
        raise RuntimeError("JWT_SECRET inválido")
    return secret


def _jwt_expire_minutes() -> int:
    raw = os.environ.get("JWT_EXPIRE_MINUTES", "10080").strip()
    try:
        return int(raw)
    except ValueError:
        return 10080


def emitir_access_token(user_id: str) -> str:
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=_jwt_expire_minutes())

    payload = {
        "sub": user_id,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }

    return jwt.encode(payload, _jwt_secret(), algorithm="HS256")


def decodificar_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(token, _jwt_secret(), algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise AuthInvalidTokenError("Token expirado")
    except jwt.InvalidTokenError:
        raise AuthInvalidTokenError("Token inválido")


# =========================
# PASSWORD
# =========================

def _password_bytes(plain: str) -> bytes:
    return plain.encode("utf-8")[:_BCRYPT_MAX]


def _hash_password(plain: str) -> str:
    return bcrypt.hashpw(_password_bytes(plain), bcrypt.gensalt()).decode("ascii")


def _verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(_password_bytes(plain), hashed.encode("ascii"))


# =========================
# SERIALIZER
# =========================

def _to_public(doc: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": str(doc["_id"]),
        "nombre": doc.get("nombre", ""),
        "username": doc.get("username"),
        "email": doc.get("email"),
        "telefono_e164": doc.get("telefono_e164"),
    }


# =========================
# REGISTER
# =========================

async def registrar(body: RegistroUsuario) -> dict[str, Any]:
    email = body.email.strip().lower()
    username = body.username.strip().lower()
    telefono = normalizar_telefono_e164(body.codigo_pais, body.numero)

    doc = {
        "nombre": body.nombre.strip(),
        "username": username,
        "email": email,
        "telefono_e164": telefono,
        "password_hash": _hash_password(body.password),
        "creado_en": datetime.now(timezone.utc),
    }

    try:
        result = await db.usuarios.insert_one(doc)
    except DuplicateKeyError:
        raise AuthConflictError("Usuario ya existe")

    doc["_id"] = result.inserted_id

    return {
        "access_token": emitir_access_token(str(result.inserted_id)),
        "token_type": "bearer",
        "user": _to_public(doc),
    }


# =========================
# LOGIN
# =========================

async def login_por_email(email: str, password: str) -> dict[str, Any] | None:
    doc = await db.usuarios.find_one({"email": email.strip().lower()})

    if not doc:
        return None

    if not _verify_password(password, doc["password_hash"]):
        return None

    return {
        "access_token": emitir_access_token(str(doc["_id"])),
        "token_type": "bearer",
        "user": _to_public(doc),
    }


# =========================
# ME 
# =========================

async def obtener_usuario_por_token(token: str) -> dict[str, Any]:
    payload = decodificar_token(token)

    user_id = payload.get("sub")
    if not user_id:
        raise AuthInvalidTokenError("Token sin sub")

    user = await db.usuarios.find_one({"_id": ObjectId(user_id)})

    if not user:
        raise AuthUserNotFoundError("Usuario no encontrado")

    return _to_public(user)