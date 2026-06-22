#!/usr/bin/env python3
"""
Orquestador Supervisor-Agente para CodeAgent.
Prueba el agente local en 3 niveles de exigencia (baja, media, alta).
Con API key, el Supervisor diagnostica fallos y genera correcciones al system prompt.
"""
import os, sys, json, subprocess, tempfile, traceback, shutil
from pathlib import Path

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

CODEAGENT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mis_agentes_inteligentes")
REPO_DIR = os.path.dirname(os.path.abspath(__file__))
MODELO_LOCAL = os.getenv("MODELO_LOCAL", "qwen2.5-coder:7b")
API_KEY = os.getenv("OPENAI_API_KEY", "")
API_BASE = os.getenv("API_BASE", "https://openrouter.ai/api/v1")
SUPERVISOR_MODEL = os.getenv("SUPERVISOR_MODEL", "openai/gpt-4o-mini")
MAX_ITER = int(os.getenv("MAX_ITERACIONES", "6"))
TEMP = 0.2
HISTORIAL = []
BACKUP_AGENTS = None
BACKUP_ARCHIVOS = {}

NIVELES = {
    "baja": "Operaciones basicas: leer, escribir, listar archivos, edicion search/replace",
    "media": "Ingenieria: refactorizar, escribir tests, mejorar manejo de errores",
    "alta":  "Sistema completo: features multi-archivo, analisis de codebase, automatizacion",
}

