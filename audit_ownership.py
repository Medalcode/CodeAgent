"""State Ownership Audit."""
print('=== STATE OWNERSHIP AUDIT ===')
print()

# Based on analysis of agent_pipeline.py and the D0/D1 work, map ownership:

ownership_map = {
    "Agent state (AgentStateMachineController._current_state)": {
        "OWNER": "AgentStateMachineController",
        "READERS": ["AgentStateMachineController, event_bus on STATE_ENTERED/STATE_EXITED"],
        "WRITERS": ["AgentStateMachineController, _save_checkpoint"],
        "PERSISTENCE": "SQLite / DatabaseManager (C3.1: Source of Truth)",
        "RISK": "LOW - controlled via state machine transitions"
    },
    "Task state (task_id in DB + checkpoint)": {
        "OWNER": "DatabaseManager / SQLite (C3.1: Source of Truth)",
        "READERS": ["AgentStateMachineController, resume_session, event_bus"],
        "WRITERS": ["DatabaseManager via _save_checkpoint"],
        "PERSISTENCE": "SQLite primary, JSON legacy (C3.1: dual ownership designed)",
        "RISK": "MEDIUM - dual ownership per C3.1 design, SQLite canonical"
    },
    "Session state (session_id, execution_level)": {
        "OWNER": "DatabaseManager / SQLite (C3.1: Source of Truth)",
        "READERS": ["resume_session, event_bus"],
        "WRITERS": ["DatabaseManager via _save_checkpoint, session_manager JSON legacy export"],
        "PERSISTENCE": "SQLite primary, JSON legacy export (C3.1: explicit LEGACY)",
        "RISK": "LOW - SQLite authoritative, JSON legacy secondary"
    },
    "Verification state (verification_res from _stage_verifier)": {
        "OWNER": "AgentStateMachineController (local variable, passed through run())",
        "READERS": ["_save_checkpoint, _stage_critic"],
        "WRITERS": ["AgentStateMachineController.run() loop"],
        "PERSISTENCE": "SQLite checkpoint (primary), JSON legacy export (secondary, C3.1)",
        "RISK": "LOW - transient per pipeline run"
    },
    "Cognitive directives (get_phase_cognitive_directive)": {
        "OWNER": "cognitive_directives.py (canonical), agent_pipeline.py (call site)",
        "READERS": ["AgentStateMachineController.run() - 2 call sites"],
        "WRITERS": ["None - pure function, no state mutation"],
        "PERSISTENCE": "N/A - pure computational output",
        "RISK": "N/A - pure function, no side effects"
    },
    "Tool permissions (PermissionLevel + check_tool_permission)": {
        "OWNER": "AgentStateMachineController / tools module",
        "READERS": ["_stage_executor, tool execution paths"],
        "WRITERS": ["PermissionLevel enum definition, check_tool_permission()"],
        "PERSISTENCE": "Not persisted per run, checked against task contract",
        "RISK": "LOW - controlled by TaskContract canonical authority (C3.3)"
    },
}

for responsibility, details in ownership_map.items():
    print(f"--- {responsibility} ---")
    for key, value in details.items():
        print(f"  {key}: {value}")
    print()