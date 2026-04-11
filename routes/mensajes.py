from fastapi import APIRouter
from services.mensaje_service import enviar_mensaje, listar_mensajes, mensajes_por_usuario
from models.schemas import Mensaje

router = APIRouter()

@router.post("/mensajes", tags=["Mensajes"])
async def enviar(mensaje: Mensaje):
    return await enviar_mensaje(mensaje.id_usuario, mensaje.contenido)

@router.get("/mensajes", tags=["Mensajes"])
async def listar():
    return await listar_mensajes()

@router.get("/mensajes/{id_usuario}", tags=["Mensajes"])
async def por_usuario(id_usuario: int):
    return await mensajes_por_usuario(id_usuario)