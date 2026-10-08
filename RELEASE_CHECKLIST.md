# Lista de verificación de versión 1.0

## Pruebas realizadas en el entorno de desarrollo
- [x] Compilación sintáctica de todos los archivos `.py`.
- [x] 16 pruebas unitarias del cliente HTTP (simulación sin credenciales).
- [x] Revisión de rutas `Nombre`, `BuscarEntidad` y `Ficha` contra la documentación INEGI.
- [x] Sin token en código fuente, documentación ni pruebas.
- [x] Se evita `verify=False`: CA de confianza opcional para proxy HTTPS institucional.
- [x] Estructura instalable con `pyproject.toml` y scripts PowerShell.

## Pendiente de validar desde Windows con tu cuenta
- [ ] Ejecutar `scripts/setup.ps1` con Python 3.14 y Flet instalado.
- [ ] Abrir realmente la GUI Flet (el entorno de auditoría no permite instalar Flet).
- [ ] Buscar razón social usando **tu token real** y contrastar registros.
- [ ] Buscar por palabras clave, fichas ID y navegar entre páginas.
- [ ] Resolver el certificado corporativo si aplica.
- [ ] Construir y ejecutar EXE Windows con `scripts/package.ps1`.
- [ ] Publicar en nuevo repositorio GitHub y comprobar Actions (el conector disponible no permite crear un repositorio nuevo).

**No afirmar garantía de cero errores ni prueba end-to-end en ausencia de esas validaciones.**
