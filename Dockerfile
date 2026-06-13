# Dockerfile para OpenCode Hub

# Usar imagen base oficial de Python ligera
FROM python:3.11-slim

# Instalar git y dependencias del sistema necesarias para construir algunos paquetes (ej. sqlite)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar el archivo de requerimientos primero para cachear esta capa de Docker
COPY mis_agentes_inteligentes/requirements.txt .

# Instalar las dependencias de Python
RUN pip3 install --no-cache-dir -r requirements.txt

# Instalar dependencias opcionales para usar otros proveedores
RUN pip3 install --no-cache-dir langchain-openai langchain-anthropic langchain-groq langchain-google-genai

# Copiar el resto del código al contenedor
COPY mis_agentes_inteligentes/ ./mis_agentes_inteligentes/

# Exponer el puerto por defecto de Streamlit
EXPOSE 8501

# Comando para verificar la salud del contenedor
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Cambiar el directorio de trabajo a donde está la app para ejecutarla
WORKDIR /app/mis_agentes_inteligentes

# Iniciar la aplicación Streamlit
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
