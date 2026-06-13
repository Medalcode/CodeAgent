#!/bin/bash
# Ejecutable de OpenCode Hub

# Determinar el directorio donde se encuentra este script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$DIR"

echo "Iniciando OpenCode Hub..."

# Verificar si el entorno virtual existe
if [ ! -d "venv" ]; then
    echo "Configurando el entorno por primera vez..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Ejecutar Streamlit de forma silenciosa
streamlit run app.py
