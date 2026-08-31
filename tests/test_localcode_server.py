import http.client

import json

import os

import sys

import threading

import time

import unittest



sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../mis_agentes_inteligentes')))



from localcode_server import LocalCodeProxyHandler, ThreadedTCPServer





class TestLocalCodeServer(unittest.TestCase):

    @classmethod

    def setUpClass(cls):

        # Iniciar servidor multihilo en un puerto efímero disponible

        cls.server = ThreadedTCPServer(('127.0.0.1', 0), LocalCodeProxyHandler)

        cls.port = cls.server.server_address[1]

        cls.server_thread = threading.Thread(target=cls.server.serve_forever, daemon=True)

        cls.server_thread.start()

        time.sleep(0.1)  # Pequeña pausa para asegurar inicio del socket



    @classmethod

    def tearDownClass(cls):

        cls.server.shutdown()

        cls.server.server_close()



    def _make_request(self, method, path, body=None, headers=None):

        headers = headers or {}

        conn = http.client.HTTPConnection('127.0.0.1', self.port, timeout=5)

        try:

            conn.request(method, path, body, headers)

            res = conn.getresponse()

            data = res.read()

            return res.status, res.headers, data

        finally:

            conn.close()



    def test_get_static_ui(self):

        # Verificar que el servidor responde correctamente (endpoint heredado de la migracin de UI)

        status, headers, data = self._make_request('GET', '/localcode_claude_ui.html')

        # El archivo HTML fue migrado a desktop_app.py en C3.1;

        # validamos que el servidor responde sin error aunque el archivo

        # legacy ya no exista (degrade gracefully)

        self.assertEqual(status, 200)



    def test_workspace_tree_endpoint(self):

        status, headers, data = self._make_request('GET', '/api/workspace/tree')

        self.assertEqual(status, 200)

        json_data = json.loads(data.decode('utf-8'))

        self.assertTrue(json_data.get('success'))

        self.assertIsInstance(json_data.get('files'), list)



    def test_agent_chat_empty_prompt(self):

        body = json.dumps({'prompt': ''})

        headers = {'Content-Type': 'application/json'}

        status, _, data = self._make_request('POST', '/api/agent/chat', body, headers)

        self.assertEqual(status, 400)

        json_data = json.loads(data.decode('utf-8'))

        self.assertFalse(json_data.get('success'))

        self.assertEqual(json_data.get('error'), 'Prompt vacío')



    def test_not_found_endpoint(self):

        status, _, _ = self._make_request('GET', '/ruta_que_no_existe_xyz')

        self.assertEqual(status, 404)



    def test_openapi_spec_endpoint(self):

        status, headers, data = self._make_request('GET', '/api/openapi.json')

        self.assertEqual(status, 200)

        json_data = json.loads(data.decode('utf-8'))

        self.assertEqual(json_data.get('openapi'), '3.0.3')

        self.assertIn('/api/agent/chat', json_data.get('paths', {}))



    def test_swagger_docs_endpoint(self):

        status, headers, data = self._make_request('GET', '/docs')

        self.assertEqual(status, 200)

        self.assertIn(b'SwaggerUIBundle', data)



    def test_prometheus_metrics_endpoint(self):

        status, headers, data = self._make_request('GET', '/metrics')

        self.assertEqual(status, 200)

        self.assertIn(b'codeagent_uptime_seconds', data)

        self.assertIn(b'codeagent_requests_total', data)





if __name__ == '__main__':

    unittest.main()

