# DENUE Explorer

Aplicación de escritorio en **Flet** para consultar la API oficial DENUE del INEGI. No pertenece al INEGI ni a SIGER.

## Requisitos
- Windows 10/11 con Python 3.11 o posterior, Git y acceso a internet.
- **Token personal DENUE**, obtenido en https://www.inegi.org.mx/servicios/api_denue.html
- Para redes con inspección SSL, solicita a TI el certificado raíz institucional en formato PEM.

## Instalar desde cero en PowerShell / VS Code

```powershell
git clone https://github.com/TU_USUARIO/denue-explorer.git
cd denue-explorer
.\scripts\setup.ps1
.\scripts\run.ps1
```

> `TU_USUARIO` es un marcador: sustituye por tu usuario al crear el repositorio GitHub. Si Windows bloquea scripts, ejecuta `powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1`.

Ingresa el token en la aplicación (se mantiene en memoria, nunca se almacena en el repositorio), o establece temporalmente ` $env:INEGI_DENUE_TOKEN='tu-token' ` antes de iniciar.

## Buscar
- **Nombre**: establecimiento o razón social, entidad opcional `00` para México.
- **BuscarEntidad**: términos separados por coma, de acuerdo con la documentación INEGI.
- **Ficha**: ID de establecimiento DENUE, **no** CLEE ni FME.
- Paginación: inicio y fin; máximo 100 registros por petición.
- Filtrar: filtra solo los resultados descargados (no toda la base nacional).
- Exportar CSV: crea `Downloads/denue_resultados.csv`.
- **FME**: pertenece al Registro Público de Comercio; se abre el sitio de SIGER de manera externa, sin fingir que el DENUE resuelve FME.

## Certificados corporativos
Si aparece `CERTIFICATE_VERIFY_FAILED` o `self-signed certificate in certificate chain`, pide a TI el certificado raíz del proxy de tu organización y configura su ruta:

```powershell
$env:DENUE_CA_BUNDLE='C:\ruta\certificado-corporativo.pem'
.\scripts\run.ps1
```

No uses `verify=False` en producción. Verifica el nombre de archivo del certificado y que sea un CA de confianza.

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
- No se promete compatibilidad universal con futuras versiones de Flet: se mantiene la restricción `<2`.
- GitHub Actions ejecutará pruebas en Windows tras publicar el repositorio.

## Endpoints respaldados oficialmente

`/Nombre/{termino}/{entidad}/{inicio}/{fin}/{token}`  
`/BuscarEntidad/{condicion}/{entidad}/{inicio}/{fin}/{token}`  
`/Ficha/{id}/{token}`

Documentación: https://www.inegi.org.mx/servicios/api_denue.html
