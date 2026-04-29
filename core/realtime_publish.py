"""Publicación de eventos de tiempo real: Redis PUBLISH o broadcast local."""

from __future__ import annotations

import json
import logging
from typing import Any

from core.realtime_hub import get_realtime_hub
from core.redis_client import redis_client

logger = logging.getLogger(__name__)


async def publish_or_local(room_key: str, event: dict[str, Any]) -> None:
    body = json.dumps(event, ensure_ascii=False)
    r = redis_client()
    if r is not None:
        try:
            await r.publish(room_key, body)
        except Exception as exc:
            logger.warning("Redis publish falló, broadcast local: %s", exc)
            await get_realtime_hub().deliver_to_room(room_key, body)
    else:
        await get_realtime_hub().deliver_to_room(room_key, body)
