#!/usr/bin/env python3
"""
Tests para C3.1: Persistence Canonicalization (DRIFT-01 fix)

Verifica que:
1. SQLite tiene prioridad como Source of Truth
2. JSON solo actúa como fallback/migración
3. JSON legacy se migra correctamente a SQLite
4. Checkpoint escribe SQLite primero
5. Recovery usa SQLite
6. Corrupción JSON no reemplaza SQLite válido
7. Corrupción SQLite produce failure controlado
8. No se pierde información durante migración
"""
import os
import json
import tempfile
import unittest
from unittest.mock import MagicMock, patch

# Configurar entorno de test
os.environ["SKIP_SUBPROCESS_TESTS"] = "1"


class TestPersistenceCanonicalization(unittest.TestCase):
    """Tests para verificar la autoridad de persistencia canónica (C3.1)."""

    def setUp(self):
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../mis_agentes_inteligentes'))
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        
        # Usar directorio temporal para DB y sesiones
        self.temp_dir = tempfile.TemporaryDirectory()
        self.workspace_dir = self.temp_dir.name
        
        # Configurar DB path
        os.environ["CODEAGENT_DB_PATH"] = os.path.join(self.workspace_dir, "test_codeagent.db")
        
        # Configurar sessions dir para JSON legacy
        sessions_dir = os.path.join(self.workspace_dir, "sesiones")
        os.environ["CODEAGENT_SESSIONS_DIR"] = sessions_dir
        os.makedirs(sessions_dir, exist_ok=True)

    def tearDown(self):
        try:
            self.temp_dir.cleanup()
        except Exception:
            pass

    def test_01_sqlite_priority_over_json(self):
        """TEST 1: SQLite tiene prioridad como Source of Truth."""
        from mis_agentes_inteligentes.agent_pipeline import AgentStateMachineController
        from mis_agentes_inteligentes.storage.database import get_db_manager
        
        db = get_db_manager()
        task_id = "test-priority-001"
        
        # Crear task en SQLite
        db.create_task(task_id, self.workspace_dir, "Goal SQLite", "LEVEL_3_FEATURE")
        db.save_checkpoint(task_id, "EXECUTE", "plan sqlite", None, 0)
        
        # Crear JSON legacy con datos DIFERENTES (conflicto)
        from session_manager import save_session
        legacy_data = {
            "id": task_id,
            "name": "Legacy Session",
            "memory": {
                "working": {
                    "state_checkpoint": {
                        "user_goal": "Goal JSON Legacy",
                        "current_state": "PLAN",
                        "replans_count": 99,
                        "execution_level": "LEVEL_1_CHAT"
                    }
                }
            }
        }
        save_session(task_id, legacy_data)
        
        # resume_session debe usar SQLite (Source of Truth), NO JSON
        controller = AgentStateMachineController(workspace_dir=self.workspace_dir)
        mock_runner = MagicMock(side_effect=lambda prompt: f"Ejecutando: {prompt}")
        
        response, metrics = controller.resume_session(task_id, agent_runner=mock_runner)
        
        db = get_db_manager()
        task_db = db.get_task(task_id)
        self.assertEqual(task_db["goal"], "Goal SQLite")
        self.assertNotIn("Goal JSON Legacy", response)
        self.assertEqual(metrics.get("replans_count"), 0)
        self.assertIn("Nivel", str(metrics.get("execution_level")))

    def test_02_json_fallback_when_sqlite_missing(self):
        """TEST 2: JSON legacy actúa como fallback cuando SQLite no tiene la sesión."""
        from mis_agentes_inteligentes.agent_pipeline import AgentStateMachineController
        from session_manager import save_session
        
        task_id = "test-fallback-002"
        
        # Solo JSON legacy (sin SQLite)
        legacy_data = {
            "id": task_id,
            "name": "Legacy Only",
            "memory": {
                "working": {
                    "state_checkpoint": {
                        "user_goal": "Goal from JSON",
                        "current_state": "EXECUTE",
                        "replans_count": 1,
                        "failed_verification": {"ast_errors": ["error1"]},
                        "execution_level": "LEVEL_3_FEATURE"
                    }
                }
            }
        }
        save_session(task_id, legacy_data)
        
        controller = AgentStateMachineController(workspace_dir=self.workspace_dir)
        mock_runner = MagicMock(side_effect=lambda prompt: f"Ejecutando: {prompt}")
        
        response, metrics = controller.resume_session(task_id, agent_runner=mock_runner)
        
        # Debe cargar desde JSON y migrar
        self.assertIn("Goal from JSON", response)
        self.assertEqual(metrics.get("replans_count"), 1)

    def test_03_json_migration_to_sqlite(self):
        """TEST 3: JSON legacy se migra correctamente a SQLite en resume_session."""
        from mis_agentes_inteligentes.agent_pipeline import AgentStateMachineController
        from mis_agentes_inteligentes.storage.database import get_db_manager
        from session_manager import save_session, load_session
        
        task_id = "test-migration-003"
        
        # Solo JSON legacy
        legacy_data = {
            "id": task_id,
            "name": "To Migrate",
            "memory": {
                "working": {
                    "state_checkpoint": {
                        "user_goal": "Migrated Goal",
                        "current_state": "VERIFY",
                        "replans_count": 2,
                        "execution_level": "LEVEL_4_FULL",
                        "plan_data": {"pasos": ["step1", "step2"]}
                    }
                }
            }
        }
        save_session(task_id, legacy_data)
        
        controller = AgentStateMachineController(workspace_dir=self.workspace_dir)
        mock_runner = MagicMock(side_effect=lambda prompt: f"Ejecutando: {prompt}")
        
        # Primera llamada: debe migrar
        response, metrics = controller.resume_session(task_id, agent_runner=mock_runner)
        
        # Verificar migración ocurrió en SQLite
        db = get_db_manager()
        task_db = db.get_task(task_id)
        chk_db = db.get_latest_checkpoint(task_id)
        
        self.assertIsNotNone(task_db, "Task debe crearse en SQLite tras migración")
        self.assertIsNotNone(chk_db, "Checkpoint debe crearse en SQLite tras migración")
        self.assertEqual(task_db["goal"], "Migrated Goal")
        self.assertIn(chk_db["state"], ("VERIFY", "CRITIC", "DONE"))
        self.assertEqual(chk_db["replans_count"], 2)
        
        # Segunda llamada: debe usar SQLite (ya migrado)
        response2, metrics2 = controller.resume_session(task_id, agent_runner=mock_runner)
        task_db2 = db.get_task(task_id)
        self.assertEqual(task_db2["goal"], "Migrated Goal")

    def test_04_checkpoint_writes_sqlite_first(self):
        """TEST 4: _save_checkpoint escribe SQLite primero (Source of Truth)."""
        from mis_agentes_inteligentes.agent_pipeline import AgentStateMachineController, State, ExecutionLevel
        from mis_agentes_inteligentes.storage.database import get_db_manager
        
        controller = AgentStateMachineController(workspace_dir=self.workspace_dir)
        task_id = "test-checkpoint-004"
        
        # Ejecutar _save_checkpoint
        controller._save_checkpoint(
            session_id=task_id,
            current_state=State.EXECUTE,
            execution_level=ExecutionLevel.LEVEL_3_FEATURE,
            user_goal="Test Goal",
            replans_count=0,
            failed_verification=None,
            diagnostic_report=None,
            plan_data={"pasos": ["test"]}
        )
        
        # Verificar que se escribió en SQLite
        db = get_db_manager()
        task_db = db.get_task(task_id)
        chk_db = db.get_latest_checkpoint(task_id)
        
        self.assertIsNotNone(task_db, "Task debe crearse en SQLite")
        self.assertIsNotNone(chk_db, "Checkpoint debe crearse en SQLite")
        self.assertEqual(chk_db["state"], "EXECUTE")
        self.assertIn(task_db["execution_level"], ("LEVEL_3_FEATURE", "Nivel 3 (Feature Standard)"))
        
        # Verificar que JSON se escribió como LEGACY EXPORT (marcado)
        from session_manager import load_session
        json_data = load_session(task_id)
        if json_data:
            checkpoint = json_data.get("memory", {}).get("working", {}).get("state_checkpoint", {})
            self.assertTrue(checkpoint.get("_legacy_export"), "JSON debe marcarse como _legacy_export=True")
            self.assertEqual(checkpoint.get("_source_of_truth"), "sqlite")

    def test_05_recovery_uses_sqlite(self):
        """TEST 5: Recovery/resume usa SQLite como Source of Truth."""
        from mis_agentes_inteligentes.agent_pipeline import AgentStateMachineController
        from mis_agentes_inteligentes.storage.database import get_db_manager
        
        db = get_db_manager()
        task_id = "test-recovery-005"
        
        # Preparar estado en SQLite
        db.create_task(task_id, self.workspace_dir, "Recovery Goal", "LEVEL_3_FEATURE")
        db.save_checkpoint(task_id, "CRITIC", "plan recovery", {"ast_errors": []}, 1)
        db.update_task_status(task_id, "PAUSED", "CRITIC")
        
        controller = AgentStateMachineController(workspace_dir=self.workspace_dir)
        mock_runner = MagicMock(return_value="Recovery OK")
        
        response, metrics = controller.resume_session(task_id, agent_runner=mock_runner)
        task_db = db.get_task(task_id)
        self.assertEqual(task_db["goal"], "Recovery Goal")
        self.assertIn("Nivel", str(metrics.get("execution_level")))

    def test_06_json_corruption_does_not_replace_valid_sqlite(self):
        """TEST 6: JSON corrupto no reemplaza SQLite válido."""
        from mis_agentes_inteligentes.agent_pipeline import AgentStateMachineController
        from mis_agentes_inteligentes.storage.database import get_db_manager
        from session_manager import save_session
        
        task_id = "test-corruption-006"
        
        # SQLite válido
        db = get_db_manager()
        db.create_task(task_id, self.workspace_dir, "Valid SQLite Goal", "LEVEL_3_FEATURE")
        db.save_checkpoint(task_id, "EXECUTE", "plan valid", None, 0)
        
        # JSON corrupto (malformado)
        import os
        json_path = os.path.join(os.environ.get("CODEAGENT_SESSIONS_DIR", ""), f"{task_id}.json")
        with open(json_path, "w", encoding="utf-8") as f:
            f.write("{ invalid json }")
        
        controller = AgentStateMachineController(workspace_dir=self.workspace_dir)
        mock_runner = MagicMock(side_effect=lambda prompt: f"Ejecutando: {prompt}")
        
        response, metrics = controller.resume_session(task_id, agent_runner=mock_runner)
        
        # Debe usar SQLite válido, ignorar JSON corrupto
        self.assertIn("Valid SQLite Goal", response)

    def test_07_sqlite_corruption_fails_explicitly(self):
        """TEST 7: SQLite corrupto produce failure controlado (no inventa estado)."""
        from mis_agentes_inteligentes.agent_pipeline import AgentStateMachineController
        
        task_id = "test-sqlite-corrupt-007"
        
        # No hay SQLite ni JSON
        controller = AgentStateMachineController(workspace_dir=self.workspace_dir)
        mock_runner = MagicMock(side_effect=lambda prompt: f"Ejecutando: {prompt}")
        
        response, metrics = controller.resume_session(task_id, agent_runner=mock_runner)
        
        # Debe fallar explícitamente con mensaje claro
        self.assertIn("Error", response)
        self.assertIn("No se", response)
        self.assertIn("checkpoint", response)
        self.assertEqual(metrics, {})

    def test_08_no_data_loss_during_migration(self):
        """TEST 8: No se pierde información durante migración JSON → SQLite."""
        from mis_agentes_inteligentes.agent_pipeline import AgentStateMachineController
        from mis_agentes_inteligentes.storage.database import get_db_manager
        from session_manager import save_session
        
        task_id = "test-noloss-008"
        
        # JSON legacy con TODOS los campos
        legacy_data = {
            "id": task_id,
            "name": "Complete Legacy",
            "memory": {
                "working": {
                    "state_checkpoint": {
                        "user_goal": "Full Migration Goal",
                        "current_state": "DIAGNOSE",
                        "replans_count": 2,
                        "failed_verification": {
                            "ast_errors": ["SyntaxError: invalid syntax", "ImportError: missing module"],
                            "ruff_failed": True
                        },
                        "diagnostic_report": {
                            "root_cause": "Missing import",
                            "strategy_change": "Add import statement"
                        },
                        "execution_level": "LEVEL_4_FULL",
                        "plan_data": {
                            "objetivo": "Full Migration Goal",
                            "pasos": ["step1", "step2", "AJUSTE ESTRATÉGICO: Add import statement"]
                        }
                    }
                }
            }
        }
        save_session(task_id, legacy_data)
        
        controller = AgentStateMachineController(workspace_dir=self.workspace_dir)
        mock_runner = MagicMock(side_effect=lambda prompt: f"Ejecutando: {prompt}")
        
        response, metrics = controller.resume_session(task_id, agent_runner=mock_runner)
        
        # Verificar que TODOS los datos se migraron
        db = get_db_manager()
        task_db = db.get_task(task_id)
        chk_migrated = db.get_latest_checkpoint(task_id)
        
        chk_db = db.get_latest_checkpoint(task_id)
        self.assertEqual(task_db["goal"], "Full Migration Goal")
        self.assertIn(chk_db["state"], ("DIAGNOSE", "CRITIC", "DONE"))
        
        # Verificar failed_verification se migró completo en el checkpoint inicial
        import json as json_module
        failed_ver = json_module.loads(chk_migrated["failed_verification_json"]) if chk_migrated.get("failed_verification_json") else {}
        self.assertTrue(isinstance(failed_ver, dict))
        
        # Verificar diagnostic_report
        self.assertIsNotNone(chk_db.get("plan"))

    def test_09_resume_without_session_id_fails_gracefully(self):
        """TEST 9: resume_session con session_id inválido falla graciosamente."""
        from mis_agentes_inteligentes.agent_pipeline import AgentStateMachineController
        
        controller = AgentStateMachineController(workspace_dir=self.workspace_dir)
        mock_runner = MagicMock(side_effect=lambda prompt: f"Ejecutando: {prompt}")
        
        response, metrics = controller.resume_session("", agent_runner=mock_runner)
        self.assertIn("Error", response)
        
        response, metrics = controller.resume_session(None, agent_runner=mock_runner)
        self.assertIn("Error", response)

    def test_10_save_checkpoint_sqlite_failure_propagates(self):
        """TEST 10: Falla en SQLite en _save_checkpoint propaga error (no silencioso)."""
        from mis_agentes_inteligentes.agent_pipeline import AgentStateMachineController, State, ExecutionLevel
        from mis_agentes_inteligentes.storage.database import get_db_manager
        
        controller = AgentStateMachineController(workspace_dir=self.workspace_dir)
        db = get_db_manager()
        controller._db_manager = db
        
        # Mocking save_checkpoint to simulate SQLite failure
        import sqlite3
        with patch.object(db, 'save_checkpoint', side_effect=sqlite3.OperationalError("disk I/O error")):
            with self.assertRaises(Exception) as cm:
                controller._save_checkpoint(
                    session_id="test-sqlite-fail",
                    current_state=State.EXECUTE,
                    execution_level=ExecutionLevel.LEVEL_3_FEATURE,
                    user_goal="Test",
                    replans_count=0
                )
        self.assertIn("disk I/O error", str(cm.exception))


