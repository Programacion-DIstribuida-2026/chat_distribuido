import logging
from typing import Dict

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, user_id: str, websocket: WebSocket) -> None:
        await websocket.accept()

        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].close()
            except Exception as exc:
                logger.warning("No se pudo cerrar WebSocket previo de %s: %s", user_id, exc)

        self.active_connections[user_id] = websocket
        logger.info("Usuario %s conectado por WebSocket", user_id)

    def disconnect(self, user_id: str) -> None:
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            logger.info("Usuario %s desconectado", user_id)

    async def send_to_user(self, user_id: str, message: str) -> None:
        websocket = self.active_connections.get(user_id)

        if websocket:
            try:
                await websocket.send_text(message)
            except Exception as exc:
                logger.warning("Fallo envío a %s: %s", user_id, exc)
                self.disconnect(user_id)

    async def broadcast(self, message: str) -> None:
        disconnected_users: list[str] = []

        for user_id, websocket in self.active_connections.items():
            try:
                await websocket.send_text(message)
            except Exception as exc:
                logger.warning("Fallo broadcast a %s: %s", user_id, exc)
                disconnected_users.append(user_id)

        for user_id in disconnected_users:
            self.disconnect(user_id)
