import csv
import json
from urllib.error import HTTPError, URLError
import pytest
from denue_explorer.client import SearchQuery, DenueError, build_url, search, export_csv

TOKEN='private-unit-test-token'

class FakeResponse:
    def __init__(self, data): self.data=data
    def __enter__(self): return self
    def __exit__(self,*_): pass
    def read(self): return self.data

class FakeOpener:
    def __init__(self, result): self.result=result; self.request=None
    def open(self, request, timeout=25):
        self.request=request
        if isinstance(self.result, Exception): raise self.result
        return FakeResponse(self.result)

def test_name_url():
    url=build_url(SearchQuery('Nombre','master black','00',1,10),TOKEN)
    assert '/Nombre/master%20black/00/1/10/' in url
    assert TOKEN in url

def test_broad_url():
    assert '/BuscarEntidad/minisuper,Jalisco/14/1/50/' in build_url(SearchQuery('BuscarEntidad','minisuper,Jalisco','14'),TOKEN)

def test_ficha_url():
    assert '/Ficha/9321560/' in build_url(SearchQuery('Ficha','9321560'),TOKEN)

@pytest.mark.parametrize('q',[SearchQuery('Nombre',''),SearchQuery('Nombre','x','33'),
    SearchQuery('Nombre','x','00',0,1),SearchQuery('Nombre','x','00',1,101),
    SearchQuery('Ficha','not an ID')])
def test_invalid_query(q):
    with pytest.raises(DenueError): build_url(q,TOKEN)

def test_invalid_token():
    with pytest.raises(DenueError):build_url(SearchQuery('Nombre','oxxo'),'AQUÍ_VA_TU_TOKEN')

def test_success():
    opener=FakeOpener(json.dumps([{'Id':'1','Nombre':'Ejemplo'}]).encode())
    result=search(SearchQuery('Nombre','ejemplo'),TOKEN,opener=opener)
    assert result[0]['Nombre']=='Ejemplo'
    assert opener.request.get_header('Accept')=='application/json'

def test_empty():
    assert search(SearchQuery('Nombre','x'),TOKEN,opener=FakeOpener(b'[]'))==[]

def test_bad_json():
    with pytest.raises(DenueError,match='JSON'):
        search(SearchQuery('Nombre','x'),TOKEN,opener=FakeOpener(b'<html>fail</html>'))

def test_bad_shape():
    with pytest.raises(DenueError,match='inesperada'):
        search(SearchQuery('Nombre','x'),TOKEN,opener=FakeOpener(b'{"error":"Bad"}'))

def test_http_error_hides_token():
    err=HTTPError('https://example.invalid',403,'Forbidden',{},None)
    with pytest.raises(DenueError) as info:
        search(SearchQuery('Nombre','x'),TOKEN,opener=FakeOpener(err))
    assert TOKEN not in str(info.value)

def test_ssl_error_message():
    with pytest.raises(DenueError,match='HTTPS'):
        search(SearchQuery('Nombre','x'),TOKEN,opener=FakeOpener(URLError('ssl certificate verify failed')))

def test_csv(tmp_path):
    path=tmp_path/'out.csv'
    export_csv([{'Nombre':'Compañía','Id':'1'},{'Nombre':'Otra','CLEE':'2'}],str(path))
    with path.open(encoding='utf-8-sig',newline='') as f:
        records=list(csv.DictReader(f))
    assert len(records)==2 and records[0]['Nombre']=='Compañía' and records[1]['CLEE']=='2'
