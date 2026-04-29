"""Tipos compartidos entre rutas HTTP (parámetros de path reutilizables)."""

from typing import Annotated

from fastapi import Path

ObjectIdPath = Annotated[
    str,
    Path(
        pattern="^[a-fA-F0-9]{24}$",
        description="ObjectId de MongoDB, 24 caracteres hexadecimales",
    ),
]
