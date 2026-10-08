"""Interfaz Flet. La capa de red no depende de Flet y es comprobable por separado."""
from __future__ import annotations

import asyncio
import os
import webbrowser
from pathlib import Path
from urllib.parse import quote
import flet as ft

from .client import DenueError, SearchQuery, export_csv, search
from .settings import load_token

STATES = {
    '00': 'Toda la República', '01': 'Aguascalientes', '02': 'Baja California',
    '03': 'Baja California Sur', '04': 'Campeche', '05': 'Coahuila', '06': 'Colima',
    '07': 'Chiapas', '08': 'Chihuahua', '09': 'Ciudad de México', '10': 'Durango',
    '11': 'Guanajuato', '12': 'Guerrero', '13': 'Hidalgo', '14': 'Jalisco',
    '15': 'Estado de México', '16': 'Michoacán', '17': 'Morelos', '18': 'Nayarit',
    '19': 'Nuevo León', '20': 'Oaxaca', '21': 'Puebla', '22': 'Querétaro',
    '23': 'Quintana Roo', '24': 'San Luis Potosí', '25': 'Sinaloa', '26': 'Sonora',
    '27': 'Tabasco', '28': 'Tamaulipas', '29': 'Tlaxcala', '30': 'Veracruz',
    '31': 'Yucatán', '32': 'Zacatecas',
}
FIELDS = ['Id','CLEE','Nombre','Razon_social','Clase_actividad','Estrato',
          'Ubicacion','Calle','Colonia','CP','Telefono','Correo_e',
          'Sitio_internet','Latitud','Longitud']


def txt(row: dict, field: str) -> str:
    value = row.get(field)
    return str(value).strip() if value is not None else ''


