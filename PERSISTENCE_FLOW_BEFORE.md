# PERSISTENCE FLOW AUDIT — BEFORE (Phase C3.1 Baseline)

**Fecha:** 2026-08-30  
**Objetivo:** Documentar todos los flujos de persistencia actuales antes de la canonicalización.

---

## 🔴 RESUMEN EJECUTIVO

**DRIFT-01 CONFIRMADO:** El runtime usa `session_manager.py / JSON` como **primera opción** en múltiples flujos críticos, violando la arquitectura canónica que establece `DatabaseManager / SQLite = SOURCE OF TRUTH`.

---

## 📊 MAPA DE FLUJOS DE PERSISTENCIA ACTUALES

### 1. CHECKPOINT GUARDADO — `_save_checkpoint()` (agent_pipeline.py:213-275)

```
┌─────────────────────────────────────────────────────────────────┐
│                     _save_checkpoint()                          │
├─────────────────────────────────────────────────────────────────┤
│  PRIMERO (Líneas 227-248):                                      │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ from session_manager import load_session, save_session     │  │
│  │ data = load_session(session_id)          ← JSON READ       │  │
│  │ data["memory"]["working"]["state_checkpoint"] = {...}      │  │
│  │ save_session(session_id, data)           ← JSON WRITE      │  │
│  └────────────────────────────────────────────────────────────┘  │
│                              │                                  │
│                              ▼                                  │
│  SEGUNDO (Líneas 250-275):                                      │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ from storage.database import get_db_manager                │  │
│  │ db.save_checkpoint(...)              ← SQLite WRITE        │  │
│  │ db.update_task_status(...)           ← SQLite WRITE        │  │
│  │ bus.publish(...)                     ← EventBus            │  │
│  └────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘

❌ PROBLEMA: JSON se escribe ANTES que SQLite. JSON es "Source of Truth" primario.
```

---

### 2. RESUME SESSION — `resume_session()` (agent_pipeline.py:496-554)

```
┌─────────────────────────────────────────────────────────────────┐
│                     resume_session()                            │
├─────────────────────────────────────────────────────────────────┤
│  PRIMERO (Líneas 504-508):                                      │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ from session_manager import load_session                   │  │
│  │ data = load_session(session_id)          ← JSON READ       │  │
│  │ checkpoint = data["memory"]["working"]["state_checkpoint"] │  │
│  └────────────────────────────────────────────────────────────┘  │
│                              │                                  │
│                              ▼ (si no hay checkpoint en JSON)   │
│  SEGUNDO (Líneas 510-520):                                      │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ if not checkpoint and self._db_manager:                    │  │
│  │     chk_db = self._db_manager.get_latest_checkpoint()      │  │
│  │     task_db = self._db_manager.get_task()                  │  │
│  │     checkpoint = {...}                 ← SQLite READ       │  │
│  └────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘

❌ PROBLEMA: JSON se consulta PRIMERO. SQLite es fallback.
```

---

### 3. SESSION MANAGER API — Funciones públicas (session_manager.py:126-147)

```
┌─────────────────────────────────────────────────────────────────┐
│  create_new_session()   → JSON WRITE (crea archivo .json)       │
│  load_session()         → JSON READ                              │
│  save_session()         → JSON WRITE                             │
│  list_sessions()        → JSON READ (lista archivos .json)      │
│  delete_session()       → JSON DELETE                            │
│  rename_session()       → JSON READ + WRITE                      │
│  export_session_to_md() → JSON READ                              │
└─────────────────────────────────────────────────────────────────┘

⚠️ USO: Desktop UI (localcode_claude_ui.html) usa estas APIs vía localcode_server.py
```

---

### 4. LOCALCODE SERVER — Endpoints de sesión (localcode_server.py)

```
┌─────────────────────────────────────────────────────────────────┐
│  GET  /api/sessions           → session_manager.list_sessions() │
│  POST /api/sessions           → session_manager.create_new_session() │
│  GET  /api/sessions/{id}      → session_manager.load_session()  │
│  PUT  /api/sessions/{id}      → session_manager.save_session()  │
│  DELETE /api/sessions/{id}    → session_manager.delete_session()│
│  POST /api/sessions/{id}/rename→ session_manager.rename_session()│
└─────────────────────────────────────────────────────────────────┘

❌ PROBLEMA: API REST expone JSON session_manager como interfaz primaria.
```

---

### 5. DESKTOP STARTUP — desktop_app.py

```
┌─────────────────────────────────────────────────────────────────┐
│  launch_codeagent_desktop()                                     │
│       │                                                         │
│       ▼                                                         │
│  find_free_port() + subprocess.Popen(localcode_server.py)       │
│       │                                                         │
│       ▼                                                         │
│  localcode_server.py inicia en puerto dinámico                  │
│       │                                                         │
│       ▼                                                         │
│  Sirve localcode_claude_ui.html (usa session_manager API)       │
└─────────────────────────────────────────────────────────────────┘

⚠️ No persiste estado de arranque en SQLite directamente.
```

