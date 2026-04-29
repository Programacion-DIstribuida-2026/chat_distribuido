"""Registro en memoria de WebSockets por sala (DM o grupo) para broadcast local."""

from __future__ import annotations

import asyncio
import logging
from typing import Dict, Set

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class RealtimeHub:
    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._rooms: Dict[str, Set[WebSocket]] = {}
        self._conn_meta: Dict[int, dict] = {}

    async def bind_user(self, ws: WebSocket, user_id: str) -> None:
        async with self._lock:
            self._conn_meta[id(ws)] = {"user": user_id, "rooms": set()}

    def get_user_for_ws(self, ws: WebSocket) -> str | None:
        meta = self._conn_meta.get(id(ws))
        return meta["user"] if meta else None

    async def join_room(self, ws: WebSocket, room_key: str) -> None:
        async with self._lock:
            self._rooms.setdefault(room_key, set()).add(ws)
            meta = self._conn_meta.setdefault(id(ws), {"user": None, "rooms": set()})
            meta["rooms"].add(room_key)

    async def leave_room(self, ws: WebSocket, room_key: str) -> None:
        async with self._lock:
            subs = self._rooms.get(room_key)
            if subs and ws in subs:
                subs.discard(ws)
                if not subs:
                    self._rooms.pop(room_key, None)
            meta = self._conn_meta.get(id(ws))
            if meta:
                meta["rooms"].discard(room_key)

    async def disconnect(self, ws: WebSocket) -> None:
        async with self._lock:
            meta = self._conn_meta.pop(id(ws), None)
            if not meta:
                return
            for rk in list(meta["rooms"]):
                subs = self._rooms.get(rk)
                if subs:
                    subs.discard(ws)
                    if not subs:
                        self._rooms.pop(rk, None)

    async def deliver_to_room(self, room_key: str, text: str) -> None:
        async with self._lock:
            subscribers = list(self._rooms.get(room_key, set()))
        for ws in subscribers:
            try:
                await ws.send_text(text)
            except Exception as exc:
                logger.debug("Fallo send_text a cliente WS: %s", exc)
                await self.disconnect(ws)


_hub = RealtimeHub()


def get_realtime_hub() -> RealtimeHub:
    return _hub
