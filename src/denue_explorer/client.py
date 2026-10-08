"""Cliente aislado para la API pública DENUE de INEGI."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Literal
from urllib.parse import quote
from urllib.request import Request, build_opener, HTTPSHandler
from urllib.error import HTTPError, URLError
import ssl

BASE_URL = 'https://www.inegi.org.mx/app/api/denue/v1/consulta'
Mode = Literal['Nombre', 'BuscarEntidad', 'Ficha']

class DenueError(Exception):
    """Error seguro para mostrar al usuario, sin exponer su token."""

@dataclass(frozen=True)
class SearchQuery:
    mode: Mode
    term: str
    entity: str = '00'
    start: int = 1
    end: int = 50

    def validate(self) -> None:
        if self.mode not in ('Nombre', 'BuscarEntidad', 'Ficha'):
            raise DenueError('Modo de búsqueda no admitido.')
        if not self.term.strip():
            raise DenueError('Escribe el criterio de búsqueda.')
        if '/' in self.term or '\\' in self.term:
            raise DenueError('No se admiten diagonales en el criterio.')
        if self.mode != 'Ficha':
            if len(self.entity) != 2 or not self.entity.isdigit() or not (0 <= int(self.entity) <= 32):
                raise DenueError('Selecciona una entidad válida.')
            if self.start < 1 or self.end < self.start or self.end - self.start >= 100:
                raise DenueError('Rango inválido: máximo 100 registros por consulta.')
        elif not self.term.strip().isdigit():
            raise DenueError('La consulta Ficha requiere el ID numérico del DENUE (no CLEE ni FME).')


def build_url(query: SearchQuery, token: str) -> str:
    query.validate()
    token = token.strip()
    if not token or token == 'AQUÍ_VA_TU_TOKEN':
        raise DenueError('Configura un token válido de INEGI antes de buscar.')
    term = quote(query.term.strip(), safe=',')
    suffix = (f'{query.mode}/{term}' if query.mode == 'Ficha'
              else f'{query.mode}/{term}/{query.entity}/{query.start}/{query.end}')
    return f'{BASE_URL}/{suffix}/{quote(token, safe="")}'



def _safe_server_message(value: Any, token: str) -> str:
    """Messages sent by INEGI should never expose the embedded credential."""
    text = ' '.join(str(value).split())
    if token:
        text = text.replace(token, '[TOKEN OCULTO]')
        text = text.replace(quote(token, safe=''), '[TOKEN OCULTO]')
    return text[:350]


def _empty_result_message(text: str) -> bool:
    lowered = text.casefold()
    return any(marker in lowered for marker in (
        'no se encontraron', 'sin resultados', 'no hay resultados',
        'no existen establecimientos', 'no existe información',
    ))


def parse_denue_response(raw: bytes, *, token: str = '',
                         content_type: str = '') -> list[dict[str, Any]]:
    """Interpret standard arrays and report actual API error messages.

    DENUE officially returns lists for successful queries. A non-list payload
    is not silently treated as an establishment. Some proxies and backends
    respond with a JSON message even when the HTTP status is 200.
    """
    try:
        payload: Any = json.loads(raw.decode('utf-8-sig'))
    except (ValueError, UnicodeDecodeError) as exc:
        sample = raw[:180].decode('utf-8', errors='replace').lower()
        if '<html' in sample or '<!doctype html' in sample or 'html' in content_type.lower():
            raise DenueError(
                'INEGI devolvió una página HTML en lugar de JSON. '
                'Puede deberse a un bloqueo, mantenimiento o proxy corporativo.'
            ) from exc
        raise DenueError('INEGI no devolvió JSON válido. Revisa el servicio o la red.') from exc

    # Tolerate serialized JSON strings, used by some .NET services.
    for _ in range(2):
        if isinstance(payload, str) and payload.strip().startswith(('[', '{')):
            try:
                payload = json.loads(payload)
            except ValueError:
                break
        else:
            break

    if isinstance(payload, list):
        if all(isinstance(item, dict) for item in payload):
            return payload
        raise DenueError('INEGI devolvió una lista con elementos que no son establecimientos.')

    if isinstance(payload, dict):
        index = {str(key).casefold(): key for key in payload}
        err_key = index.get('error') or index.get('errors')
        if err_key is not None and payload[err_key] not in (None, False, '', []):
            msg = _safe_server_message(payload[err_key], token)
            if _empty_result_message(msg):
                return []
            raise DenueError('INEGI reportó un error: ' + msg)

        for alias in ('datos', 'data', 'resultados', 'results',
                      'resultado', 'response', 'value', 'd'):
            key = index.get(alias)
            if key is None:
                continue
            value = payload[key]
            if isinstance(value, list) and all(isinstance(x, dict) for x in value):
                return value
            if isinstance(value, str) and value.strip().startswith('['):
                return parse_denue_response(value.encode('utf-8'), token=token)

        if 'id' in index and ('nombre' in index or 'clee' in index):
            return [payload]

        for alias in ('mensaje', 'message', 'descripcion', 'detalle', 'detail', 'status'):
            if alias in index:
                msg = _safe_server_message(payload[index[alias]], token)
                if _empty_result_message(msg):
                    return []
                raise DenueError('INEGI respondió: ' + msg)
        keys = ', '.join(_safe_server_message(k, token) for k in list(payload)[:6])
        raise DenueError(
            f'INEGI devolvió un objeto sin establecimientos (campos: {keys}). '
            'Revisa si el token está activo o si el servicio cambió la respuesta.'
        )

    if isinstance(payload, str):
        message = _safe_server_message(payload, token)
        if _empty_result_message(message):
            return []
        if 'no autorizado' in message.casefold() or 'clave válida' in message.casefold():
            raise DenueError(
                'INEGI rechazó el token DENUE incorporado: ' + message
                + ' Obtén una clave vigente de la API DENUE y reemplaza BUILTIN_TOKEN '
                  'en settings.py. No es un fallo del buscador.'
            )
        raise DenueError('INEGI respondió: ' + (message or '(mensaje vacío)'))

    if payload is None:
        raise DenueError('INEGI devolvió null; revisa la vigencia del token o el servicio.')
    raise DenueError('INEGI devolvió un tipo inesperado: ' + type(payload).__name__)


def search(query: SearchQuery, token: str, *, ca_bundle: str | None = None,
           timeout: int = 25, opener: Any = None) -> list[dict[str, Any]]:
    url = build_url(query, token)
    if opener is None:
        try:
            context = ssl.create_default_context(cafile=ca_bundle or None)
        except (OSError, ssl.SSLError) as exc:
            raise DenueError('No se pudo cargar el archivo CA. Comprueba la ruta y el formato PEM.') from exc
        opener = build_opener(HTTPSHandler(context=context))
    request = Request(url, headers={'Accept': 'application/json',
                                     'User-Agent': 'DenueExplorer/1.1'})
    try:
        with opener.open(request, timeout=timeout) as response:
            raw = response.read()
            content_type = (response.headers.get('Content-Type', '')
                            if getattr(response, 'headers', None) is not None else '')
    except HTTPError as exc:
        if exc.code in (401, 403):
            raise DenueError(f'INEGI rechazó el acceso (HTTP {exc.code}). Revisa si el token está activo.') from exc
        if exc.code == 429:
            raise DenueError('INEGI limitó las consultas (HTTP 429). Intenta de nuevo más tarde.') from exc
        raise DenueError(f'INEGI devolvió HTTP {exc.code}. El servicio puede estar temporalmente indisponible.') from exc
    except (ssl.SSLError, URLError, TimeoutError, OSError) as exc:
        reason = str(getattr(exc, 'reason', exc)).lower()
        if 'certificate' in reason or 'ssl' in reason:
            raise DenueError('No se pudo validar HTTPS. Si estás en una red institucional, '
                             'configura el certificado raíz PEM desde Conexión HTTPS.') from exc
        raise DenueError('No se pudo conectar con INEGI. Comprueba red y proxy.') from exc
    return parse_denue_response(raw, token=token, content_type=content_type)


def export_csv(rows: list[dict[str, Any]], file_path: str) -> None:
    import csv
    keys = list(dict.fromkeys(key for row in rows for key in row))
    with open(file_path, 'w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=keys, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)
