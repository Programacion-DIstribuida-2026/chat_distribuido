from pydantic import BaseModel

class Usuario(BaseModel):
    nombre: str

class Mensaje(BaseModel):
    id_usuario: int
    contenido: str