"""Nombres de canales Redis y salas lógicas para DM y grupos."""


def dm_room_key(user_a: str, user_b: str) -> str:
    """Canal estable para el par (A,B) sin importar el orden."""
    x, y = sorted([user_a.lower(), user_b.lower()])
    return f"dm:{x}:{y}"


def grupo_room_key(grupo_id: str) -> str:
    return f"grupo:{grupo_id.lower()}"
