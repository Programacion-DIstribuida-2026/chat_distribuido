"""Normalización de teléfono a E.164 (compartido por auth y contactos)."""

from __future__ import annotations

import re


def normalizar_telefono_e164(codigo_pais: str, numero: str) -> str:
    digits = re.sub(r"\D", "", numero)
    if len(digits) < 7 or len(digits) > 15:
        raise ValueError("El número de teléfono debe tener entre 7 y 15 dígitos.")
    code = codigo_pais.strip()
    if not code.startswith("+"):
        code = "+" + re.sub(r"\D", "", code)
    if not re.match(r"^\+\d{1,4}$", code):
        raise ValueError("codigo_pais inválido (use formato +57).")
    return f"{code}{digits}"
