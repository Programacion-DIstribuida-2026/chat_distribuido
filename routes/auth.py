from fastapi import (
    APIRouter,
    HTTPException,
    status,
    Depends,
)
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from models.schemas import AuthTokenResponse, LoginUsuario, RegistroUsuario
from services.auth_service import (
    AuthConflictError,
    login_por_email,
    registrar,
    obtener_usuario_por_token,
)

router = APIRouter()
security = HTTPBearer()


# =========================
# REGISTER
# =========================
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
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e),
        ) from e

    except AuthConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        ) from e

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        ) from e

    return data


# =========================
# LOGIN
# =========================
@router.post(
    "/auth/login",
    response_model=AuthTokenResponse,
    tags=["Auth"],
)
async def login(body: LoginUsuario):
    try:
        data = await login_por_email(body.email, body.password)

    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e),
        ) from e

    if data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas.",
        )

    return data


# =========================
# ME (TOKEN → USER)
# =========================
@router.get("/auth/me", tags=["Auth"])
async def me(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    return await obtener_usuario_por_token(credentials.credentials)