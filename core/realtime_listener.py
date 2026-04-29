"""Tarea en segundo plano: escucha Redis PSUBSCRIBE y entrega al hub local."""

from __future__ import annotations

import asyncio
import logging

from core.realtime_hub import get_realtime_hub
from core.redis_client import redis_client

logger = logging.getLogger(__name__)

_task: asyncio.Task[None] | None = None


async def _listener_loop() -> None:
    r = redis_client()
    if r is None:
        return
    pubsub = r.pubsub()
    await pubsub.psubscribe("grupo:*", "dm:*")
    hub = get_realtime_hub()
    try:
        async for message in pubsub.listen():
            if message["type"] != "pmessage":
                continue
            channel = message.get("channel")
            data = message.get("data")
            if isinstance(channel, bytes):
                channel = channel.decode()
            if isinstance(data, bytes):
                data = data.decode()
            if channel and isinstance(data, str):
                await hub.deliver_to_room(channel, data)
    except asyncio.CancelledError:
        try:
            await pubsub.punsubscribe()
            await pubsub.aclose()
        except Exception as exc:
            logger.debug("Cierre pubsub: %s", exc)
        raise


def start_redis_listener_task() -> asyncio.Task[None] | None:
    global _task
    if redis_client() is None:
        logger.info("Redis no disponible: no se inicia listener Pub/Sub.")
        return None
    if _task is not None and not _task.done():
        return _task
    _task = asyncio.create_task(_listener_loop(), name="redis_realtime_listener")
    logger.info("Listener Redis Pub/Sub iniciado (grupo:*, dm:*).")
    return _task


async def stop_redis_listener_task() -> None:
    global _task
    if _task is None:
        return
    _task.cancel()
    try:
        await _task
    except asyncio.CancelledError:
        pass
    _task = None
