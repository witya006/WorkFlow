@echo off
setlocal
set "RF455_POWERSHELL=pwsh.exe"
if exist "%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe" set "RF455_POWERSHELL=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe"
"%RF455_POWERSHELL%" -NoLogo -NoProfile -File "%~dp0Invoke-Python.ps1" scripts/preview_client455.py %*
if errorlevel 1 pause
