# 💻 OpenCode Hub (CodeAgent)

Un Centro de Mando Avanzado para Agentes Inteligentes, construido con **Python, Streamlit y smolagents**. Este proyecto ha evolucionado de un simple script de consola a una plataforma completa estilo *OpenCode* o *OpenWebUI*, diseñada para interactuar con repositorios de código locales y remotos, gestionar tareas y proveer una arquitectura de orquestación de agentes robusta compatible con modelos locales (como Qwen y Llama) y en la nube.

## ✨ Características Principales (Fases 1 a 6)

- **🔄 Multi-Proveedor Dinámico:** Cambia al vuelo entre modelos locales (Ollama) y proveedores Cloud (OpenAI, Anthropic, Google Gemini, Groq) unificados a través de **LiteLLM**.
- **🧠 Orquestación con smolagents:** Utiliza el framework moderno `smolagents` de HuggingFace. A diferencia de agentes antiguos basados en JSON (ReAct), nuestro `CodeAgent` interactúa escribiendo código Python real para orquestar herramientas complejas, lo que lo hace infalible incluso con modelos pequeños de 7B/8B.
- **💾 Sesiones Persistentes:** Las conversaciones se guardan en el disco duro automáticamente. Puedes crear nuevas sesiones, renombrarlas, alternar entre ellas o borrarlas.
- **🌟 Enrutador Swarm Automático:** Selecciona el modo "Auto", y un clasificador ruteará tu petición al agente y conjunto de herramientas adecuados automáticamente.
- **🧬 Subagentes Dinámicos:** Soporta la importación dinámica de subagentes desde la comunidad. Simplemente arrastra un archivo `.md` (con YAML frontmatter) a la carpeta `subagents/` y la interfaz lo asimilará como un nuevo agente nativo.
- **🤖 Agentes (Personas) Preconfigurados:** 
  - *Ingeniero de Software Local:* Puede listar directorios, leer archivos, modificar código de forma segura y ejecutar comandos en tu PC.
  - *Analista de Código:* Lee repositorios de GitHub reales, descarga `README.md` y estructura de archivos para análisis. Detecta inteligentemente el nombre real del repositorio sin que el LLM tenga que adivinarlo.
  - *Asistente de Productividad:* Se conecta a bases de datos SQLite locales en **modo de solo lectura estricto** para gestionar datos y crear reportes sin riesgo de inyecciones destructivas.
- **🔌 Mercado de Skills (Tools):**
  - **Archivos Locales:** Lectura con truncamiento inteligente para no saturar la memoria (Context Window) del LLM, y un motor de edición basado en Diffs para modificaciones de código.
  - **Memoria RAG:** Indexación local de código fuente utilizando bases de datos vectoriales (Chroma) para búsquedas semánticas directas.
  - **Terminal Integrada:** Ejecución de comandos Bash con una capa de seguridad (Blacklist) que bloquea operaciones destructivas del sistema operativo.
  - **Búsqueda Web:** Permite buscar documentación o errores en internet (Google Search).
  - **Integración Git:** Status, Add, Commit, Diff y Push automatizados.

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

- **[Streamlit](https://streamlit.io/):** Interfaz de usuario reactiva y gestión de estados.
- **[smolagents](https://huggingface.co/docs/smolagents/):** Orquestador nativo en Python para LLMs, altamente eficiente con modelos locales.
- **[LiteLLM](https://litellm.vercel.app/):** Traductor universal que permite conectar OpenAI, Anthropic, Gemini, Groq y Ollama usando el mismo código.
- **ChromaDB / HuggingFaceEmbeddings:** Para Memoria Semántica RAG.
- **APIs de GitHub:** Para extracción y análisis de repositorios en modalidad *Deep Dive*.