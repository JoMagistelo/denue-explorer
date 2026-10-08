# DENUE Explorer

Buscador de establecimientos mediante la API oficial DENUE de INEGI, con interfaz de escritorio en Flet. Proyecto independiente; no es una aplicación oficial del INEGI.

## Instalación en Windows / VS Code

Requisitos: Windows 10/11, Python 3.11+, Git e Internet.

```powershell
git clone https://github.com/JoMagistelo/denue-explorer.git
cd denue-explorer
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\setup.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run.ps1
```

Si la corrección todavía está en el PR, primero cambia a su rama:

```powershell
git fetch origin
git switch --track origin/feat/local-credentials-ui-audit
```

Si la rama ya existe en tu equipo: `git switch feat/local-credentials-ui-audit; git pull --ff-only`.

**No hay que capturar ni guardar el token.** El token proporcionado por el propietario está incorporado en `src/denue_explorer/settings.py`. El programa lo carga solo al comenzar. La variable opcional `INEGI_DENUE_TOKEN` permite reemplazarlo sin editar el archivo.

> **Atención:** este repositorio es público y la credencial incorporada también. Toda persona con acceso al repositorio puede verla y usarla. Si INEGI permite regenerarla, hazlo cuando terminen las pruebas y actualiza el valor.

## Funciones

- Buscar por nombre comercial o razón social (método `Nombre`).
- Buscar por palabras clave, actividad y otros términos (método `BuscarEntidad`).
- Abrir ficha por identificador numérico del establecimiento (`Ficha`).
- Seleccionar la entidad federativa; `00` consulta todas.
- Paginación con rangos de hasta 100 registros por petición.
- Tabla acotada, filtro sobre los resultados descargados (incluyendo CLEE).
- Panel de detalles de cada empresa y enlace a Google Maps si hay coordenadas.
- Exportación CSV a la carpeta Descargas.
- Acceso externo a SIGER para FME; no existe búsqueda FME por DENUE.

El botón **Conexión HTTPS** solo se utiliza si una red corporativa requiere un certificado raíz CA personalizado.

## Problemas de SSL corporativo

Si tu red intercepta HTTPS y ves `CERTIFICATE_VERIFY_FAILED`, solicita a TI el certificado raíz PEM. La aplicación permite indicar su ruta en **Conexión HTTPS**. No se desactiva la comprobación del certificado.

También puedes definir temporalmente la variable de entorno `DENUE_CA_BUNDLE` antes de arrancar.

## Pruebas

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test.ps1
```

GitHub Actions comprueba las pruebas unitarias y la construcción de controles Flet en Windows. **No garantiza la apariencia exacta de la ventana ni el éxito de la consulta real en cualquier red.** Verifica una búsqueda de nombre y la exportación en tu equipo.

## Empaquetar para Windows

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\package.ps1
```

Revisa `dist\DENUE-Explorer.exe`. El empaquetado debe probarse en Windows.

## API INEGI

Documentación oficial: https://www.inegi.org.mx/servicios/api_denue.html

- `/Nombre/{criterio}/{entidad}/{inicio}/{fin}/{token}`
- `/BuscarEntidad/{criterio}/{entidad}/{inicio}/{fin}/{token}`
- `/Ficha/{id}/{token}`
