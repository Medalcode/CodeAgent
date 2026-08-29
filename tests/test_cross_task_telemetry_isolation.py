"""
Tests de aislamiento de telemetría entre ejecuciones consecutivas (Cross-Task Isolation).
Garantiza que la secuencia ACTION -> CHAT -> CHAT en la misma instancia del backend no contamine la telemetría de los CHATs.
"""
import os
import sys
import unittest
from mis_agentes_inteligentes.agent_pipeline import AgentPipeline, ExecutionLevel, TaskType
from mis_agentes_inteligentes.tools import TERMINAL_TASKS_BUFFER, get_terminal_tasks_buffer


class TestCrossTaskTelemetryIsolation(unittest.TestCase):

    def setUp(self):
        self.workspace_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.pipeline = AgentPipeline(workspace_dir=self.workspace_dir)

    def test_action_chat_chat_isolation(self):
        """
        Garantiza que la secuencia ACTION -> CHAT -> CHAT aísle completamente
        la telemetría de herramientas entre peticiones consecutivas.
        """
        # 1. Petición A: Tarea ACTION que ejecuta un comando de terminal
        action_prompt = "Crea el archivo demo.py y ejecuta python demo.py"

        def action_runner(prompt):
            TERMINAL_TASKS_BUFFER.append({"command": "python demo.py", "exit_code": 0, "stdout": "DEMO_OK"})
            return "Ejecutado demo.py"

        _, metrics_a = self.pipeline.run(user_goal=action_prompt, agent_runner=action_runner)

        self.assertEqual(metrics_a.get("task_type"), "ACTION")
        self.assertEqual(metrics_a.get("execution_level"), ExecutionLevel.LEVEL_2_ACTION.value)
        self.assertEqual(metrics_a.get("tool_calls_count"), 1)
        self.assertEqual(metrics_a.get("execution_count"), 1)

        # 2. Petición B: Primer CHAT inmediatamente después en la MISMA instancia
        chat_prompt_1 = "Responde únicamente con OK."
        _, metrics_b = self.pipeline.run(user_goal=chat_prompt_1, agent_runner=lambda p: "OK")

        self.assertEqual(metrics_b.get("task_type"), "CHAT")
        self.assertEqual(metrics_b.get("execution_level"), ExecutionLevel.LEVEL_1_CHAT.value)
        self.assertEqual(metrics_b.get("tool_calls_count"), 0, "Primer CHAT no debe heredar ejecuciones de ACTION")
        self.assertEqual(metrics_b.get("execution_count"), 0)
        self.assertEqual(metrics_b.get("replans_count"), 0)

        # 3. Petición C: Segundo CHAT inmediatamente después en la MISMA instancia
        chat_prompt_2 = "Responde únicamente con OK. No ejecutes herramientas."
        _, metrics_c = self.pipeline.run(user_goal=chat_prompt_2, agent_runner=lambda p: "OK")

        self.assertEqual(metrics_c.get("task_type"), "CHAT")
        self.assertEqual(metrics_c.get("execution_level"), ExecutionLevel.LEVEL_1_CHAT.value)
        self.assertEqual(metrics_c.get("tool_calls_count"), 0, "Segundo CHAT tampoco debe heredar ejecuciones")
        self.assertEqual(metrics_c.get("execution_count"), 0)
        self.assertEqual(metrics_c.get("replans_count"), 0)


if __name__ == "__main__":
    unittest.main()
