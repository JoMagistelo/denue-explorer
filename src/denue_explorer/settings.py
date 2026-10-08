"""Configuración del cliente DENUE.

El valor fue proporcionado por el propietario para incorporarlo directamente.
ATENCIÓN: este repositorio es público; el token también lo es.
"""
from __future__ import annotations

import os

BUILTIN_TOKEN = "374ad581-44c0-42e5-945b-65e52ec0517d"


def load_token() -> str:
    """Devuelve automáticamente el token incluido, sin preguntar al usuario.

    La variable de entorno permite sustituir la clave sin modificar el código.
    """
    return os.getenv("INEGI_DENUE_TOKEN", "").strip() or BUILTIN_TOKEN
