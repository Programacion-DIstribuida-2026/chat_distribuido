"""Cliente Redis asíncrono para healthcheck y futuras extensiones (pub/sub, rate limit)."""

import logging
import os
from typing import Optional

import redis.asyncio as redis

logger = logging.getLogger(__name__)

_redis: Optional[redis.Redis] = None


def get_redis_url() -> Optional[str]:
    return os.environ.get("REDIS_URL")


async def connect_redis() -> None:
    global _redis
    url = get_redis_url()
    if not url:
        logger.info("REDIS_URL no definida; Redis deshabilitado.")
        return
    try:
        _redis = redis.from_url(url, encoding="utf-8", decode_responses=True)
        await _redis.ping()
        logger.info("Redis conectado correctamente.")
    except Exception as exc:
        logger.warning("No se pudo conectar a Redis: %s", exc)
        _redis = None


async def disconnect_redis() -> None:
    global _redis
    if _redis is not None:
        try:
            await _redis.aclose()
        except Exception as exc:
            logger.warning("Error al cerrar Redis: %s", exc)
        _redis = None


def redis_client() -> Optional[redis.Redis]:
    return _redis


async def ping_redis() -> bool:
    if _redis is None:
        return False
    try:
        return bool(await _redis.ping())
    except Exception:
        return False
