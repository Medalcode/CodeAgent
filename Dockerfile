# Dockerfile para OpenCode Hub

FROM python:3.11-slim

# Evitar generación de bytecode .pyc y forzar salida unbuffered en logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Instalar dependencias necesarias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario sin privilegios root para ejecutar la aplicación
RUN useradd -m -s /bin/bash appuser

WORKDIR /app

# Copiar dependencias de Python
COPY mis_agentes_inteligentes/requirements.txt .

# Instalar dependencias
RUN pip3 install --no-cache-dir -r requirements.txt

# Copiar el código del proyecto
COPY mis_agentes_inteligentes/ ./mis_agentes_inteligentes/
COPY tests/ ./tests/

# Asignar propiedad de los archivos al usuario sin privilegios
RUN chown -R appuser:appuser /app

# Cambiar a usuario sin privilegios
USER appuser

EXPOSE 8501 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl --fail http://localhost:8501/_stcore/health || exit 1

WORKDIR /app/mis_agentes_inteligentes

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
