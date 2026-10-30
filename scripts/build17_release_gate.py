"""Build 17: local-only code and release readiness gate. Never publishes."""
from __future__ import annotations
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JS = ('scripts/preload-model.mjs', 'scripts/offline-smoke.mjs', 'scripts/qvac-parse.mjs', 'web/app.js')
REQUIRED = ('core.py', 'server.py', 'package.json', 'package-lock.json', 'data/demo_case.json',
            'docs/JUDGE_REPRODUCE.md', 'docs/PRIOR_WORK_DISCLOSURE.md', *JS)

def run(args, timeout=120):
    try:
        p = subprocess.run(args, cwd=ROOT, text=True, capture_output=True, timeout=timeout)
        return {'status': 'PASS' if p.returncode == 0 else 'FAIL',
                'exit_code': p.returncode, 'tail': (p.stdout + '\n' + p.stderr)[-1200:]}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {'status': 'NOT_RUN', 'reason': type(exc).__name__}

def main():
    missing = [x for x in REQUIRED if not (ROOT / x).is_file()]
    tests = run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-v'])
    js = {x: run(['node', '--check', str(ROOT / x)], 15) for x in JS}
    readme = (ROOT / 'README.md').read_text(encoding='utf-8', errors='replace')
    docs_current = 'NO GITHUB PUBLICATION' not in readme and 'REAL WINDOWS QVAC OFFLINE UNVERIFIED' not in readme
    code_ok = not missing and tests['status'] == 'PASS' and bool(re.search(r'Ran \d+ tests?', tests.get('tail', ''))) and all(x['status'] == 'PASS' for x in js.values())
    result = {'schema': 'ai-missy-build17-release-gate/1',
              'generated_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
              'scope': 'local code tests only; NOT real Windows QVAC inference',
              'missing_files': missing, 'python_tests': tests, 'javascript_syntax': js,
              'readme_status_current': docs_current, 'licenses': 'PENDING_REVIEW',
              'windows_offline_qvac': 'NOT_VERIFIED_BY_THIS_SCRIPT',
              'uncut_video': 'NOT_VERIFIED_BY_THIS_SCRIPT',
              'code_gate': 'PASS' if code_ok else 'FAIL', 'public_release_gate': 'NO_GO'}
    output = ROOT / 'local-evidence' / 'BUILD17_RELEASE_GATE.json'
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print('BUILD17_CODE_GATE=' + result['code_gate'])
    print('BUILD17_PUBLIC_RELEASE=NO_GO')
    print('BUILD17_RECEIPT=' + str(output))
    return 0 if code_ok else 1

if __name__ == '__main__':
    sys.exit(main())
