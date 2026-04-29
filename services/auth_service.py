"""Registro e inicio de sesión (hash bcrypt + JWT HS256)."""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
import jwt
from pymongo.errors import DuplicateKeyError

from database import db
from models.schemas import RegistroUsuario
from services.phone_utils import normalizar_telefono_e164

_BCRYPT_MAX = 72


class AuthConflictError(Exception):
    """Email, username o teléfono ya registrado."""

    pass


def _jwt_secret() -> str:
    secret = os.environ.get("JWT_SECRET", "").strip()
    if len(secret) < 16:
        raise RuntimeError(
            "JWT_SECRET no definida o demasiado corta (mínimo 16 caracteres). "
            "Configúrala en .env para usar /auth/register y /auth/login."
        )
    return secret


def _jwt_expire_minutes() -> int:
    raw = os.environ.get("JWT_EXPIRE_MINUTES", "10080").strip()
    try:
        n = int(raw)
    except ValueError:
        return 10080
    return max(5, min(n, 525600))


def _password_bytes(plain: str) -> bytes:
    """bcrypt solo usa los primeros 72 bytes UTF-8."""
    return plain.encode("utf-8")[:_BCRYPT_MAX]


def _hash_password(plain: str) -> str:
    return bcrypt.hashpw(_password_bytes(plain), bcrypt.gensalt()).decode("ascii")


def _verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(
            _password_bytes(plain),
            hashed.encode("ascii"),
        )
    except (ValueError, TypeError):
        return False


def emitir_access_token(user_id: str) -> str:
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=_jwt_expire_minutes())
    payload: dict[str, Any] = {
        "sub": user_id,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }
    return jwt.encode(payload, _jwt_secret(), algorithm="HS256")


def _doc_to_public(doc: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": str(doc["_id"]),
        "nombre": doc.get("nombre", ""),
        "username": doc.get("username"),
        "email": doc.get("email"),
        "telefono_e164": doc.get("telefono_e164"),
    }


async def registrar(body: RegistroUsuario) -> dict[str, Any]:
    _jwt_secret()
    email = body.email.strip().lower()
    username = body.username.strip().lower()
    telefono_e164 = normalizar_telefono_e164(body.codigo_pais, body.numero)

    doc = {
        "nombre": body.nombre.strip(),
        "username": username,
        "email": email,
        "telefono_e164": telefono_e164,
        "password_hash": _hash_password(body.password),
        "creado_en": datetime.now(timezone.utc),
    }
    try:
        result = await db.usuarios.insert_one(doc)
    except DuplicateKeyError as e:
        raise AuthConflictError(
            "Ya existe una cuenta con ese correo, usuario o teléfono."
        ) from e

    doc["_id"] = result.inserted_id
    token = emitir_access_token(str(result.inserted_id))
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": _doc_to_public(doc),
    }


async def login_por_email(email: str, password: str) -> dict[str, Any] | None:
    _jwt_secret()
    normalized = email.strip().lower()
    doc = await db.usuarios.find_one({"email": normalized})
    if not doc:
        return None
    hashed = doc.get("password_hash")
    if not hashed or not isinstance(hashed, str):
        return None
    if not _verify_password(password, hashed):
        return None
    token = emitir_access_token(str(doc["_id"]))
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": _doc_to_public(doc),
    }
