# Guarda el token en Windows Credential Manager. Nunca en GitHub.
$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$python = Join-Path $root '.venv\Scripts\python.exe'
if (-not (Test-Path $python)) {
    throw 'Primero ejecuta .\scripts\setup.ps1 para crear el entorno.'
}
$secret = Read-Host 'Pega tu token INEGI (entrada oculta)' -AsSecureString
$ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secret)
try {
    $env:DENUE_TOKEN_INPUT = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr)
    & $python -c "import os; from denue_explorer.settings import save_token; save_token(os.environ['DENUE_TOKEN_INPUT']); print('Token guardado en Windows Credential Manager. Abre de nuevo la app.')"
    if ($LASTEXITCODE -ne 0) { throw 'No se pudo guardar el token. Revisa el mensaje anterior.' }
}
finally {
    Remove-Item Env:DENUE_TOKEN_INPUT -ErrorAction SilentlyContinue
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr)
}
