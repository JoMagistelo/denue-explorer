"""Comprobación de compatibilidad de controles reales en Flet 1.x."""
import flet as ft
from denue_explorer.app import main

class Window: pass

class FakePage:
    def __init__(self):
        self.window = Window()
        self.controls = []
    def add(self, *controls):
        self.controls.extend(controls)
    def update(self):
        pass

def test_ui_initializes_controls_without_error(monkeypatch):
    monkeypatch.delenv('INEGI_DENUE_TOKEN', raising=False)
    page = FakePage()
    main(page)
    assert len(page.controls) >= 5

def test_flet_api():
    assert ft.Button
    assert ft.TextButton
    assert ft.OutlinedButton
    assert ft.DropdownOption
    assert ft.DataTable
    assert ft.TextOverflow.ELLIPSIS