def main(page: ft.Page) -> None:
    page.title = 'DENUE Explorer'
    page.window.width = 1180
    page.window.height = 780
    page.window.min_width = 900
    page.window.min_height = 630
    page.bgcolor = '#F5F7FB'
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 12
    page.theme_mode = ft.ThemeMode.LIGHT

    rows: list[dict] = []
    selected: dict | None = None
    current_query: SearchQuery | None = None

    token = load_token()  # Incorporado en settings.py; sin formulario ni configuración
    ca_field = ft.TextField(label='Certificado HTTPS (.pem, opcional)',
                            value=os.getenv('DENUE_CA_BUNDLE',''), width=480, dense=True)
    mode = ft.Dropdown(label='Método', value='Nombre', width=225, dense=True, options=[
        ft.DropdownOption(key='Nombre', text='Nombre / razón social'),
        ft.DropdownOption(key='BuscarEntidad', text='Palabras clave'),
        ft.DropdownOption(key='Ficha', text='ID DENUE (Ficha)'),
    ])
    entity = ft.Dropdown(label='Entidad', value='00', width=245, dense=True, options=[
        ft.DropdownOption(key=k,text=f'{k} · {v}') for k,v in STATES.items()
    ])
    term = ft.TextField(label='Nombre, razón social, actividad o ID', expand=True,
                        dense=True, hint_text='Ej. master black')
    start = ft.TextField(label='Inicio', value='1', width=78, dense=True)
    end = ft.TextField(label='Fin', value='50', width=78, dense=True)
    filter_field = ft.TextField(label='Filtro local (incluye CLEE)', width=320, dense=True)
    status = ft.Text('Listo para buscar en INEGI.', selectable=True, size=12, color='#334155')
    total = ft.Text('0 resultados', weight=ft.FontWeight.BOLD)
    detail = ft.Column([ft.Text('Selecciona una empresa para ver sus datos.', size=12)],
                       spacing=5, scroll=ft.ScrollMode.AUTO)
    grid = ft.DataTable(columns=[ft.DataColumn(ft.Text(v, size=12)) for v in
        ('ID', 'Establecimiento', 'Razón social', 'Actividad', 'Ubicación')], rows=[],
        show_checkbox_column=False, column_spacing=12, heading_row_height=40,
        data_row_min_height=40, data_row_max_height=60)
    empty_hint = ft.Text('Sin resultados. Busca un establecimiento para comenzar.',
                         size=12, color='#64748B')
    page_label = ft.Text('Sin búsqueda', size=11, color='#64748B')

    def show_detail(record: dict) -> None:
        nonlocal selected
        selected = record
        detail.controls = [ft.Text(txt(record,'Nombre') or 'Establecimiento', size=19,
                                   weight=ft.FontWeight.BOLD)]
        for key, value in record.items():
            if value is not None and str(value).strip():
                detail.controls.append(ft.Text(f'{key}: {value}', selectable=True))
        lat, lon = txt(record,'Latitud'), txt(record,'Longitud')
        if lat and lon:
            detail.controls.append(ft.TextButton(content='Ver ubicación en Google Maps',
                on_click=lambda e: webbrowser.open(
                    f'https://www.google.com/maps/search/?api=1&query={quote(lat+","+lon)}')))
        page.update()

    def render() -> None:
        needle = (filter_field.value or '').casefold().strip()
        visible = [r for r in rows if needle in ' '.join(str(v) for v in r.values()).casefold()]
        widths = {'Id': 90, 'Nombre': 215, 'Razon_social': 225,
                  'Clase_actividad': 250, 'Ubicacion': 250}
        grid.rows = [ft.DataRow(cells=[ft.DataCell(ft.Container(
            width=widths[k],
            content=ft.Text(txt(r,k) or '—', size=11, max_lines=2,
                            overflow=ft.TextOverflow.ELLIPSIS),
            on_click=lambda e, item=r: show_detail(item)))
            for k in ('Id','Nombre','Razon_social','Clase_actividad','Ubicacion')])
            for r in visible]
        total.value = f'{len(visible)} visibles / {len(rows)} recibidos'
        empty_hint.visible = not bool(visible)
        empty_hint.value = ('Sin coincidencias en este filtro.' if rows
                            else 'Sin resultados. Busca un establecimiento para comenzar.')
        page_label.value = ('Ficha por ID' if current_query and current_query.mode == 'Ficha'
                            else f'Registros {current_query.start}–{current_query.end}'
                            if current_query else 'Sin búsqueda')
        export_button.disabled = not bool(visible)
        prev_button.disabled = not current_query or current_query.mode == 'Ficha' or current_query.start <= 1
        next_button.disabled = not current_query or current_query.mode == 'Ficha' or len(rows) < (current_query.end-current_query.start+1)
        page.update()

    async def run_search(e=None, *, move: int = 0) -> None:
        nonlocal rows, selected, current_query
        try:
            if move and current_query:
                size = current_query.end-current_query.start+1
                first = max(1, current_query.start + move*size)
                q = SearchQuery(current_query.mode,current_query.term,current_query.entity,first,first+size-1)
            else:
                q = SearchQuery(mode.value, term.value or '', entity.value,
                                int(start.value), int(end.value))
            q.validate()
            if not token or token.strip() == 'AQUÍ_VA_TU_TOKEN':
                raise DenueError('Captura tu token personal de INEGI.')
            selected_ca = (ca_field.value or '').strip() or None
            if selected_ca and not Path(selected_ca).is_file():
                raise DenueError('El certificado CA indicado no existe. Corrige la ruta.')
        except (ValueError, TypeError, DenueError) as exc:
            status.value = f'Error de validación: {exc}'
            page.update()
            return
        search_button.disabled = True
        status.value = 'Consultando INEGI…'
        page.update()
        try:
            result = await asyncio.to_thread(search,q,token,ca_bundle=selected_ca)
            rows = result
            current_query = q
            selected = None
            detail.controls = [ft.Text('Selecciona una empresa de la tabla.')]
            start.value, end.value = str(q.start), str(q.end)
            filter_field.value = ''
            status.value = (f'Consulta correcta: {len(rows)} registros. Rango {q.start}–{q.end}.'
                            if rows else 'Sin resultados en este rango. Prueba otras palabras.')
            render()
        except DenueError as exc:
            status.value = f'Error DENUE: {exc}'
        except Exception:
            status.value = 'Ocurrió un error inesperado. Revisa la terminal para diagnosticarlo.'
            import traceback
            traceback.print_exc()
        finally:
            search_button.disabled = False
            page.update()

    def export_click(e) -> None:
        if not [r for r in rows if (filter_field.value or '').casefold().strip() in
                ' '.join(str(v) for v in r.values()).casefold()]:
            return
        output = Path.home() / 'Downloads' / 'denue_resultados.csv'
        output.parent.mkdir(parents=True,exist_ok=True)
        try:
            visible = [r for r in rows if (filter_field.value or '').casefold().strip() in
                ' '.join(str(v) for v in r.values()).casefold()]
            export_csv(visible,str(output))
            status.value = f'Archivo CSV exportado: {output}'
        except OSError as exc:
            status.value = f'No se pudo guardar el archivo: {exc}'
        page.update()

    search_button = ft.Button(content='Buscar en DENUE', icon=ft.Icons.SEARCH,
                              on_click=run_search)
    export_button = ft.OutlinedButton(content='Exportar CSV',
                                     icon=ft.Icons.DOWNLOAD, on_click=export_click,
                                     disabled=True)
    async def previous_page(e):
        await run_search(e, move=-1)

    async def next_page(e):
        await run_search(e, move=1)

    prev_button = ft.OutlinedButton(content='Anterior', disabled=True,
                                   on_click=previous_page)
    next_button = ft.OutlinedButton(content='Siguiente', disabled=True,
                                   on_click=next_page)
    filter_field.on_change = lambda e: render()
    term.on_submit = run_search

    def clear_click(e):
        nonlocal rows, selected, current_query
        if search_button.disabled:
            return
        rows, selected, current_query = [], None, None
        term.value, filter_field.value = '', ''
        detail.controls = [ft.Text('Selecciona una empresa de la tabla.')]
        status.value = 'Resultados limpiados.'
        render()

    def on_mode_select(e=None):
        ficha = mode.value == 'Ficha'
        entity.disabled = ficha
        start.disabled = ficha
        end.disabled = ficha
        page.update()

    mode.on_select = on_mode_select

    token_hint = ft.Text('API configurada', size=11, color='#475569')

    def toggle_settings(_=None):
        settings_panel.visible = not settings_panel.visible
        page.update()

    settings_panel = ft.Container(
        visible=False, bgcolor='#FFFFFF', padding=12, border_radius=10,
        content=ft.Column([
            ft.Text('Opciones de conexión HTTPS', weight=ft.FontWeight.BOLD, size=12),
            ft.Text('Solo si tu red corporativa requiere un certificado CA adicional.',
                    size=11, color='#64748B'),
            ca_field,
        ], spacing=8))

    def panel(controls):
        return ft.Container(
            bgcolor='#FFFFFF', padding=12, border_radius=10,
            content=ft.Column(controls, spacing=8))

    page.add(
        ft.Row([
            ft.Icon(ft.Icons.BUSINESS, color='#2454A6', size=24),
            ft.Text('DENUE Explorer', size=21, color='#1B3052',
                    weight=ft.FontWeight.BOLD),
            ft.Text('INEGI · Consulta empresarial', size=11, color='#64748B'),
            ft.Container(expand=True),
            token_hint,
            ft.TextButton(content='Conexión HTTPS', on_click=toggle_settings),
        ]),
        settings_panel,
        panel([
            ft.Row([
                ft.Text('Buscar establecimientos', weight=ft.FontWeight.BOLD, size=14),
                ft.Container(expand=True),
                ft.TextButton(content='FME / SIGER ↗',
                    on_click=lambda e: webbrowser.open('https://rpc.economia.gob.mx/')),
            ]),
            ft.Row([mode, entity, start, end], spacing=10),
            # Nunca combinar wrap=True con TextField(expand=True):
            # produjo un área gris gigante en Windows con Flet 1.0.3.
            ft.Row([term, search_button,
                    ft.TextButton(content='Limpiar', on_click=clear_click)],
                    spacing=10),
            ft.Text('Nombre, razón social, actividad y palabras clave · Ficha por ID DENUE.',
                    size=11, color='#64748B'),
        ]),
        ft.Container(bgcolor='#E8F0FC', border_radius=8, padding=9, content=status),
        panel([
            ft.Row([total, ft.Container(expand=True), filter_field,
                    export_button], spacing=8),
            ft.Row([prev_button, page_label, next_button], spacing=8),
            ft.Container(height=280, content=ft.Column([
                empty_hint,
                ft.Row([grid], scroll=ft.ScrollMode.ALWAYS)
            ], scroll=ft.ScrollMode.AUTO)),
        ]),
        panel([
            ft.Text('Detalles del establecimiento', weight=ft.FontWeight.BOLD, size=14),
            ft.Container(height=130, content=detail),
        ]),
        ft.Text('Fuente: INEGI DENUE · No afiliada al INEGI',
                size=10, color='#64748B'),
    )
    on_mode_select()
