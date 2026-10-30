"""Real end-to-end Windows offline exercise: local HTTP -> actual QVAC subprocess -> SQLite.

This script never mocks inference. Run only AFTER disconnecting network adapters.
It cannot independently prove that the host has no network route; record uncut video.
"""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]


def http_json(base, path, token=None, data=None, timeout=190):
    headers = {}
    if data is not None:
        headers = {'Content-Type': 'application/json', 'Origin': base, 'X-Missy-Token': token or ''}
    payload = json.dumps(data).encode('utf-8') if data is not None else None
    request = urllib.request.Request(base + path, data=payload, headers=headers, method='POST' if data is not None else 'GET')
    try:
        with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(request, timeout=timeout) as response:
            return response.status, json.load(response)
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode('utf-8'))


def check_workflow(base, expected_initial=700):
    status, session = http_json(base, '/api/session')
    if status != 200 or not session.get('synthetic') or not isinstance(session.get('token'), str):
        raise RuntimeError('LOCAL_SESSION_FAILED')
    token = session['token']
    status, before = http_json(base, '/api/status')
    if status != 200 or before['summary']['recorded_ml'] != expected_initial:
        raise RuntimeError('SYNTHETIC_BASELINE_UNEXPECTED')
    status, parsed = http_json(base, '/api/parse', token, {'text': 'Log 200 ml water'})
    if status != 200:
        raise RuntimeError('REAL_QVAC_HTTP_PARSE_FAILED:' + parsed.get('error', 'UNKNOWN'))
    pending = parsed.get('pending', {})
    proof = parsed.get('proof', {})
    if pending.get('volume_ml') != 200 or proof.get('engine') != 'QVAC_LOCAL' or proof.get('model') != 'LLAMA_3_2_1B_INST_Q4_0':
        raise RuntimeError('REAL_QVAC_HTTP_CONTRACT_FAILED')
    status, confirmed = http_json(base, '/api/confirm', token, pending)
    if status != 200 or confirmed.get('persisted') is not True or confirmed['summary']['recorded_ml'] != expected_initial + 200:
        raise RuntimeError('SQLITE_CONFIRMATION_FAILED')
    status, after = http_json(base, '/api/status')
    if status != 200 or after['summary']['recorded_ml'] != expected_initial + 200:
        raise RuntimeError('SQLITE_READBACK_FAILED')
    status, replay = http_json(base, '/api/confirm', token, pending)
    if status != 422 or replay.get('error') != 'NO_VALID_QVAC_PENDING_CONFIRMATION':
        raise RuntimeError('REPLAY_NOT_REJECTED')
    status, food = http_json(base, '/api/food', token, {'name': 'banana'})
    if status != 200 or food.get('status') != 'INSUFFICIENT_DATA':
        raise RuntimeError('FOOD_ABSTENTION_FAILED')
    return {
        'schema': 'ai-missy-build07-real-http-e2e/1',
        'result': 'HOST_OBSERVED_E2E_PASS',
        'generated_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'synthetic': True,
        'model': proof['model'],
        'engine': proof['engine'],
        'qvac_parse_latency_ms': proof.get('latency_ms'),
        'initial_recorded_ml': expected_initial,
        'confirmed_recorded_ml': after['summary']['recorded_ml'],
        'confirmation_persisted': True,
        'replay_rejected': True,
        'food_abstention': True,
        'network_isolation': 'NOT_INDEPENDENTLY_ATTESTED',
        'note': 'The HTTP parse path ran the actual QVAC Node subprocess; no model mock is installed. Host isolation requires video review.'
    }


def run_live(output):
    with tempfile.TemporaryDirectory(prefix='missy-real-e2e-') as tmp:
        db = Path(tmp) / 'e2e.sqlite3'
        with socket.socket() as s:
            s.bind(('127.0.0.1', 0))
            port = s.getsockname()[1]
        base = f'http://127.0.0.1:{port}'
        env = os.environ.copy()
        env['MISSY_DB_PATH'] = str(db)
        env['MISSY_PORT'] = str(port)
        log_path = Path(tmp) / 'server.log'
        with log_path.open('w', encoding='utf-8') as logfile:
            proc = subprocess.Popen([sys.executable, str(ROOT / 'server.py')], cwd=ROOT, env=env,
                                    stdout=logfile, stderr=subprocess.STDOUT)
            try:
                for _ in range(60):
                    if proc.poll() is not None:
                        raise RuntimeError('LOCAL_SERVER_EXITED')
                    try:
                        status, _ = http_json(base, '/api/session', timeout=1)
                        if status == 200:
                            break
                    except (OSError, TimeoutError):
                        time.sleep(.2)
                else:
                    raise RuntimeError('LOCAL_SERVER_NOT_READY')
                result = check_workflow(base)
                result['server_sha256'] = hashlib.sha256((ROOT / 'server.py').read_bytes()).hexdigest()
                result['qvac_adapter_sha256'] = hashlib.sha256((ROOT / 'scripts' / 'qvac-parse.mjs').read_bytes()).hexdigest()
                result['local_db_removed_after_test'] = True
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
                print('BUILD07_REAL_HTTP_E2E=HOST_OBSERVED_PASS')
                print('E2E_RECEIPT=' + str(output))
                return 0
            finally:
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait(timeout=5)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    try:
        sys.exit(run_live(Path(args.output)))
    except Exception as exc:
        print('BUILD07_REAL_HTTP_E2E=FAIL ' + str(exc), file=sys.stderr)
        sys.exit(1)
