from fastapi import APIRouter, HTTPException, Response, status

from models.schemas import ContactoActualizar, ContactoCrear
from routes.deps import ObjectIdPath
from services import contacto_service
from services.contacto_service import ContactoDuplicateError

router = APIRouter()


@router.post("/usuarios/{owner_id}/contactos", tags=["Contactos"], status_code=status.HTTP_201_CREATED)
async def crear_contacto(owner_id: ObjectIdPath, body: ContactoCrear):
    try:
        return await contacto_service.crear_contacto(owner_id, body)
    except ContactoDuplicateError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)) from e
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.patch("/usuarios/{owner_id}/contactos/{contacto_id}", tags=["Contactos"])
async def actualizar_contacto(
    owner_id: ObjectIdPath,
    contacto_id: ObjectIdPath,
    body: ContactoActualizar,
):
    try:
        doc = await contacto_service.actualizar_contacto(owner_id, contacto_id, body)
    except ContactoDuplicateError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)) from e
    if doc is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contacto no encontrado")
    return doc


@router.get("/usuarios/{owner_id}/contactos", tags=["Contactos"])
async def listar_contactos(owner_id: ObjectIdPath):
    try:
        return await contacto_service.listar_por_owner(owner_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)) from e


@router.delete(
    "/usuarios/{owner_id}/contactos/{contacto_id}",
    tags=["Contactos"],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def eliminar_contacto(
    owner_id: ObjectIdPath,
    contacto_id: ObjectIdPath,
):
    try:
        ok = await contacto_service.eliminar_contacto(owner_id, contacto_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)) from e
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contacto no encontrado")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
