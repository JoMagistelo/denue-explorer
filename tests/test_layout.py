"""Evita regresión del bloqueo gris por filas flexibles envueltas."""
import flet as ft
from denue_explorer.app import main

class Window:
    pass

class FakePage:
    def __init__(self):
        self.window = Window()
        self.controls = []

    def add(self, *controls):
        self.controls.extend(controls)

    def update(self):
        pass


def walk(control):
    yield control
    for child in (getattr(control, 'controls', None) or []):
        yield from walk(child)
    inner = getattr(control, 'content', None)
    if isinstance(inner, ft.Control):
        yield from walk(inner)


def test_search_is_visible_and_has_no_wrapping_expanded_field(monkeypatch):
    monkeypatch.setattr('denue_explorer.app.load_token', lambda: 'test-token')
    page = FakePage()
    main(page)
    controls = [node for root in page.controls for node in walk(root)]
    assert any(isinstance(x, ft.TextField) and x.hint_text == 'Ej. master black'
               for x in controls)
    # The old app put a TextField(expand=True) into Row(wrap=True) and
    # produced a giant grey area in desktop Flet 1.0.3.
    for row in (x for x in controls if isinstance(x, ft.Row)):
        assert not (row.wrap and any(
            isinstance(c, ft.TextField) and c.expand for c in row.controls))
    assert any(isinstance(x, ft.Container) and x.height == 280 for x in controls)
    assert any(isinstance(x, ft.Container) and x.height == 130 for x in controls)


def test_settings_collapsed_and_all_buttons_exist(monkeypatch):
    monkeypatch.setattr('denue_explorer.app.load_token', lambda: '')
    page = FakePage()
    main(page)
    controls = [node for root in page.controls for node in walk(root)]
    labels = [str(getattr(x, 'content', '')) for x in controls
              if isinstance(x, (ft.Button, ft.TextButton, ft.OutlinedButton))]
    for label in ('Buscar en DENUE', 'Limpiar', 'Exportar CSV',
                  'Anterior', 'Siguiente', 'Configurar token', 'FME / SIGER'):
        assert any(label in text for text in labels), label
    assert any(isinstance(x, ft.Container) and x.visible is False for x in controls)
