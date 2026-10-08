"""Diagnóstico de la respuesta real de DENUE sin imprimir la credencial."""
import json
import ssl
import urllib.request
import urllib.error
from denue_explorer.client import SearchQuery, build_url
from denue_explorer.settings import load_token

def inspect(mode, term):
    token = load_token()
    request = urllib.request.Request(
        build_url(SearchQuery(mode, term, "00", 1, 5), token),
        headers={"Accept": "application/json", "User-Agent": "DENUEExplorer/diagnostic"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            status = response.status
            content_type = response.headers.get("Content-Type", "")
            raw = response.read(80000)
    except urllib.error.HTTPError as exc:
        status = exc.code
        content_type = exc.headers.get("Content-Type", "")
        raw = exc.read(80000)
    except Exception as exc:
        message = str(exc).replace(token, "[TOKEN]")
        print(f"{mode}: NETWORK_ERROR {type(exc).__name__}: {message[:250]}")
        return
    try:
        payload = json.loads(raw)
        kind = type(payload).__name__
        if isinstance(payload, list):
            detail = f"count={len(payload)} first_type={type(payload[0]).__name__ if payload else 'none'}"
        elif isinstance(payload, dict):
            detail = f"keys={list(payload)[:15]!r} preview={str(payload)[:350]}"
        else:
            detail = f"preview={str(payload)[:350]}"
    except (ValueError, UnicodeDecodeError):
        kind = "not-json"
        detail = f"preview={raw[:350].decode('utf-8','replace')}"
    detail = detail.replace(token, "[TOKEN]")
    print(f"{mode}: HTTP={status}, CT={content_type}, TYPE={kind}, {detail}")

if __name__ == "__main__":
    inspect("Nombre", "bimbo")
    inspect("BuscarEntidad", "bimbo")
