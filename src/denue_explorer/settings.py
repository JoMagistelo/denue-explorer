"""Credenciales locales del sistema: el token no se incluye en el código."""
from __future__ import annotations
import os

SERVICE = "denue-explorer"
ACCOUNT = "inegi-denue-token"

class CredentialError(RuntimeError):
    pass

def load_token() -> str:
    env = os.environ.get("INEGI_DENUE_TOKEN", "").strip()
    if env:
        return env
    try:
        import keyring
        return (keyring.get_password(SERVICE, ACCOUNT) or "").strip()
    except Exception:
        return ""

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
