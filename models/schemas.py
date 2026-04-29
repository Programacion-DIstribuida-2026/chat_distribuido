from pydantic import BaseModel, EmailStr, Field

_OID24 = "^[a-fA-F0-9]{24}$"
_CODIGO_PAIS = r"^\+\d{1,4}$"


class Usuario(BaseModel):
    nombre: str = Field(min_length=1, max_length=200)


class UsuarioActualizar(BaseModel):
    nombre: str = Field(min_length=1, max_length=200)


class Mensaje(BaseModel):
    remitente_id: str = Field(pattern=_OID24)
    destinatario_id: str = Field(pattern=_OID24)
    contenido: str = Field(min_length=1, max_length=8000)


class GrupoCrear(BaseModel):
    nombre: str = Field(min_length=1, max_length=200)
    creado_por: str = Field(pattern=_OID24)


class GrupoMiembroCrear(BaseModel):
    """Quién añade (`actor_id`) debe ser admin del grupo."""

    usuario_id: str = Field(pattern=_OID24)
    actor_id: str = Field(pattern=_OID24)


class MensajeGrupoCrear(BaseModel):
    remitente_id: str = Field(pattern=_OID24)
    contenido: str = Field(min_length=1, max_length=8000)


class RegistroUsuario(BaseModel):
    """Registro alineado al mockup (paso nombre/usuario/email + paso teléfono/contraseña)."""

    nombre: str = Field(min_length=1, max_length=200)
    username: str = Field(min_length=2, max_length=64, pattern=r"^[a-zA-Z0-9_]+$")
    email: EmailStr
    codigo_pais: str = Field(pattern=_CODIGO_PAIS)
    numero: str = Field(
        min_length=7,
        max_length=20,
        description="Solo dígitos o con espacios; se normaliza en el servidor.",
    )
    password: str = Field(min_length=8, max_length=72)


class LoginUsuario(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=200)


class UsuarioPublico(BaseModel):
    id: str
    nombre: str
    username: str | None = None
    email: str | None = None
    telefono_e164: str | None = None


class AuthTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UsuarioPublico
