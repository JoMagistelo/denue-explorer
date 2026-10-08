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

**No se necesita capturar el token al iniciar.** Si existe `src/denue_explorer/local_token.py`, se utiliza su valor `BUILTIN_TOKEN` automáticamente; este archivo está ignorado por Git y protege tu token nuevo frente a futuras actualizaciones. Si no existe, usa el token incorporado en `settings.py` o la variable de entorno de respaldo.

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

## Diagnóstico confirmado de la clave actual (8 de octubre de 2026)

Se comprobó mediante una petición real al servicio oficial que las consultas `Nombre/bimbo` y `BuscarEntidad/bimbo` reciben **HTTP 200** con un **mensaje JSON de no autorización**, no una lista de establecimientos. Por eso la versión anterior mostraba «Respuesta inesperada de INEGI». El problema es la credencial rechazada por el servicio, no el diseño de Flet.

La aplicación ahora interpreta correctamente ese mensaje y distingue:
- Listas de establecimientos y listas vacías.
- JSON envuelto en objetos de respuesta.
- Objetos de error, mensajes del servicio, HTML de bloqueo y JSON inválido.
- Credencial rechazada con código HTTP 200 o 401/403.

**Para hacer consultas de verdad hace falta una clave activa de la API DENUE.** Solicítala o regénérala a través de la [página oficial del INEGI](https://www.inegi.org.mx/servicios/api_denue.html). Como pediste incrustarla en el programa, sustituye una única vez el valor `BUILTIN_TOKEN` del archivo `src/denue_explorer/settings.py` con tu nueva clave, guarda el archivo y reinicia la app. En esta instalación editable no tienes que repetir `setup.ps1`. Evita compartir la nueva clave en GitHub público.

Para comprobar el formato de respuesta sin imprimir el token, puedes ejecutar `.\.venv\Scripts\python.exe scripts/diagnose_api.py`.

## Cuando cambias la clave y sigue apareciendo un error

**Importante:** la clave escrita en `src/denue_explorer/settings.py` tiene prioridad sobre `INEGI_DENUE_TOKEN`, incluso si en Windows quedó configurada una variable de entorno antigua. El programa lee la clave activa al buscar.

Cierra la ventana del programa, inicia una nueva terminal en la raíz del proyecto y comprueba en modo seguro cuál archivo Python está cargado y qué contesta INEGI:

```powershell
.\.venv\Scripts\python.exe -m denue_explorer.diagnostics
```

El diagnóstico imprime la ruta de `settings.py`, el **origen** (nunca el contenido) de la clave, y el resultado de una consulta de prueba de 3 registros de BIMBO. No muestra token ni URL con token.

- **OK**: la API reconoció la clave y devolvió resultados (que podrían ser cero).
- **No autorizado**: INEGI no aceptó la clave activa. Comprueba que sea el token emitido específicamente para **API DENUE**, no para otro servicio de INEGI, y que esté habilitado.
- **HTTPS / certificado**: problema de verificación TLS de la red, no necesariamente de credenciales.
- Si la ruta muestra otra carpeta, se estaba ejecutando otra copia de la aplicación.

Si modificas `settings.py`, **reinicia la aplicación**. No necesitas volver a ejecutar `setup.ps1` porque el proyecto se instaló en modo editable. No publiques claves nuevas en el repositorio público.

## Actualizar sin perder el token ya editado (Windows)

Si actualizaste el token manualmente en `settings.py` y Git muestra `local changes to settings.py would be overwritten by merge`, **no uses `git reset --hard` ni `git stash pop`**. Haz una migración de la clave ya existente:

```powershell
cd C:\Proyectos\denue-explorer
Copy-Item .\src\denue_explorer\settings.py .\src\denue_explorer\local_token.py -Force
git stash push -m "respaldo token local" -- src/denue_explorer/settings.py
git switch main
git pull --ff-only origin main
.\scripts\run.ps1
```

El primer comando copia tu clave nueva sin mostrarla en pantalla. El segundo guarda la modificación local para que Git pueda actualizar; **no se necesita restaurar el stash**: la copia privada `local_token.py` se carga con prioridad automáticamente y Git la ignora. `git pull origin master` no funciona porque la rama principal se llama `main`.

En actualizaciones posteriores bastará con:

```powershell
git switch main
git pull --ff-only origin main
.\scripts\run.ps1
```

Para saber cuál archivo y configuración están activos, sin revelar la clave:

```powershell
.\.venv\Scripts\python.exe -m denue_explorer.diagnostics
```

Si el servidor responde `No autorizado` con el token nuevo, es un rechazo real de INEGI y no un problema de `git pull`. No publiques `local_token.py` ni restaures la modificación de `settings.py` tras hacer la migración.
