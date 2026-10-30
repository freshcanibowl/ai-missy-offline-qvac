"""Explicitly MOCKED QVAC transport tests. Not evidence of offline AI inference."""
import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch
from subprocess import CompletedProcess
import server

class MockedQvacHttpTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.old_db = server.DB
        server.DB = Path(self.tmp.name) / 'demo.sqlite3'
        server.PENDING.clear()
        self.httpd = ThreadingHTTPServer(('127.0.0.1', 0), server.Handler)
        self.port = self.httpd.server_port
        self.base = f'http://127.0.0.1:{self.port}'
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()
        self.token = self.request('/api/session')[1]['token']

    def tearDown(self):
        self.httpd.shutdown()
        self.httpd.server_close()
        self.thread.join(timeout=5)
        server.DB = self.old_db
        server.PENDING.clear()
        self.tmp.cleanup()

    def request(self, path, body=None):
        headers = {}
        if body is not None:
            headers = {'Content-Type': 'application/json', 'Origin': self.base, 'X-Missy-Token': self.token}
        req = urllib.request.Request(self.base + path,
                                     data=json.dumps(body).encode() if body is not None else None,
                                     headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=5) as r:
                return r.status, json.load(r)
        except urllib.error.HTTPError as e:
            return e.code, json.load(e)

    @staticmethod
    def fake_completion(ml=200):
        """Test fixture only: never included in the product runtime."""
        envelope = {'engine': 'QVAC_LOCAL', 'model': 'LLAMA_3_2_1B_INST_Q4_0',
                    'latency_ms': 12, 'stop_reason': 'eos',
                    'parsed': {'action': 'LOG_FLUID', 'volume_ml': ml, 'unit': 'ml', 'confidence': 0.95}}
        return CompletedProcess(args=['node'], returncode=0, stdout=json.dumps(envelope), stderr='')

    def test_mocked_extraction_confirmation_and_replay(self):
        with patch.object(server.subprocess, 'run', return_value=self.fake_completion()):
            status, proposal = self.request('/api/parse', {'text': 'Log 200 ml water'})
        self.assertEqual(status, 200)
        self.assertTrue(proposal['needs_confirmation'])
        status, saved = self.request('/api/confirm', proposal['pending'])
        self.assertEqual(status, 200)
        self.assertEqual(saved['summary']['recorded_ml'], 900)
        status, err = self.request('/api/confirm', proposal['pending'])
        self.assertEqual(status, 422)
        self.assertEqual(err['error'], 'NO_VALID_QVAC_PENDING_CONFIRMATION')

    def test_database_failure_does_not_consume_pending(self):
        with patch.object(server.subprocess, 'run', return_value=self.fake_completion()):
            status, proposal = self.request('/api/parse', {'text': 'Log 200 ml water'})
        self.assertEqual(status, 200)
        real_confirm = server.confirm
        calls = [0]
        def transient_failure(*args, **kwargs):
            calls[0] += 1
            if calls[0] == 1:
                raise RuntimeError('TEST_SIMULATED_DATABASE_FAILURE')
            return real_confirm(*args, **kwargs)
        with patch.object(server, 'confirm', side_effect=transient_failure):
            first, _ = self.request('/api/confirm', proposal['pending'])
            second, saved = self.request('/api/confirm', proposal['pending'])
        self.assertEqual(first, 500)
        self.assertEqual(second, 200)
        self.assertEqual(saved['summary']['recorded_ml'], 900)

    def test_model_quantity_mismatch_is_rejected(self):
        with patch.object(server.subprocess, 'run', return_value=self.fake_completion(300)):
            status, response = self.request('/api/parse', {'text': 'Log 200 ml water'})
        self.assertEqual(status, 422)
        self.assertEqual(response['error'], 'INPUT_QUANTITY_NOT_VERIFIED')
        self.assertFalse(server.PENDING)

    def test_negated_logging_is_rejected(self):
        with patch.object(server.subprocess, 'run', return_value=self.fake_completion()):
            status, response = self.request('/api/parse', {'text': "Don't log 200 ml water"})
        self.assertEqual(status, 422)
        self.assertEqual(response['error'], 'NEGATED_OR_CANCELLED_LOG')
        self.assertFalse(server.PENDING)

    def test_qvac_unavailable_fails_closed(self):
        with patch.object(server.subprocess, 'run', side_effect=FileNotFoundError('node absent')):
            status, response = self.request('/api/parse', {'text': 'Log 200 ml water'})
        self.assertEqual(status, 503)
        self.assertEqual(response['error'], 'QVAC_INFERENCE_UNAVAILABLE')
        self.assertFalse(server.PENDING)

    def test_pending_limit_rejects_new_extraction(self):
        import time
        for i in range(100):
            server.PENDING[str(i)] = {'ml': 200, 'text': 'Log 200 ml water', 'expires': time.monotonic()+300}
        with patch.object(server.subprocess, 'run', return_value=self.fake_completion()):
            status, response = self.request('/api/parse', {'text': 'Log 200 ml water'})
        self.assertEqual(status, 422)
        self.assertEqual(response['error'], 'TOO_MANY_PENDING_REQUESTS')
        self.assertEqual(len(server.PENDING), 100)

if __name__ == '__main__':
    unittest.main()
