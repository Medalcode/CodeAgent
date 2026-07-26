@echo off
title OpenCode Hub - Iniciando...
color 0B

echo ===================================================
echo             Iniciando OpenCode Hub...
echo ===================================================
echo.

cd /d "%~dp0mis_agentes_inteligentes"

if exist "venv\Scripts\activate.bat" goto ACTIVATED
if exist ".venv\Scripts\activate.bat" goto ACTIVATED_DOT

echo [!] Configurando entorno virtual por primera vez...
py -3.10 -m venv venv 2>nul
if not exist "venv\Scripts\activate.bat" py -3.11 -m venv venv 2>nul
if not exist "venv\Scripts\activate.bat" python -m venv venv 2>nul

if not exist "venv\Scripts\activate.bat" goto GLOBAL_PYTHON

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
echo Lanzando la interfaz grafica...
echo.

python -m streamlit run app.py --server.headless=true --browser.gatherUsageStats=false

echo.
echo Presione cualquier tecla para salir...
pause