---

### 6. SERVER STARTUP — localcode_server.py

```
┌─────────────────────────────────────────────────────────────────┐
│  main() / run_server()                                          │
│       │                                                         │
│       ▼                                                         │
│  ThreadingHTTPServer en PORT (default 8000)                     │
│       │                                                         │
│       ▼                                                         │
│  _start_parent_monitor() → monitorea PID padre (Windows API)    │
│       │                                                         │
│       ▼                                                         │
│  Sirve estáticos + API REST (session_manager + Ollama proxy)    │
└─────────────────────────────────────────────────────────────────┘

⚠️ No crea task en SQLite al arrancar.
```

---

### 7. RUNTIME RECOVERY — Otros puntos de lectura/escritura

| Archivo | Método | Operación | Storage |
|---------|--------|-----------|---------|
| `agent_pipeline.py` | `run()` línea 295 | `clear_terminal_tasks_buffer()` | Memory (tools.py) |
| `agent_pipeline.py` | `run()` línea 472 | `get_terminal_tasks_buffer()` | Memory (tools.py) |
| `tools.py` | `guardar_reporte()` | Escribe archivo .md | Filesystem |
| `tools.py` | `consultar_db()` | Lee `MisEventos.db` | SQLite (legacy, read-only) |

---

## 📋 MATRIZ DE AUTORIDAD ACTUAL (BEFORE)

| Operación | Primario (1º) | Secundario (2º) | Canónico? |
|-----------|---------------|-----------------|-----------|
| **Guardar Checkpoint** | JSON (session_manager) | SQLite (DatabaseManager) | ❌ NO |
| **Cargar Checkpoint** | JSON (session_manager) | SQLite (DatabaseManager) | ❌ NO |
| **Crear Sesión** | JSON (session_manager) | — | ❌ NO |
| **Listar Sesiones** | JSON (session_manager) | — | ❌ NO |
| **Eliminar Sesión** | JSON (session_manager) | — | ❌ NO |
| **Actualizar Task Status** | SQLite (DatabaseManager) | — | ✅ SÍ |
| **Event Sourcing** | SQLite (DatabaseManager) | — | ✅ SÍ |
| **Métricas** | SQLite (DatabaseManager) | — | ✅ SÍ |

---

## 🎯 FLUJOS QUE REQUIEREN CAMBIO (Prioridad)

### PRIORIDAD ALTA — Violación directa de DRIFT-01

1. **`_save_checkpoint()`** — Invertir orden: SQLite primero, JSON como LEGACY EXPORT
2. **`resume_session()`** — Consultar SQLite primero, JSON solo como fallback/migración

### PRIORIDAD MEDIA — API expuesta incorrectamente

3. **`localcode_server.py` endpoints** — Migrar a DatabaseManager (fora de scope C3.1, documentar)
4. **`session_manager.py` funciones públicas** — Mantener para compatibilidad, marcar legacy

### PRIORIDAD BAJA — Documentación

5. **Desktop/Server startup** — No usan persistence canónica (aceptable para C3.1)

---

## 📝 NOTAS PARA IMPLEMENTACIÓN

### `_save_checkpoint()` — Cambio requerido:
```python
# ANTES (actual):
1. JSON write (session_manager.save_session)
2. SQLite write (db.save_checkpoint)

# DESPUÉS (canónico):
1. SQLite write (db.save_checkpoint) → confirmar éxito
2. JSON write (session_manager.save_session) → SOLO como LEGACY EXPORT, marcado explícitamente
```

### `resume_session()` — Cambio requerido:
```python
# ANTES (actual):
1. JSON read (load_session) → si existe, usar
2. SQLite read (get_latest_checkpoint) → fallback

# DESPUÉS (canónico):
1. SQLite read (get_latest_checkpoint + get_task) → si existe sesión válida, usar
2. JSON read (load_session) → SOLO si SQLite no tiene la sesión
   - Si JSON tiene datos: cargar, MIGRAR a SQLite (create_task + save_checkpoint)
3. Futuras llamadas: usar SQLite
```

---

## ✅ CRITERIOS DE ACEPTACIÓN POST-CAMBIO

- [ ] `resume_session()` consulta DatabaseManager **primero**
- [ ] `resume_session()` usa JSON **solo** como fallback/migración explícita
- [ ] `_save_checkpoint()` persiste en SQLite **primero** y confirma éxito
- [ ] JSON write en `_save_checkpoint()` está **explícitamente clasificado** como LEGACY EXPORT
- [ ] Tests existentes pasan (187 passed, 5 failed pre-existentes)
- [ ] `sdd_check.py` sigue pasando
- [ ] No se eliminó `session_manager.py` ni archivos legacy
- [ ] No se modificaron God Modules estructuralmente
- [ ] No se introdujeron nuevas funcionalidades