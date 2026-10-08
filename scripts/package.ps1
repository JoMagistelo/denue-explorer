$ErrorActionPreference = 'Stop'
& .\.venv\Scripts\python.exe -m pip install --upgrade pyinstaller
& .\.venv\Scripts\pyinstaller.exe --noconfirm --clean --onefile --windowed --name DENUE-Explorer --collect-all flet .\launch.py
Write-Host 'Revisa dist\DENUE-Explorer.exe' -ForegroundColor Green
