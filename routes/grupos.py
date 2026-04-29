from fastapi import APIRouter, HTTPException, Query, Response, status

from models.schemas import GrupoCrear, GrupoMiembroCrear, MensajeGrupoCrear

_OID_QUERY = "^[a-fA-F0-9]{24}$"
from routes.deps import ObjectIdPath
from services import grupo_service
from services.mensaje_service import enviar_mensaje_grupo, mensajes_por_grupo

router = APIRouter()


@router.post("/grupos", tags=["Grupos"])
async def crear_grupo(body: GrupoCrear):
    try:
        return await grupo_service.crear_grupo(body.nombre, body.creado_por)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e


@router.get("/grupos", tags=["Grupos"])
async def listar_grupos(usuario_id: str | None = Query(default=None, pattern=_OID_QUERY)):
    if not usuario_id:
        raise HTTPException(
            status_code=422,
            detail="Indique query usuario_id (ObjectId) para listar sus grupos.",
        )
    try:
        return await grupo_service.listar_grupos_por_usuario(usuario_id)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e


@router.get("/grupos/{grupo_id}", tags=["Grupos"])
async def obtener_grupo(grupo_id: ObjectIdPath):
    g = await grupo_service.obtener_grupo(grupo_id)
    if not g:
        raise HTTPException(status_code=404, detail="Grupo no encontrado")
    return g


@router.get("/grupos/{grupo_id}/miembros", tags=["Grupos"])
async def listar_miembros(grupo_id: ObjectIdPath):
    try:
        return await grupo_service.listar_miembros(grupo_id)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e


@router.post("/grupos/{grupo_id}/miembros", tags=["Grupos"])
async def agregar_miembro(grupo_id: ObjectIdPath, body: GrupoMiembroCrear):
    try:
        return await grupo_service.agregar_miembro(
            grupo_id, body.usuario_id, body.actor_id
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e)) from e


@router.delete(
    "/grupos/{grupo_id}/miembros/{usuario_id}",
    tags=["Grupos"],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def quitar_miembro(
    grupo_id: ObjectIdPath,
    usuario_id: ObjectIdPath,
    actor_id: str = Query(..., pattern=_OID_QUERY),
):
    try:
        ok = await grupo_service.eliminar_miembro(grupo_id, usuario_id, actor_id)
        if not ok:
            raise HTTPException(status_code=404, detail="Miembro no encontrado")
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e)) from e


@router.get("/grupos/{grupo_id}/mensajes", tags=["Grupos"])
async def mensajes_grupo(
    grupo_id: ObjectIdPath,
    limit: int = Query(50, ge=1, le=200),
    before_id: str | None = Query(
        default=None,
        pattern="^[a-fA-F0-9]{24}$",
    ),
):
    try:
        return await mensajes_por_grupo(grupo_id, limit, before_id)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e


@router.post("/grupos/{grupo_id}/mensajes", tags=["Grupos"])
async def enviar_mensaje_grupo_route(grupo_id: ObjectIdPath, body: MensajeGrupoCrear):
    try:
        return await enviar_mensaje_grupo(
            body.remitente_id, grupo_id, body.contenido
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e)) from e
