from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from core.connection_manager import ConnectionManager
from services.mensaje_service import enviar_mensaje

router = APIRouter()
manager = ConnectionManager()


def _validate_ws_oid(label: str, value: str) -> str:
    v = value.strip().lower()
    if len(v) != 24 or any(c not in "0123456789abcdef" for c in v):
        raise ValueError(f"{label} debe ser un ObjectId hexadecimal de 24 caracteres.")
    return v


@router.websocket("/ws/chat/{user_id}/{receptor_id}")
async def chat(websocket: WebSocket, user_id: str, receptor_id: str):
    try:
        user_id = _validate_ws_oid("user_id", user_id)
        receptor_id = _validate_ws_oid("receptor_id", receptor_id)
    except ValueError:
        await websocket.close(code=4400)
        return

    await manager.connect(user_id, websocket)

    try:
        while True:
            data = await websocket.receive_text()

            if not data.strip():
                continue

            contenido = data.strip()

            await enviar_mensaje(user_id, receptor_id, contenido)

            await manager.send_to_user(receptor_id, f"{user_id}: {contenido}")

            await websocket.send_text("enviado")

    except WebSocketDisconnect:
        manager.disconnect(user_id)