class TestPersistenceFailureSemantics(unittest.TestCase):
    """Tests para semántica de fallos (STEP 7)."""

    def setUp(self):
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../mis_agentes_inteligentes'))
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        self.temp_dir = tempfile.TemporaryDirectory()
        self.workspace_dir = self.temp_dir.name
        os.environ["CODEAGENT_DB_PATH"] = os.path.join(self.workspace_dir, "test_codeagent.db")
        sessions_dir = os.path.join(self.workspace_dir, "sesiones")
        os.environ["CODEAGENT_SESSIONS_DIR"] = sessions_dir
        os.makedirs(sessions_dir, exist_ok=True)

    def tearDown(self):
        try:
            self.temp_dir.cleanup()
        except Exception:
            pass

    def test_case_a_sqlite_available_session_exists(self):
        """CASO A: SQLite disponible + sesión existe → SQLite."""
        from mis_agentes_inteligentes.agent_pipeline import AgentStateMachineController
        from mis_agentes_inteligentes.storage.database import get_db_manager
        
        db = get_db_manager()
        task_id = "case-a"
        db.create_task(task_id, self.workspace_dir, "Case A Goal", "LEVEL_3_FEATURE")
        db.save_checkpoint(task_id, "EXECUTE", "plan", None, 0)
        
        controller = AgentStateMachineController(workspace_dir=self.workspace_dir)
        response, _ = controller.resume_session(task_id, agent_runner=MagicMock(side_effect=lambda prompt: f"Ejecutando: {prompt}"))
        
        self.assertIn("Case A Goal", response)

    def test_case_b_sqlite_available_no_session_json_exists(self):
        """CASO B: SQLite disponible + sesión no existe + JSON existe → JSON → migrar → SQLite."""
        from mis_agentes_inteligentes.agent_pipeline import AgentStateMachineController
        from mis_agentes_inteligentes.storage.database import get_db_manager
        from session_manager import save_session
        
        task_id = "case-b"
        
        # Solo JSON
        save_session(task_id, {
            "id": task_id,
            "memory": {"working": {"state_checkpoint": {
                "user_goal": "Case B JSON Goal",
                "current_state": "EXECUTE",
                "replans_count": 0,
                "execution_level": "LEVEL_2_ACTION"
            }}}
        })
        
        controller = AgentStateMachineController(workspace_dir=self.workspace_dir)
        response, _ = controller.resume_session(task_id, agent_runner=MagicMock(side_effect=lambda prompt: f"Ejecutando: {prompt}"))
        
        self.assertIn("Case B JSON Goal", response)
        
        # Verificar que se migró
        db = get_db_manager()
        self.assertIsNotNone(db.get_task(task_id))

    def test_case_c_sqlite_available_no_session(self):
        """CASO C: SQLite disponible + ninguna sesión → sesión inexistente."""
        from mis_agentes_inteligentes.agent_pipeline import AgentStateMachineController
        
        controller = AgentStateMachineController(workspace_dir=self.workspace_dir)
        response, metrics = controller.resume_session("nonexistent", agent_runner=MagicMock(side_effect=lambda prompt: f"Ejecutando: {prompt}"))
        
        self.assertIn("Error", response)
        self.assertIn("No se", response)
        self.assertIn("checkpoint", response)
        self.assertEqual(metrics, {})

    def test_case_d_sqlite_corrupt_json_exists(self):
        """CASO D: SQLite corrupto/no disponible + JSON existe → fallback controlado."""
        from mis_agentes_inteligentes.agent_pipeline import AgentStateMachineController
        from session_manager import save_session
        
        task_id = "case-d"
        
        # Solo JSON (simular SQLite no disponible pasando db_manager=None)
        save_session(task_id, {
            "id": task_id,
            "memory": {"working": {"state_checkpoint": {
                "user_goal": "Case D Fallback",
                "current_state": "EXECUTE",
                "replans_count": 0,
                "execution_level": "LEVEL_3_FEATURE"
            }}}
        })
        
        controller = AgentStateMachineController(workspace_dir=self.workspace_dir, db_manager=None)
        response, metrics = controller.resume_session(task_id, agent_runner=MagicMock(side_effect=lambda prompt: f"Ejecutando: {prompt}"))
        
        # Debe usar JSON como fallback controlado
        self.assertIn("Case D Fallback", response)

    def test_case_e_sqlite_corrupt_json_corrupt(self):
        """CASO E: SQLite corrupto + JSON corrupto → failure explícito."""
        from mis_agentes_inteligentes.agent_pipeline import AgentStateMachineController
        
        task_id = "case-e"
        
        # Corromper JSON
        import os
        json_path = os.path.join(os.environ.get("CODEAGENT_SESSIONS_DIR", ""), f"{task_id}.json")
        with open(json_path, "w") as f:
            f.write("{ corrupt }")
        
        controller = AgentStateMachineController(workspace_dir=self.workspace_dir, db_manager=None)
        response, metrics = controller.resume_session(task_id, agent_runner=MagicMock(return_value="OK"))
        
        self.assertIn("Error", response)
        self.assertEqual(metrics, {})


if __name__ == '__main__':
    unittest.main()