BENCHMARKS = [
    # ─── Nivel Baja ─────────────────────────────────────────────────
    {
        "nivel": "baja",
        "nombre": "leer_y_editar",
        "tools": ["Archivos Locales"],
        "tarea": (
            "1. Lee mis_agentes_inteligentes/session_manager.py\n"
            '2. Encuentra la funcion "delete_session"\n'
            '3. Agrega un comentario "# TODO: add validation" al inicio del cuerpo de esa funcion\n'
            "4. USA editar_archivo_search_replace (NO reescribas el archivo completo)\n"
            "5. Vuelve a leer el archivo para verificar que el cambio se aplico\n"
            "6. final_answer() con el resultado"
        ),
        "checklist": ["leer_archivo", "usar_search_replace", "verificar_cambio", "final_answer"],
        "tools_requeridas": ["leer_archivo_local", "editar_archivo_search_replace", "final_answer"],
    },
    {
        "nivel": "baja",
        "nombre": "explorar_y_reportar",
        "tools": ["Archivos Locales"],
        "tarea": (
            "1. Lista mis_agentes_inteligentes/\n"
            "2. Lee mis_agentes_inteligentes/tools.py y cuenta cuantas funciones @tool hay\n"
            "3. Escribe un archivo mis_agentes_inteligentes/RESUMEN.txt con: nombre del proyecto, archivos encontrados, cantidad de tools\n"
            "4. Verifica que RESUMEN.txt se creo correctamente leyendolo\n"
            "5. final_answer()"
        ),
        "checklist": ["listar_dir", "analizar_codigo", "escribir_archivo", "verificar", "final_answer"],
        "tools_requeridas": ["listar_directorio_local", "leer_archivo_local", "escribir_archivo_local", "final_answer"],
    },

    # ─── Nivel Media ────────────────────────────────────────────────
    {
        "nivel": "media",
        "nombre": "refactorizar_funcion",
        "tools": ["Archivos Locales"],
        "tarea": (
            "1. Lee la funcion guardar_reporte en mis_agentes_inteligentes/tools.py\n"
            "2. Mejora su manejo de errores: agrega try/except que capture PermissionError y OSError\n"
            "3. Agrega un mensaje de error especifico para cada tipo de excepcion\n"
            "4. USA editar_archivo_search_replace (NO reescribas tools.py completo)\n"
            "5. Vuelve a leer tools.py para verificar que el cambio sea correcto (el try/except envuelve solo el open/write)\n"
            "6. final_answer()"
        ),
        "checklist": ["leer_codigo", "entender_logica", "mejorar_error_handling", "usar_search_replace", "verificar"],
        "tools_requeridas": ["leer_archivo_local", "editar_archivo_search_replace", "final_answer"],
    },
    {
        "nivel": "media",
        "nombre": "escribir_y_ejecutar_test",
        "tools": ["Archivos Locales", "Terminal Integrada"],
        "tarea": (
            "1. Lee la funcion listar_directorio_local en mis_agentes_inteligentes/tools.py para entender su firma\n"
            "2. Crea un archivo mis_agentes_inteligentes/test_tools.py\n"
            "3. Escribe una prueba unitaria con pytest que pruebe listar_directorio_local('.')\n"
            "4. La prueba debe verificar que el resultado contiene 'tools.py'\n"
            '5. Ejecuta: python3 -m pytest mis_agentes_inteligentes/test_tools.py -v\n'
            "6. final_answer() con el resultado de los tests"
        ),
        "checklist": ["leer_firma", "crear_test", "escribir_test_correcto", "ejecutar_test", "pasar_test"],
        "tools_requeridas": ["leer_archivo_local", "escribir_archivo_local", "ejecutar_comando_terminal", "final_answer"],
    },
    {
        "nivel": "media",
        "nombre": "depurar_y_corregir",
        "tools": ["Archivos Locales"],
        "tarea": (
            "1. Lee mis_agentes_inteligentes/session_manager.py completo\n"
            "2. Identifica: la funcion delete_session no verifica si la sesion existe antes de eliminar\n"
            "3. Agrega una validacion: si el archivo no existe, retorna 'Sesion no encontrada'\n"
            "4. USA editar_archivo_search_replace\n"
            "5. Lee el archivo para verificar el cambio\n"
            "6. final_answer()"
        ),
        "checklist": ["leer_archivo", "identificar_issue", "implementar_validacion", "usar_search_replace", "verificar"],
        "tools_requeridas": ["leer_archivo_local", "editar_archivo_search_replace", "final_answer"],
    },

    # ─── Nivel Alta ─────────────────────────────────────────────────
    {
        "nivel": "alta",
        "nombre": "feature_multi_archivo",
        "tools": ["Archivos Locales"],
        "tarea": (
            "Implementa una nueva herramienta 'obtener_fecha_actual' en mis_agentes_inteligentes/tools.py y registrala en mis_agentes_inteligentes/main.py.\n\n"
            "PASOS:\n"
            "1. Lee mis_agentes_inteligentes/tools.py para ver el patron @tool existente\n"
            "2. Lee mis_agentes_inteligentes/main.py para ver como se registran las herramientas en TOOLS_MAP\n"
            "3. Agrega en tools.py una nueva funcion @tool llamada obtener_fecha_actual\n"
            "   - Debe retornar la fecha actual en formato YYYY-MM-DD HH:MM:SS\n"
            "   - Debe tener docstring con descripcion y argumentos (no requiere args)\n"
            "   - Debe tener try/except\n"
            "4. En main.py, agrega la nueva funcion a la lista de 'Archivos Locales' en TOOLS_MAP\n"
            "5. Verifica: lee ambos archivos para confirmar los cambios\n"
            "6. final_answer() con los nombres de la funcion y las lineas modificadas"
        ),
        "checklist": ["leer_patron_existente", "crear_nueva_funcion", "registrar_en_main", "verificar_ambos", "final_answer"],
        "tools_requeridas": ["leer_archivo_local", "escribir_archivo_local", "editar_archivo_search_replace", "final_answer"],
    },
    {
        "nivel": "alta",
        "nombre": "analisis_completo_codebase",
        "tools": ["Archivos Locales"],
        "tarea": (
            "Realiza un analisis completo del codebase de CodeAgent.\n\n"
            "PASOS:\n"
            "1. Lista mis_agentes_inteligentes/ para ver todos los archivos\n"
            "2. Lee CADA archivo .py en ese directorio (uno por uno)\n"
            "3. Para cada archivo, identifica: que hace, cuantas funciones tiene, que imports usa\n"
            "4. Escribe un archivo ANALISIS_CODEBASE.md con:\n"
            "   - Lista de archivos y lineas\n"
            "   - Proposito de cada modulo\n"
            "   - Dependencias entre modulos\n"
            "   - 3 sugerencias de mejora\n"
            "5. final_answer() con la ruta del archivo creado"
        ),
        "checklist": ["listar_todo", "leer_todos_los_archivos", "sintetizar", "escribir_analisis", "final_answer"],
        "tools_requeridas": ["listar_directorio_local", "leer_archivo_local", "escribir_archivo_local", "final_answer"],
    },
    {
        "nivel": "alta",
        "nombre": "automatizar_flujo",
        "tools": ["Archivos Locales", "Terminal Integrada"],
        "tarea": (
            "Crea un script de automatizacion y pruebalo.\n\n"
            "PASOS:\n"
            "1. Lee mis_agentes_inteligentes/session_manager.py para entender el formato de las sesiones\n"
            "2. Crea un script mis_agentes_inteligentes/limpiar_sesiones.py que:\n"
            "   - Lee todos los .json en mis_agentes_inteligentes/sesiones/\n"
            "   - Si recibe --dry-run solo muestra lo que haria\n"
            "   - Si recibe --ejecutar, elimina sesiones vacias (sin mensajes)\n"
            "3. Prueba el script con: python3 mis_agentes_inteligentes/limpiar_sesiones.py --dry-run\n"
            "4. Si funciona, ejecuta con --ejecutar\n"
            "5. Verifica que las sesiones vacias se eliminaron (o muestra el dry-run)\n"
            "6. final_answer() con el resultado del dry-run"
        ),
        "checklist": ["leer_formato", "crear_script", "probar_con_dry_run", "ejecutar", "verificar", "final_answer"],
        "tools_requeridas": ["leer_archivo_local", "escribir_archivo_local", "listar_directorio_local", "ejecutar_comando_terminal", "final_answer"],
    },
]


