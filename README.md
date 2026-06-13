# 💻 OpenCode Hub (CodeAgent)

Un Centro de Mando Avanzado para Agentes Inteligentes, construido con **Python, Streamlit y CrewAI**. Este proyecto ha evolucionado de un simple script de consola a una plataforma completa estilo *OpenCode* o *OpenWebUI*, diseñada para interactuar con repositorios de código locales y remotos, gestionar tareas y proveer una arquitectura de Inteligencia de Enjambre (Swarm).

## ✨ Características Principales (Fases 1 a 6)

- **🔄 Multi-Proveedor Dinámico:** Cambia al vuelo entre modelos locales (Ollama) y proveedores Cloud (OpenAI, Anthropic, Google Gemini, Groq).
- **💾 Sesiones Persistentes:** Las conversaciones se guardan en el disco duro automáticamente. Puedes crear nuevas sesiones, renombrarlas, alternar entre ellas o borrarlas.
- **🌟 Enrutador Swarm Automático:** Selecciona el modo "Auto", y un modelo clasificador leerá tu intención y ruteará tu petición al agente y conjunto de herramientas adecuados automáticamente.
- **🧬 Subagentes Dinámicos (Claude Code):** Ahora soporta la importación dinámica de subagentes desde la comunidad. Simplemente arrastra un archivo `.md` (con YAML frontmatter) a la carpeta `subagents/` y la interfaz lo asimilará como un nuevo agente nativo.
- **🤖 Agentes (Personas) Preconfigurados:** 
  - *Ingeniero de Software Local:* Puede listar directorios, leer archivos, modificar código y ejecutar comandos en tu PC.
  - *Analista de Código:* Lee repositorios de GitHub reales (Soporta paginación de 100 repositorios), descarga `README.md` y estructura de archivos para un análisis profundo.
  - *Asistente de Productividad:* Se conecta a bases de datos SQLite locales para gestionar agendas y crear reportes.
- **🔌 Mercado de Skills (MCPs):**
  - **Archivos Locales:** Lectura, listado y un poderoso motor de edición basado en Diffs (inspirado en Aider) para modificaciones precisas de código.
  - **Memoria RAG:** Indexación local de código fuente utilizando bases de datos vectoriales (Chroma) para encontrar exactamente la línea de código que responde a tu pregunta.
  - **Terminal Integrada:** Ejecución de comandos Bash en tiempo real.
  - **Búsqueda Web:** Permite buscar documentación o errores en internet (DuckDuckGo).

## 🚀 Instalación y Ejecución

1. Clona el repositorio e ingresa a la carpeta principal de la aplicación:
   ```bash
   cd mis_agentes_inteligentes
   ```
2. Activa el entorno virtual:
   ```bash
   source venv/bin/activate
   ```
3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
4. Ejecuta la interfaz gráfica con Streamlit:
   ```bash
   streamlit run app.py
   ```

## 🛠️ Tecnologías Utilizadas

- [Streamlit](https://streamlit.io/): Interfaz de usuario reactiva.
- [CrewAI](https://crewai.com/): Orquestador de agentes y tareas.
- [LangChain](https://python.langchain.com/): Integración con múltiples proveedores de LLMs.
- ChromaDB / HuggingFaceEmbeddings: Para Memoria Semántica RAG.
- APIs de GitHub: Para análisis de código en modalidad *Deep Dive*.