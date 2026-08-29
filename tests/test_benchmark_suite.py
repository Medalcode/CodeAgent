import os
import unittest
from unittest.mock import MagicMock

try:
    from mis_agentes_inteligentes.benchmark_suite import CodeAgentBenchmarkSuite
except ImportError:
    from benchmark_suite import CodeAgentBenchmarkSuite


class TestCodeAgentBenchmarkSuite(unittest.TestCase):

    def setUp(self):
        os.environ["SKIP_SUBPROCESS_TESTS"] = "1"
        self.suite = CodeAgentBenchmarkSuite()

    def test_get_benchmark_tasks_returns_5_tasks(self):
        tasks = self.suite.get_benchmark_tasks()
        self.assertEqual(len(tasks), 5)
        task_ids = [t["id"] for t in tasks]
        self.assertIn("TASK_01", task_ids)
        self.assertIn("TASK_02", task_ids)
        self.assertIn("TASK_03", task_ids)
        self.assertIn("TASK_04", task_ids)
        self.assertIn("TASK_05", task_ids)

    def test_run_suite_execution(self):
        mock_runner = MagicMock(return_value="Respuesta del runner para tarea de benchmark")
        summary = self.suite.run_suite(agent_runner=mock_runner)

        self.assertIn("total_tasks", summary)
        self.assertEqual(summary["total_tasks"], 5)
        self.assertIn("success_rate_pct", summary)
        self.assertIn("tasks_results", summary)
        self.assertEqual(len(summary["tasks_results"]), 5)

        # Verificar que se haya generado el archivo de reporte markdown
        report_path = os.path.join(self.suite.workspace_dir, "mis_agentes_inteligentes", "benchmark_report_v42.md")
        self.assertTrue(os.path.exists(report_path))


if __name__ == "__main__":
    unittest.main()