def supervisor(prompt, system):
    if not API_KEY or not OpenAI:
        return None
    client = OpenAI(api_key=API_KEY, base_url=API_BASE)
    kwargs = {"model": SUPERVISOR_MODEL, "messages": [
        {"role": "system", "content": system},
        {"role": "user", "content": prompt}
    ], "temperature": TEMP}
    # response_format no siempre disponible en todos los modelos/providers
    try:
        resp = client.chat.completions.create(**kwargs, response_format={"type": "json_object"})
    except Exception:
        resp = client.chat.completions.create(**kwargs)
    return json.loads(resp.choices[0].message.content)

def backup_archivos_trabajo():
    """Guarda backups de archivos que los benchmarks pueden modificar."""
    global BACKUP_ARCHIVOS
    for archivo in ["tools.py", "main.py", "session_manager.py"]:
        fp = os.path.join(CODEAGENT_DIR, archivo)
        if os.path.exists(fp):
            with open(fp) as f:
                BACKUP_ARCHIVOS[archivo] = f.read()

def restaurar_archivos_trabajo():
    """Restaura archivos de trabajo a su estado original."""
    for archivo, contenido in BACKUP_ARCHIVOS.items():
        fp = os.path.join(CODEAGENT_DIR, archivo)
        with open(fp, "w") as f:
            f.write(contenido)
    # Limpiar cache de Python
    import shutil
    pycache = os.path.join(CODEAGENT_DIR, "__pycache__")
    if os.path.exists(pycache):
        shutil.rmtree(pycache)


def gen_script(b):
    return f'''#!/usr/bin/env python3
import os, sys, json, traceback
sys.path.insert(0, {json.dumps(CODEAGENT_DIR)})
os.chdir({json.dumps(REPO_DIR)})
from agents import get_model, crear_agente
import tools as T
from smolagents.memory import ActionStep

tools = [T.leer_archivo_local, T.escribir_archivo_local, T.listar_directorio_local, T.editar_archivo_search_replace, T.ejecutar_comando_terminal]
model = get_model("Ollama (Local)", {json.dumps(MODELO_LOCAL)})
agent = crear_agente("Ingeniero de Software Local", model, tools)

tarea = {json.dumps(b["tarea"])}
tr = {{"nombre": {json.dumps(b["nombre"])}, "nivel": {json.dumps(b["nivel"])}, "pasos": [], "n": 0, "res": "", "err": None, "tools": []}}
try:
    r = agent.run(tarea)
    tr["res"] = str(r)[:600]
    for i, s in enumerate(getattr(agent.memory, "steps", [])):
        if not isinstance(s, ActionStep):
            continue
        mo = str(s.model_output or "")
        hs = [tn for tn in ["leer_archivo_local","escribir_archivo_local","listar_directorio_local","editar_archivo_search_replace","ejecutar_comando_terminal","final_answer"] if tn in mo]
        obs = str(s.observations)[:400] if hasattr(s, "observations") and s.observations else ""
        tr["pasos"].append({{"i": i, "hs": hs, "mo": mo[:400], "obs": obs}})
        tr["n"] += 1
    tr["tools"] = list(set(h for p in tr["pasos"] for h in p["hs"]))
except Exception as e:
    tr["err"] = str(e)[:500]
    tr["res"] = traceback.format_exc()[:500]
print("===JSON_TRACE_BEGIN===")
print(json.dumps(tr))
print("===JSON_TRACE_END===")
'''


def probar(b):
    s = gen_script(b)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(s)
        p = f.name
    try:
        r = subprocess.run([sys.executable, p], capture_output=True, text=True, timeout=180)
        i = r.stdout.rfind("===JSON_TRACE_BEGIN===")
        j = r.stdout.rfind("===JSON_TRACE_END===")
        if i >= 0 and j > i:
            return json.loads(r.stdout[i+22:j].strip())
        return {"err": f"no trace ({len(r.stdout)}b)", "nombre": b["nombre"], "res": r.stdout[-300:]}
    except subprocess.TimeoutExpired:
        return {"err": "timeout", "nombre": b["nombre"], "res": ""}
    finally:
        try: os.unlink(p)
        except: pass


