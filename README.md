# DENUE Explorer

Aplicación de escritorio en **Flet** para consultar la API oficial DENUE del INEGI. No pertenece al INEGI ni a SIGER.

## Requisitos
- Windows 10/11 con Python 3.11 o posterior, Git y acceso a internet.
- **Token personal DENUE**, obtenido en https://www.inegi.org.mx/servicios/api_denue.html
- Para redes con inspección SSL, solicita a TI el certificado raíz institucional en formato PEM.

## Instalar desde cero en PowerShell / VS Code

```powershell
git clone https://github.com/JoMagistelo/denue-explorer.git
cd denue-explorer
.\scripts\setup.ps1
.\scripts\run.ps1
```

> Si Windows bloquea scripts, ejecuta `powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1`.

### Configurar el token una sola vez (recomendado)

En PowerShell ejecuta después de instalar:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\configurar-token.ps1
```

Pega el token cuando se solicite: la entrada permanece oculta. El token se guarda en **Windows Credential Manager** y se carga automáticamente cada vez que abras la app. **No hay que volver a escribirlo ni tocar el código Python**. Para actualizarlo, ejecuta el mismo comando. El botón `Configurar token` permite modificarlo desde la aplicación.

No añadas el token como cadena literal a los archivos Python de un repositorio público. Como alternativa, puedes definir temporalmente la variable de entorno `INEGI_DENUE_TOKEN` antes de iniciar.

## Seguridad del token

**El token no se incluye en el código ni en GitHub.** Se guarda en tu equipo al usar el script de configuración o al pulsar *Guardar token*. Si ya lo compartiste fuera del equipo, es recomendable regenerarlo en INEGI. Para las redes con inspección SSL, proporciona la ruta de tu CA institucional desde la interfaz, sin desactivar la validación HTTPS.

## Buscar
- **Nombre**: establecimiento o razón social, entidad opcional `00` para México.
- **BuscarEntidad**: términos separados por coma, de acuerdo con la documentación INEGI.
- **Ficha**: ID de establecimiento DENUE, **no** CLEE ni FME.
- Paginación: inicio y fin; máximo 100 registros por petición.
- Filtrar: filtra solo los resultados descargados, incluso por CLEE (no toda la base nacional).
- Exportar CSV: crea `Downloads/denue_resultados.csv`.
- **FME**: pertenece al Registro Público de Comercio; se abre el sitio de SIGER de manera externa, sin fingir que el DENUE resuelve FME.

## Certificados corporativos
Si aparece `CERTIFICATE_VERIFY_FAILED` o `self-signed certificate in certificate chain`, pide a TI el certificado raíz del proxy de tu organización y configura su ruta:

```powershell
$env:DENUE_CA_BUNDLE='C:\ruta\certificado-corporativo.pem'
.\scripts\run.ps1
```

No uses `verify=False` en producción. Verifica el nombre de archivo del certificado y que sea un CA de confianza.

## Controles disponibles

Buscar, Anterior, Siguiente, Limpiar, Exportar CSV, Guardar token, Eliminar token, filtro local, detalle por establecimiento, Google Maps y consulta externa de FME en SIGER. El rango máximo es de 100 registros. La versión de Flet está fijada para evitar incompatibilidades de controles.

## Ejecutar pruebas

```powershell
.\scripts\test.ps1
```

Las pruebas usan simulaciones HTTP: no requieren token; no sustituyen una prueba en vivo.

## Empaquetar EXE Windows

```powershell
.\scripts\package.ps1
```

Busca el ejecutable en `dist\DENUE-Explorer.exe`. Debe construirse **en Windows**. PyInstaller + Flet se ofrece como alternativa; puede requerir ajustes según las dependencias nativas de la versión de Flet instalada. Si falla, considera el empaquetador oficial `flet build windows` consultando su documentación de la versión instalada.

## Limitaciones verificadas
- La API DENUE exige token y conexión. No es posible validar respuesta de producción sin un token real.
- Sin certificado CA institucional confiable, una red con interceptación HTTPS puede impedir la conexión.
- Flet está limitado a `>=1.0.3,<1.1`; los cambios futuros necesitan su propia validación.
- GitHub Actions ejecutará pruebas en Windows tras publicar el repositorio.

## Endpoints respaldados oficialmente

`/Nombre/{termino}/{entidad}/{inicio}/{fin}/{token}`  
`/BuscarEntidad/{condicion}/{entidad}/{inicio}/{fin}/{token}`  
`/Ficha/{id}/{token}`

Documentación: https://www.inegi.org.mx/servicios/api_denue.html

## Corrección visual de Flet 1.0.3

Se eliminó la combinación `Row(wrap=True)` con `TextField(expand=True)` que ocultaba la búsqueda tras un gran rectángulo gris. La pantalla tiene un buscador visible, configuración plegada, tabla de altura limitada (280 px), filtro y detalle con desplazamiento. El resultado del test de construcción de controles no sustituye una inspección visual humana en Windows.

## Qué validar antes del merge

```powershell
.\scripts\test.ps1
.\scripts\run.ps1
```

Verifica nombre, razón social, palabras clave, ficha por ID, anterior/siguiente, filtro CLEE, detalle, Google Maps, CSV, SIGER, guardar y eliminar token. Las consultas reales dependen del servicio del INEGI y de la cadena de certificados TLS instalada en tu equipo.
