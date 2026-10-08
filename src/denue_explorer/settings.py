"""Configuración del cliente DENUE.

El valor fue proporcionado por el propietario para incorporarlo directamente.
ATENCIÓN: este repositorio es público; el token también lo es.
"""
from __future__ import annotations

import os

BUILTIN_TOKEN = "374ad581-44c0-42e5-945b-65e52ec0517d"


def load_token() -> str:
    """Prioriza la clave de settings.py que el usuario editó explícitamente.

    Una variable de entorno previa no debe anular silenciosamente la clave
    que se configura en el código. Solo se usa cuando BUILTIN_TOKEN está vacío.
    """
    token_in_file = BUILTIN_TOKEN.strip()
    if token_in_file and token_in_file != "AQUÍ_VA_TU_TOKEN":
        return token_in_file
    return os.getenv("INEGI_DENUE_TOKEN", "").strip()


def token_source() -> str:
    """Indica de dónde salió el token sin mostrar la credencial."""
    token_in_file = BUILTIN_TOKEN.strip()
    if token_in_file and token_in_file != "AQUÍ_VA_TU_TOKEN":
        return "settings.py (token incorporado)"
    if os.getenv("INEGI_DENUE_TOKEN", "").strip():
        return "variable INEGI_DENUE_TOKEN"
    return "ninguna: falta token"
