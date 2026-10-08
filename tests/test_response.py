import json

import pytest

from denue_explorer.client import DenueError, parse_denue_response


@pytest.mark.parametrize('body, expected', [
    (b'[]', []),
    (b'[{"Id":"1","Nombre":"BIMBO"}]', [{'Id':'1','Nombre':'BIMBO'}]),
    (b'{"Datos":[{"Id":"1"}]}', [{'Id':'1'}]),
    (b'{"results":[]}', []),
    (b'{"Id":"2","Nombre":"Prueba"}', [{'Id':'2','Nombre':'Prueba'}]),
    (b'"No se encontraron resultados"', []),
    (b'{"Mensaje":"No se encontraron registros"}', []),
    (json.dumps('[{"Id":"1"}]').encode(), [{'Id':'1'}]),
])
def test_response_formats(body, expected):
    assert parse_denue_response(body) == expected


@pytest.mark.parametrize('body, message', [
    (b'{"Message":"Token no vigente"}', 'Token no vigente'),
    (b'{"Error":"Token incorrecto"}', 'Token incorrecto'),
    (b'{"codigo":403}', 'campos: codigo'),
    (b'null', 'null'),
    (b'<html>proxy</html>', 'HTML'),
    (b'[{"Id":"1"},42]', 'lista'),
])
def test_response_errors(body, message):
    with pytest.raises(DenueError, match=message):
        parse_denue_response(body)


def test_token_is_redacted_in_server_message():
    secret = 'never-show-this-token'
    message = json.dumps({'Message': 'Token inválido: ' + secret}).encode()
    with pytest.raises(DenueError) as info:
        parse_denue_response(message, token=secret)
    assert secret not in str(info.value)

def test_real_inegi_authorization_response_is_actionable():
    # Observed in live CI as JSON string with HTTP 200.
    response = json.dumps('No autorizado. Utilice una clave válida.').encode()
    with pytest.raises(DenueError, match='rechazó el token DENUE incorporado'):
        parse_denue_response(response)
