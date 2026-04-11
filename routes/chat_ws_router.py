# routers/chat_ws_router.py

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from core.connection_manager import ConnectionManager
from services.mensaje_service import enviar_mensaje

router = APIRouter()
manager = ConnectionManager()

@router.websocket("/ws/chat/{user_id}/{receptor_id}")
async def chat(websocket: WebSocket, user_id: int, receptor_id: int):
    await manager.connect(user_id, websocket)

    try:
        while True:
            data = await websocket.receive_text()

            if not data.strip():
                continue

            contenido = data.strip()

            await enviar_mensaje(user_id, contenido)

            await manager.send_to_user(receptor_id, f"{user_id}: {contenido}")

            await websocket.send_text("enviado")

    except WebSocketDisconnect:
        manager.disconnect(user_id)