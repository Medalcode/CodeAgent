@echo off
title OpenCode Hub - Iniciando...
color 0B

echo ===================================================
echo             Iniciando OpenCode Hub...
echo ===================================================
echo.

cd /d "%~dp0mis_agentes_inteligentes"

if exist "..\.venv\Scripts\activate.bat" goto ACTIVATED_ROOT
if exist "venv\Scripts\activate.bat" goto ACTIVATED
if exist ".venv\Scripts\activate.bat" goto ACTIVATED_DOT

echo [!] Configurando entorno virtual por primera vez...
py -3.11 -m venv venv 2>nul
if not exist "venv\Scripts\activate.bat" py -3.10 -m venv venv 2>nul
if not exist "venv\Scripts\activate.bat" python -m venv venv 2>nul

if not exist "venv\Scripts\activate.bat" goto GLOBAL_PYTHON

:ACTIVATED_ROOT
echo [OK] Activando entorno virtual principal .venv...
call ..\.venv\Scripts\activate.bat
goto CHECK_DEPS

:ACTIVATED
echo [OK] Activando entorno virtual venv...
call venv\Scripts\activate.bat
goto CHECK_DEPS

:ACTIVATED_DOT
echo [OK] Activando entorno virtual .venv...
call .venv\Scripts\activate.bat
goto CHECK_DEPS

:GLOBAL_PYTHON
echo [!] Usando Python global...

:CHECK_DEPS
python -c "import streamlit" 2>nul
if errorlevel 1 goto INSTALL_DEPS
goto LAUNCH

:INSTALL_DEPS
echo [!] Instalando dependencias necesarias por primera vez (esto tomara unos momentos)...
python -m pip install --upgrade pip
pip install --prefer-binary -r requirements.txt

:LAUNCH
echo.
echo Seleccione el modo de operacion:
echo 1) Lanzar CodeAgent Desktop IDE All-In-One (Canonica - PyWebView + Ollama + Backend)
echo 2) Lanzar CLI en Terminal (Claude Code Local CLI)
echo 3) Lanzar Interfaz Web Streamlit (3 Paneles IDE - Legacy)
echo.
set /p M=Ingrese su opcion (1, 2 o 3, por defecto 1): 
if "%M%"=="2" goto LAUNCH_CLI
if "%M%"=="3" goto LAUNCH_STREAMLIT

echo Lanzando CodeAgent Desktop IDE All-In-One (Ollama + Backend + UI)...
cd /d "%~dp0.."
python desktop_app.py
goto END

:LAUNCH_CLI
echo Lanzando Claude Code Local CLI en Terminal...
python claude_code_cli.py
goto END

:LAUNCH_STREAMLIT
echo Lanzando Interfaz Web Streamlit (Legacy)...
python -m streamlit run app.py --server.headless=true --browser.gatherUsageStats=false
goto END

:END
echo.
echo Presione cualquier tecla para salir...
pause
