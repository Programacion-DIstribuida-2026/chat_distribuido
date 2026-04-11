from fastapi import APIRouter
from services.usuario_service import crear_usuario, listar_usuarios, obtener_usuario
from models.schemas import Usuario

router = APIRouter()

@router.post("/usuarios", tags=["Usuarios"])
async def crear(usuario: Usuario):
    return await crear_usuario(usuario.nombre)

@router.get("/usuarios", tags=["Usuarios"])
async def listar():
    return await listar_usuarios()

@router.get("/usuarios/{id}", tags=["Usuarios"])
async def obtener(id: int):
    return await obtener_usuario(id)