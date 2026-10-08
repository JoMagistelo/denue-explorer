"""Configuración del cliente DENUE.

El valor fue proporcionado por el propietario para incorporarlo directamente.
ATENCIÓN: este repositorio es público; el token también lo es.
"""
from __future__ import annotations

import os

BUILTIN_TOKEN = "374ad581-44c0-42e5-945b-65e52ec0517d"


def _local_token() -> str:
    """Lee un token privado opcional; nunca se incorpora a Git."""
    try:
        from .local_token import BUILTIN_TOKEN as private_token
    except ImportError as exc:
        if exc.name not in ("denue_explorer.local_token", "local_token"):
            raise
        return ""
    return str(private_token).strip()


def load_token() -> str:
    """Clave privada local > token incorporado > variable de entorno.

    El archivo local_token.py está ignorado por Git y evita conflictos al hacer pull.
    """
    private_token = _local_token()
    if private_token:
        return private_token
    built_in = BUILTIN_TOKEN.strip()
    if built_in and built_in != "AQUÍ_VA_TU_TOKEN":
        return built_in
    return os.getenv("INEGI_DENUE_TOKEN", "").strip()


def token_source() -> str:
    """Informa el origen de la clave sin mostrarla."""
    if _local_token():
        return "local_token.py (solo este equipo)"
    if BUILTIN_TOKEN.strip() and BUILTIN_TOKEN.strip() != "AQUÍ_VA_TU_TOKEN":
        return "settings.py (token incorporado)"
    if os.getenv("INEGI_DENUE_TOKEN", "").strip():
        return "variable INEGI_DENUE_TOKEN"
    return "ninguna: falta token"
