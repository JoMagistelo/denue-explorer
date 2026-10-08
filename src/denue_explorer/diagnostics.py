"""Diagnóstico local de DENUE. No imprime el token ni la URL de consulta."""
from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import quote

from .client import DenueError, SearchQuery, search
from . import settings


def redact(message: str, token: str) -> str:
    """Oculta el token incluso si el servidor lo incluyera en su respuesta."""
    safe = str(message)
    if token:
        safe = safe.replace(token, "[TOKEN OCULTO]")
        safe = safe.replace(quote(token, safe=""), "[TOKEN OCULTO]")
    return safe


def main() -> int:
    print("=== Diagnóstico DENUE Explorer ===")
    print(f"Archivo de configuración cargado: {Path(settings.__file__).resolve()}")
    print(f"Origen de la clave: {settings.token_source()}")
    if os.getenv("INEGI_DENUE_TOKEN", "").strip() and settings.token_source().startswith("settings.py"):
        print("Aviso: había una variable INEGI_DENUE_TOKEN, pero ahora se respeta settings.py.")
    token = settings.load_token()
    if not token:
        print("ERROR: no hay token configurado.")
        return 2
    print("Consultando INEGI mediante Nombre/bimbo, registros 1 a 3...")
    try:
        rows = search(
            SearchQuery("Nombre", "bimbo", "00", 1, 3),
            token,
            ca_bundle=os.getenv("DENUE_CA_BUNDLE") or None,
            timeout=30,
        )
    except DenueError as exc:
        print("ERROR DENUE:", redact(str(exc), token))
        return 1
    except Exception as exc:
        print("ERROR INESPERADO:", type(exc).__name__, redact(str(exc), token)[:240])
        return 1
    print(f"OK: INEGI devolvió {len(rows)} registros.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
