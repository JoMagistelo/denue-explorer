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


def search(query: SearchQuery, token: str, *, ca_bundle: str | None = None,
           timeout: int = 25, opener: Any = None) -> list[dict[str, Any]]:
    url = build_url(query, token)
    if opener is None:
        context = ssl.create_default_context(cafile=ca_bundle or None)
        opener = build_opener(HTTPSHandler(context=context))
    request = Request(url, headers={'Accept': 'application/json', 'User-Agent': 'DenueExplorer/1.0'})
    try:
        with opener.open(request, timeout=timeout) as response:
            raw = response.read()
    except HTTPError as exc:
        if exc.code in (401, 403):
            raise DenueError('INEGI rechazó la solicitud (HTTP %d). Revisa el token.' % exc.code) from exc
        raise DenueError(f'INEGI devolvió HTTP {exc.code}. Inténtalo después.') from exc
    except (ssl.SSLError, URLError, TimeoutError, OSError) as exc:
        reason = str(getattr(exc, 'reason', exc)).lower()
        if 'certificate' in reason or 'ssl' in reason:
            raise DenueError('No se pudo validar HTTPS. Si estás en una red institucional, configura un archivo CA PEM de confianza en DENUE_CA_BUNDLE.') from exc
        raise DenueError('No se pudo conectar con INEGI. Comprueba tu red o proxy y vuelve a intentar.') from exc
    try:
        result = json.loads(raw)
    except (ValueError, UnicodeDecodeError) as exc:
        raise DenueError('INEGI no devolvió JSON válido. Revisa el servicio o el token.') from exc
    if not isinstance(result, list) or any(not isinstance(row, dict) for row in result):
        raise DenueError('Respuesta inesperada de INEGI. No se pudieron procesar los datos.')
    return result


def export_csv(rows: list[dict[str, Any]], file_path: str) -> None:
    import csv
    keys = list(dict.fromkeys(key for row in rows for key in row))
    with open(file_path, 'w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=keys, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)
