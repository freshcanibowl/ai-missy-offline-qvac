"""Local build/packaging audit. Does not claim QVAC offline success or DoraHacks submission."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
SOURCES = [
    'README.md', 'core.py', 'server.py', 'package.json', 'data/demo_case.json',
    'scripts/qvac-parse.mjs', 'scripts/offline-smoke.mjs', 'scripts/preload-model.mjs',
    'scripts/windows-build06.ps1', 'scripts/publish-new-repo.ps1', 'scripts/windows-offline-gate.ps1',
    'scripts/verify_offline_receipts.py', 'scripts/ship_audit.py',
    'web/index.html', 'web/app.js', 'web/style.css',
]

def run(args):
    try:
        p = subprocess.run(args, cwd=ROOT, text=True, capture_output=True, timeout=45)
        return {'status': 'PASS' if p.returncode == 0 else 'FAIL',
                'exit_code': p.returncode,
                'tail': (p.stdout + '\n' + p.stderr)[-1200:]}
    except (OSError, subprocess.TimeoutExpired) as e:
        return {'status': 'FAIL', 'error': type(e).__name__}

def audit():
    missing = [p for p in SOURCES if not (ROOT / p).is_file()]
    files = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest()
             for p in SOURCES if (ROOT / p).is_file()}
    tests = run([sys.executable, '-W', 'error::ResourceWarning', '-m', 'unittest', 'discover', '-s', 'tests', '-q'])
    node = shutil.which('node')
    checks = {}
    if node:
        for p in ['scripts/qvac-parse.mjs', 'scripts/offline-smoke.mjs',
                  'scripts/preload-model.mjs', 'web/app.js']:
            checks[p] = run([node, '--check', p])
    else:
        checks = {'node': {'status': 'NOT_RUN', 'reason': 'Node not installed on audit host'}}
    gitignore = (ROOT / '.gitignore').read_text(encoding='utf-8')
    ignored = ['node_modules/', '*.sqlite3', '.env', 'local-evidence/']
    no_sensitive_files = not any((ROOT / p).exists() for p in ['.env', 'missy_demo.sqlite3', 'node_modules', 'local-evidence'])
    code_pass = not missing and tests['status'] == 'PASS' and all(c['status'] == 'PASS' for c in checks.values()) and no_sensitive_files and all(x in gitignore for x in ignored)
    return {
        'schema': 'ai-missy-build06-release-audit/1',
        'generated_utc': datetime.now(timezone.utc).isoformat(),
        'code_gate': 'PASS' if code_pass else 'FAIL',
        'ship_gate': 'NO_GO_UNTIL_WINDOWS_QVAC_AND_EXTERNAL_SUBMISSION_VERIFIED',
        'source_sha256': files,
        'missing_source_files': missing,
        'unit_and_http_tests': tests,
        'javascript_syntax': checks,
        'sensitive_files_absent': no_sensitive_files,
        'gitignore_patterns_present': all(x in gitignore for x in ignored),
        'unverified': ['Windows Vulkan/Node compatibility', 'QVAC model preload',
                       'real disconnected-network QVAC inference', 'model license acceptance',
                       'remote participation eligibility', 'video evidence',
                       'GitHub publication', 'DoraHacks submission'],
        'mocked_test_notice': 'Build06 HTTP tests mock the QVAC subprocess; they are NOT model-inference evidence.'
    }

if __name__ == '__main__':
    r = audit()
    out = ROOT / 'docs' / 'BUILD06_RELEASE_RECEIPT.json'
    out.write_text(json.dumps(r, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('BUILD06_CODE_GATE=' + r['code_gate'])
    print('BUILD06_SHIP_GATE=' + r['ship_gate'])
    print('BUILD06_RECEIPT=' + str(out))
    sys.exit(0 if r['code_gate'] == 'PASS' else 1)
