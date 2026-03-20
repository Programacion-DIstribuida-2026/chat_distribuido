from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, WebSocket] = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()

        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].close()
            except Exception:
                pass

        self.active_connections[user_id] = websocket
        print(f"Usuario {user_id} conectado")

    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            print(f"Usuario {user_id} desconectado")

    async def send_to_user(self, user_id: int, message: str):
        websocket = self.active_connections.get(user_id)

        if websocket:
            try:
                await websocket.send_text(message)
            except Exception:
                self.disconnect(user_id)

    async def broadcast(self, message: str):
        disconnected_users = []

        for user_id, websocket in self.active_connections.items():
            try:
                await websocket.send_text(message)
            except Exception:
                disconnected_users.append(user_id)

        for user_id in disconnected_users:
            self.disconnect(user_id)