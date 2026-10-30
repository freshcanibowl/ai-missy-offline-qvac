"""Tests for the E2E verifier itself. Uses a stub HTTP service, NOT real QVAC."""
import unittest
from unittest.mock import patch
from scripts.live_http_e2e import check_workflow


class TestBuild07E2E(unittest.TestCase):
    def test_successful_contract_with_mocked_http(self):
        responses = [
            (200, {'synthetic': True, 'token': 'demo-token'}),
            (200, {'summary': {'recorded_ml': 700}}),
            (200, {'pending': {'request_id': 'id', 'volume_ml': 200, 'source': 'Log 200 ml water'},
                   'proof': {'engine': 'QVAC_LOCAL', 'model': 'LLAMA_3_2_1B_INST_Q4_0', 'latency_ms': 50}}),
            (200, {'persisted': True, 'summary': {'recorded_ml': 900}}),
            (200, {'summary': {'recorded_ml': 900}}),
            (422, {'error': 'NO_VALID_QVAC_PENDING_CONFIRMATION'}),
            (200, {'status': 'INSUFFICIENT_DATA'}),
        ]
        with patch('scripts.live_http_e2e.http_json', side_effect=responses) as mock:
            receipt = check_workflow('http://127.0.0.1:9999')
        self.assertEqual(mock.call_count, 7)
        self.assertEqual(receipt['result'], 'HOST_OBSERVED_E2E_PASS')
        self.assertEqual(receipt['network_isolation'], 'NOT_INDEPENDENTLY_ATTESTED')

    def test_rejects_wrong_qvac_model(self):
        responses = [(200, {'synthetic': True, 'token': 'x'}),
                     (200, {'summary': {'recorded_ml': 700}}),
                     (200, {'pending': {'volume_ml': 200}, 'proof': {'engine': 'MOCK', 'model': 'OTHER'}})]
        with patch('scripts.live_http_e2e.http_json', side_effect=responses):
            with self.assertRaisesRegex(RuntimeError, 'REAL_QVAC_HTTP_CONTRACT_FAILED'):
                check_workflow('http://127.0.0.1:9999')

    def test_rejects_no_sqlite_persistence(self):
        responses = [(200, {'synthetic': True, 'token': 'x'}),
                     (200, {'summary': {'recorded_ml': 700}}),
                     (200, {'pending': {'volume_ml': 200}, 'proof': {'engine': 'QVAC_LOCAL', 'model': 'LLAMA_3_2_1B_INST_Q4_0'}}),
                     (200, {'persisted': False, 'summary': {'recorded_ml': 700}})]
        with patch('scripts.live_http_e2e.http_json', side_effect=responses):
            with self.assertRaisesRegex(RuntimeError, 'SQLITE_CONFIRMATION_FAILED'):
                check_workflow('http://127.0.0.1:9999')

    def test_rejects_replay_not_rejected(self):
        responses = [(200, {'synthetic': True, 'token': 'x'}),
                     (200, {'summary': {'recorded_ml': 700}}),
                     (200, {'pending': {'volume_ml': 200}, 'proof': {'engine': 'QVAC_LOCAL', 'model': 'LLAMA_3_2_1B_INST_Q4_0'}}),
                     (200, {'persisted': True, 'summary': {'recorded_ml': 900}}),
                     (200, {'summary': {'recorded_ml': 900}}),
                     (200, {'persisted': True})]
        with patch('scripts.live_http_e2e.http_json', side_effect=responses):
            with self.assertRaisesRegex(RuntimeError, 'REPLAY_NOT_REJECTED'):
                check_workflow('http://127.0.0.1:9999')

    def test_rejects_food_false_assurance(self):
        responses = [(200, {'synthetic': True, 'token': 'x'}),
                     (200, {'summary': {'recorded_ml': 700}}),
                     (200, {'pending': {'volume_ml': 200}, 'proof': {'engine': 'QVAC_LOCAL', 'model': 'LLAMA_3_2_1B_INST_Q4_0'}}),
                     (200, {'persisted': True, 'summary': {'recorded_ml': 900}}),
                     (200, {'summary': {'recorded_ml': 900}}),
                     (422, {'error': 'NO_VALID_QVAC_PENDING_CONFIRMATION'}),
                     (200, {'status': 'SAFE'})]
        with patch('scripts.live_http_e2e.http_json', side_effect=responses):
            with self.assertRaisesRegex(RuntimeError, 'FOOD_ABSTENTION_FAILED'):
                check_workflow('http://127.0.0.1:9999')

if __name__ == '__main__':
    unittest.main()
