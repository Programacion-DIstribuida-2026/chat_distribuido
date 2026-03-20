# routers/chat_ws_router.py

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from core.connection_manager import ConnectionManager
from services.mensaje_service import enviar_mensaje
import json

router = APIRouter()
manager = ConnectionManager()

@router.websocket("/ws/chat/{user_id}")
async def chat(websocket: WebSocket, user_id: int):
    await manager.connect(user_id, websocket)

    try:
        while True:
            data = await websocket.receive_text()
            mensaje = json.loads(data)

            # mensaje debe traer: receptor_id
            receptor_id = mensaje["receptor_id"]

            # guardar en BD
            await enviar_mensaje(user_id, mensaje["contenido"])

            # enviar SOLO al receptor
            await manager.send_to_user(receptor_id, json.dumps({
                "from": user_id,
                "mensaje": mensaje["contenido"]
            }))

    except WebSocketDisconnect:
        manager.disconnect(user_id)