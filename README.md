# 💻 OpenCode Hub (CodeAgent)

Un Centro de Mando Avanzado para Agentes Inteligentes, construido con **Python, Streamlit y CrewAI**. Este proyecto ha evolucionado de un simple script de consola a una plataforma completa estilo *OpenCode* o *OpenWebUI*, diseñada para interactuar con repositorios de código, gestionar tareas y proveer una interfaz rica para interactuar con IA.

## ✨ Características Principales

- **🔄 Multi-Proveedor Dinámico:** Cambia al vuelo entre modelos locales (Ollama) y proveedores Cloud (OpenAI, Anthropic, Google Gemini, Groq).
- **💾 Sesiones Persistentes:** Las conversaciones se guardan en el disco duro automáticamente. Puedes crear nuevas sesiones, renombrarlas, alternar entre ellas o borrarlas.
- **🤖 Selección de Agentes (Personas):** 
  - *Analista de Código:* Lee repositorios de GitHub reales, descarga `README.md` y estructura de archivos para un análisis profundo sin alucinaciones.
  - *Asistente de Productividad:* Se conecta a bases de datos SQLite locales para gestionar agendas y crear reportes.
  - *Asistente General:* Un compañero versátil para cualquier tarea.
- **🔌 Mercado de Skills (MCPs):** Activa y desactiva herramientas en tiempo real desde la barra lateral (por ejemplo, apagar el acceso a GitHub o a la Base de Datos).
- **⚡ Comandos Slash:** Usa atajos rápidos directamente en el chat, como `/help` o `/clear`.

## 🚀 Instalación y Ejecución

1. Clona el repositorio e ingresa a la carpeta principal de la aplicación:
   ```bash
   cd mis_agentes_inteligentes
   ```
2. Activa el entorno virtual:
   ```bash
   source venv/bin/activate
   ```
3. Ejecuta la interfaz gráfica con Streamlit:
   ```bash
   streamlit run app.py
   ```

## 🛠️ Tecnologías Utilizadas

- [Streamlit](https://streamlit.io/): Interfaz de usuario reactiva.
- [CrewAI](https://crewai.com/): Orquestador de agentes y tareas.
- [LangChain](https://python.langchain.com/): Integración con múltiples proveedores de LLMs.
- APIs de GitHub: Para análisis de código en modalidad *Deep Dive*.