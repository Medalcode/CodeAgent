@echo off
chcp 65001 > nul
title CodeAgent Desktop IDE Launcher v3.5
cls

echo ===================================================
echo [CodeAgent] Lanzando CodeAgent Desktop IDE v3.5...
echo ===================================================
echo.

cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    echo [OK] Entorno virtual .venv detectado.
    ".venv\Scripts\python.exe" desktop_app.py
) else (
    echo [INFO] Usando ejecutable Python del sistema...
    python desktop_app.py
)

pause
