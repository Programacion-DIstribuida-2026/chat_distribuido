from fastapi import APIRouter, HTTPException, Response, status

from models.schemas import Usuario, UsuarioActualizar
from routes.deps import ObjectIdPath
from services.usuario_service import (
    actualizar_usuario,
    crear_usuario,
    eliminar_usuario,
    listar_usuarios,
    obtener_usuario,
)

router = APIRouter()


@router.post("/usuarios", tags=["Usuarios"])
async def crear(usuario: Usuario):
    return await crear_usuario(usuario.nombre)


@router.get("/usuarios", tags=["Usuarios"])
async def listar():
    return await listar_usuarios()


@router.get("/usuarios/{id}", tags=["Usuarios"])
async def obtener(id: ObjectIdPath):
    usuario = await obtener_usuario(id)
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


@router.patch("/usuarios/{id}", tags=["Usuarios"])
async def actualizar(id: ObjectIdPath, body: UsuarioActualizar):
    try:
        usuario = await actualizar_usuario(id, body.nombre)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


@router.delete("/usuarios/{id}", tags=["Usuarios"])
async def eliminar(id: ObjectIdPath):
    ok = await eliminar_usuario(id)
    if not ok:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
