"""Configuración DENUE: token incorporado a petición del propietario del repositorio."""
from __future__ import annotations
import os

SERVICE = "denue-explorer"
ACCOUNT = "inegi-denue-token"

# El propietario pidió incorporar el token directamente. ATENCIÓN:
# Esta clave es pública mientras el repositorio permanezca público.
BUILTIN_TOKEN = "374ad581-44c0-42e5-945b-65e52ec0517d"

class CredentialError(RuntimeError):
    pass

def load_token() -> str:
    env = os.environ.get("INEGI_DENUE_TOKEN", "").strip()
    if env:
        return env
    try:
        import keyring
        stored = (keyring.get_password(SERVICE, ACCOUNT) or "").strip()
        return stored or BUILTIN_TOKEN
    except Exception:
        return BUILTIN_TOKEN

def save_token(token: str) -> None:
    token = token.strip()
    if not token or len(token) < 16:
        raise CredentialError("Escribe un token válido antes de guardarlo.")
    try:
        import keyring
        keyring.set_password(SERVICE, ACCOUNT, token)
    except Exception as exc:
        raise CredentialError("No se pudo guardar el token en Windows; úsalo durante esta sesión.") from exc

def delete_token() -> None:
    try:
        import keyring
        if keyring.get_password(SERVICE, ACCOUNT):
            keyring.delete_password(SERVICE, ACCOUNT)
    except Exception as exc:
        raise CredentialError("No se pudo borrar el token de las credenciales de Windows.") from exc