def diagnosticar(tr, b):
    p = f"""Evalua si el agente completo correctamente esta tarea de nivel {b["nivel"]}.

TAREA: {b["tarea"]}
CHECKLIST: {b["checklist"]}
TOOLS REQUERIDAS: {b["tools_requeridas"]}
TOOLS USADAS: {tr.get("tools", [])}
PASOS: {tr.get("n", 0)}
RESULTADO: {tr.get("res", "")}
ERROR: {tr.get("err", "")}

TRAZA COMPLETA:
{json.dumps(tr, indent=2)[:3000]}

Analiza paso a paso:
1. Uso las herramientas correctas?
2. Completo todos los pasos sin desviarse?
3. El resultado final es correcto?
4. Para nivel media: el codigo generado es correcto?
5. Para nivel alta: los cambios multi-archivo son consistentes?

Responde JSON:
{{"ok": true/false, "fallos": ["que fallo exactamente"], "aciertos": ["que hizo bien"], "causa": "system_prompt|tools_desc|modelo", "detalle": "explicacion"}}"""
    return supervisor(p, "Eres un evaluador de agentes de IA. Respondes JSON.")


def generar_fix(tr, b, diag):
    agents = open(os.path.join(CODEAGENT_DIR, "agents.py")).read()
    hist = "\n".join(HISTORIAL[-5:]) if HISTORIAL else ""
    p = f"""El agente FALLO en nivel {b["nivel"]}: {b["nombre"]}

FALLOS: {diag.get("fallos", [])}
CAUSA: {diag.get("causa", "")}
DETALLE: {diag.get("detalle", "")}

TAREA: {b["tarea"]}
TOOLS REQUERIDAS: {b["tools_requeridas"]}
TOOLS USADAS: {tr.get("tools", [])}
PASOS: {tr.get("n", 0)}
RESULTADO: {tr.get("res", "")}

TRAZA:
{json.dumps(tr, indent=2)[:2000]}

{("HISTORIAL (NO repetir):\n" + hist) if hist else ""}

ARCHIVO MODIFICABLE (agents.py - funcion crear_agente):
{agents[:2500]}

REGLAS ESTRICTAS:
1. Cambia SOLO el texto del system_prompt de "Ingeniero de Software Local" en crear_agente()
2. Instrucciones concretas para CORREGIR los fallos detectados
3. NO agregues comentarios "#", prints, debug, ni codigo adicional
4. NO cambies la sintaxis de Python ni agregues imports
5. Para nivel media: si no escribe tests, agregale instrucciones de TDD en el prompt
6. Para nivel alta: si no hace cambios multi-archivo, explicarle en el prompt que debe modificar TODOS los archivos necesarios
7. En espanol, search/replace exacto
8. NO repitas el mismo cambio del historial

JSON: {{"cambios": [{{"archivo": "agents.py", "buscar": "...", "reemplazar": "...", "razon": "..."}}]}}"""
    r = supervisor(p, "Eres arquitecto de agentes smolagents. Solo modificas system_prompts. Respondes JSON.")
    return r or {"cambios": []}


def validar_sintaxis(fp):
    try:
        with open(fp) as f:
            compile(f.read(), fp, "exec")
        return True
    except SyntaxError as e:
        print(f"       ERROR SINTACTICO en {fp}: {e}")
        return False


def aplicar(cambios):
    global BACKUP_AGENTS
    fp = os.path.join(CODEAGENT_DIR, "agents.py")
    for c in cambios.get("cambios", []):
        if not os.path.exists(fp) or not c.get("buscar"):
            continue
        with open(fp) as f:
            con = f.read()
        if c["buscar"] not in con:
            print(f"       NO APLICADO: texto no encontrado en {c['archivo']}")
            continue
        # backup antes del primer cambio
        if BACKUP_AGENTS is None:
            BACKUP_AGENTS = con
        # sintaxis del resultado
        nuevo = con.replace(c["buscar"], c["reemplazar"], 1)
        with open(fp + ".tmp", "w") as f:
            f.write(nuevo)
        if not validar_sintaxis(fp + ".tmp"):
            os.unlink(fp + ".tmp")
            print(f"       RECHAZADO (syntax error) en {c['archivo']}")
            continue
        os.replace(fp + ".tmp", fp)
        HISTORIAL.append(f"[{c['archivo']}] {c['razon'][:100]}")
        print(f"       APLICADO en {c['archivo']}: {c['razon'][:80]}")

