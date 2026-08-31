"""Cognitive directives for each pipeline phase.

Provides get_phase_cognitive_directive() — the canonical source for
phase-specific cognitive directives extracted from agent_pipeline.py.

This module MUST NOT import from agent_pipeline to avoid circular dependencies.
State is passed as a string to maintain one-way dependency direction.
"""
from __future__ import annotations


def get_phase_cognitive_directive(
    state: str,
    failed_verification: dict[str, Any] | None = None,
) -> str:
    """Devuelve la directiva cognitiva acotada a la fase activa.

    Parameters
    ----------
    state : str
        The current agent state determining which directive to return.
        Expected values: "PLAN", "EXPLORE", "EXECUTE", "VERIFY", "DIAGNOSE", "REPLAN".
    failed_verification : dict or None
        AST/error information used by DIAGNOSE and REPLAN directives.

    Returns
    -------
    str
        Phase-specific cognitive directive, or empty string if state is
        unrecognized.
    """
    if state == "PLAN":
        return "DIRECTIVA DE FASE (PLAN): Estás en la fase PLAN. Especialízate únicamente en analizar el objetivo y construir un desglose estructurado de pasos sin aplicar modificaciones de código."
    elif state == "EXPLORE":
        return "DIRECTIVA DE FASE (EXPLORE): Estás en la fase EXPLORE. Especialízate únicamente en consultar el Grafo AST Graphify y leer dependencias para construir el contexto estructural."
    elif state == "EXECUTE":
        return "DIRECTIVA DE FASE (EXECUTE): Estás en la fase EXECUTE. Especialízate en aplicar los parches sintácticos y modificaciones de código exactas usando las herramientas de archivos."
    elif state == "VERIFY":
        return "DIRECTIVA DE FASE (VERIFY): Estás en la fase VERIFY. Especialízate en ejecutar ruff y la suite de pruebas unitarias para confirmar la validez sintáctica."
    elif state == "DIAGNOSE":
        err_msg = ", ".join(failed_verification.get("ast_errors", [])) if failed_verification else "Fallo no especificado"
        return f"DIRECTIVA DE FASE (DIAGNOSE): Analiza la causa raíz del siguiente fallo: {err_msg}. Determina si se trata de un error sintáctico, una falla en pruebas o una dependencia faltante."
    elif state == "REPLAN":
        err_msg = ", ".join(failed_verification.get("ast_errors", ["Fallo en pruebas unitarias o linter ruff"])) if failed_verification else "Errores no especificados"
        return f"DIRECTIVA DE FASE (REPLAN): La verificación anterior falló con los siguientes errores exactos: {err_msg}. Tu único objetivo cognitivo ahora es corregir y reparar estas fallas."
    return ""