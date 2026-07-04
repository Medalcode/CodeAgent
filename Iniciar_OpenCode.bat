@echo off
title OpenCode Hub - Iniciando...
color 0B

echo ===================================================
echo             Iniciando OpenCode Hub...
echo ===================================================
echo.

:: Cambiar al directorio donde está el script
cd /d "%~dp0mis_agentes_inteligentes"

:: Intentar activar el entorno virtual si existe
if exist "venv\Scripts\activate.bat" (
    echo [OK] Activando entorno virtual ^(venv^)...
    call venv\Scripts\activate.bat
) else if exist ".venv\Scripts\activate.bat" (
    echo [OK] Activando entorno virtual ^(.venv^)...
    call .venv\Scripts\activate.bat
) else (
    echo [!] No se encontro entorno virtual local. Usando Python global...
)

echo.
echo Lanzando la interfaz grafica...
echo.

:: Ejecutar la aplicacion
streamlit run app.py

:: Si hay un error, mantener la consola abierta
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Hubo un error al intentar iniciar la aplicacion.
    echo Asegurate de haber instalado las dependencias con: pip install -r requirements.txt
    pause
)