def restaurar_agents(fp):
    """Restaura agents.py desde BACKUP_AGENTS si existe."""
    global BACKUP_AGENTS
    if BACKUP_AGENTS:
        with open(fp, "w") as fw:
            fw.write(BACKUP_AGENTS)
        print(f"       RESTAURADO backup de agents.py")
        BACKUP_AGENTS = None


def main():
    tiene_api = bool(API_KEY)
    print(f"\n{'='*60}")
    print(f"ORQUESTADOR SUPERVISOR-AGENTE")
    print(f"Modelo: {MODELO_LOCAL}")
    print(f"Supervisor: {SUPERVISOR_MODEL} {'(activo)' if tiene_api else '(solo prueba)'}")
    print(f"\nNiveles de exigencia:")
    for n, d in NIVELES.items():
        print(f"  {n}: {d}")
    print(f"{'='*60}")
    resumen = {}
    total_ok = 0
    total_fail = 0

    # Backup inicial de archivos de trabajo
    backup_archivos_trabajo()

    for nivel in ["baja", "media", "alta"]:
        bs = [b for b in BENCHMARKS if b["nivel"] == nivel]
        print(f"\n{'#'*60}")
        print(f"# NIVEL {nivel.upper()} - {NIVELES[nivel]}")
        print(f"{'#'*60}")

        for b in bs:
            print(f"\n{'─'*50}")
            print(f"Benchmark: {b['nombre']}")
            print(f"{'─'*50}")
            aprobado = False

            # Restaurar archivos al inicio de cada benchmark
            restaurar_archivos_trabajo()

            for it in range(1, MAX_ITER + 1):
                # Restaurar archivos al inicio de cada iteracion
                if it > 1:
                    restaurar_archivos_trabajo()
                print(f"\n  [{it}/{MAX_ITER}] Ejecutando...")
                tr = probar(b)

                if tr.get("err") and "no trace" in str(tr.get("err")):
                    print(f"     Error: {tr['err']}")
                    if BACKUP_AGENTS and it > 1:
                        print(f"     NO TRACE tras cambio - restoring backup")
                        restaurar_agents(os.path.join(CODEAGENT_DIR, "agents.py"))
                    if it == MAX_ITER: break
                    continue

                if tr.get("err"):
                    print(f"     Error: {tr['err'][:100]}")
                    if "timeout" in str(tr.get("err")): break
                    continue

                print(f"     Pasos: {tr.get('n', 0)}")
                print(f"     Tools: {tr.get('tools', [])}")

                if not tiene_api:
                    estado = "EJECUTADO" if tr.get("res") else "FALLIDO"
                    print(f"     Estado: {estado}")
                    if tr.get("res"):
                        total_ok += 1
                        resumen[b["nombre"]] = {"estado": estado, "nivel": nivel}
                    else:
                        total_fail += 1
                    break

                diag = diagnosticar(tr, b)
                if not diag or diag.get("ok"):
                    aprobado = True
                    resumen[b["nombre"]] = {"estado": "APROBADO", "nivel": nivel, "it": it}
                    total_ok += 1
                    print(f"\n     APROBADO en iteracion {it}!")
                    break

                for f in diag.get("fallos", []):
                    print(f"     Fallo: {f}")
                print(f"     Causa: {diag.get('causa', '')}")

                if it < MAX_ITER:
                    fix = generar_fix(tr, b, diag)
                    if fix.get("cambios"):
                        aplicar(fix)
                    else:
                        print("     Sin cambios - reintentando sin modificar prompt")

                if it == MAX_ITER:
                    resumen[b["nombre"]] = {"estado": "MAX_ITER", "nivel": nivel}
                    total_fail += 1

            if aprobado:
                continue
            # Restaurar backup entre benchmarks si hubo cambios
            fp = os.path.join(CODEAGENT_DIR, "agents.py")
            if BACKUP_AGENTS:
                with open(fp) as f:
                    if f.read() != BACKUP_AGENTS:
                        restaurar_agents(fp)

    print(f"\n{'='*60}")
    print(f"RESUMEN FINAL")
    print(f"{'='*60}")
    for n, r in resumen.items():
        emoji = "PASS" if r["estado"] in ("APROBADO", "EJECUTADO") else "FAIL"
        print(f"  [{emoji}] {r['nivel']:5s} {n}")
    print(f"\nTotal: {total_ok} OK / {total_fail} FAIL")
    print(f"Modificaciones al prompt: {len(HISTORIAL)}")

if __name__ == "__main__":
    main()
