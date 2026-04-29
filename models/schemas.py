from pydantic import BaseModel, Field

_OID24 = "^[a-fA-F0-9]{24}$"


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
