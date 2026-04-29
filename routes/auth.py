from fastapi import APIRouter, HTTPException, status

from models.schemas import AuthTokenResponse, LoginUsuario, RegistroUsuario
from services.auth_service import AuthConflictError, login_por_email, registrar

router = APIRouter()


@router.post(
    "/auth/register",
    response_model=AuthTokenResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Auth"],
)
async def register(body: RegistroUsuario):
    try:
        data = await registrar(body)
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e)
        ) from e
    except AuthConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)) from e
    return data


@router.post("/auth/login", response_model=AuthTokenResponse, tags=["Auth"])
async def login(body: LoginUsuario):
    try:
        data = await login_por_email(body.email, body.password)
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e)
        ) from e
    if data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas.",
        )
    return data
