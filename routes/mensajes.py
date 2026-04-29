from fastapi import APIRouter, HTTPException, Query

from models.schemas import Mensaje
from routes.deps import ObjectIdPath
from services.mensaje_service import (
    enviar_mensaje,
    listar_mensajes,
    mensajes_entre_usuarios,
    mensajes_por_usuario,
)

router = APIRouter()


@router.post("/mensajes", tags=["Mensajes"])
async def enviar(mensaje: Mensaje):
    try:
        return await enviar_mensaje(
            mensaje.remitente_id,
            mensaje.destinatario_id,
            mensaje.contenido,
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e


@router.get(
    "/mensajes/conversacion/{usuario_a}/{usuario_b}",
    tags=["Mensajes"],
    summary="Mensajes entre dos usuarios (1:1)",
)
async def conversacion(
    usuario_a: ObjectIdPath,
    usuario_b: ObjectIdPath,
    limit: int = Query(50, ge=1, le=200, description="Tamaño de página."),
    before_id: str | None = Query(
        default=None,
        pattern="^[a-fA-F0-9]{24}$",
        description="ObjectId del mensaje; devuelve mensajes más antiguos que este.",
    ),
):
    try:
        return await mensajes_entre_usuarios(usuario_a, usuario_b, limit, before_id)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e


@router.get("/mensajes", tags=["Mensajes"])
async def listar(
    limit: int = Query(50, ge=1, le=200, description="Tamaño de página."),
    before_id: str | None = Query(
        default=None,
        pattern="^[a-fA-F0-9]{24}$",
        description="ObjectId del mensaje; devuelve mensajes más antiguos que este.",
    ),
):
    try:
        return await listar_mensajes(limit, before_id)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e


@router.get("/mensajes/{id_usuario}", tags=["Mensajes"])
async def por_usuario(
    id_usuario: ObjectIdPath,
    limit: int = Query(50, ge=1, le=200, description="Tamaño de página."),
    before_id: str | None = Query(
        default=None,
        pattern="^[a-fA-F0-9]{24}$",
        description="ObjectId del mensaje; devuelve mensajes más antiguos que este.",
    ),
):
    try:
        return await mensajes_por_usuario(id_usuario, limit, before_id)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
