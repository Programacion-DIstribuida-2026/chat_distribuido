from pydantic import BaseModel

class Usuario(BaseModel):
    nombre: str

class Mensaje(BaseModel):
    id_usuario: str  # Cambiado de int a str para MongoDB
    contenido: str