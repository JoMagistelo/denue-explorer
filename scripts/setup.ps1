$ErrorActionPreference = 'Stop'
if (!(Test-Path .venv)) { py -3 -m venv .venv }
& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe -m pip install -e '.[test]'
Write-Host 'Instalacion terminada. Ejecuta .\scripts\run.ps1' -ForegroundColor Green
