"""Generate a minimal, redacted diagnostic bundle. Never includes patient data or raw logs."""
import argparse, hashlib, json, re, subprocess, sys, zipfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
SAFE_TRIAGE_KEYS = ('node','npm','python','git','github_cli','qvac_sdk_installed',
                    'node_compatible','windows','os_64bit','vulkaninfo_available',
                    'vulkan_1_4_verified','vulkan_diagnostic','next_action')

def create_report(triage_file=None, run_tests=True):
    triage = {}
    if triage_file and Path(triage_file).is_file():
        raw = json.loads(Path(triage_file).read_text(encoding='utf-8-sig'))
        if not isinstance(raw,dict): raise ValueError('TRIAGE_NOT_OBJECT')
        triage = {k: raw[k] for k in SAFE_TRIAGE_KEYS if k in raw and type(raw[k]) in (str,bool,int,float)}
    test = {'status':'NOT_RUN','count':None}
    if run_tests:
        p = subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-q'],
                           cwd=ROOT, capture_output=True, text=True, timeout=120)
        match = re.search(r'Ran (\d+) tests?', p.stdout+'\n'+p.stderr)
        count = int(match.group(1)) if match else None
        ok = p.returncode == 0 and bool(re.search(r'(?m)^OK\s*$',p.stderr)) and count is not None
        test = {'status':'PASS' if ok else 'FAIL', 'count':count}
    paths = ('core.py','server.py','scripts/qvac-parse.mjs','scripts/offline-smoke.mjs','package.json')
    hashes = {p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths}
    return {'schema':'ai-missy-ship-support/1','scope':'SYNTHETIC_DEMO_ONLY',
            'windows_diagnostics':triage,'local_tests':test,'source_sha256':hashes,
            'qvac_real_offline':'NOT_VERIFIED_BY_THIS_SCRIPT',
            'network_isolation':'NOT_VERIFIED_BY_THIS_SCRIPT',
            'git_published':'NOT_VERIFIED_BY_THIS_SCRIPT',
            'dorahacks_submitted':'NOT_VERIFIED_BY_THIS_SCRIPT',
            'next_step':'Run PrepareOnline on Windows; then disconnect all networks and run VerifyOffline.',
            'privacy':'Only allowlisted host facts, test count/status and source hashes; no raw logs, identifiers or health data.'}

def write_bundle(output, triage_file=None, run_tests=True):
    output = Path(output)
    output.parent.mkdir(parents=True,exist_ok=True)
    report = create_report(triage_file,run_tests)
    payload = (json.dumps(report,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED) as z:
        z.writestr('SHIP_SUPPORT_REDACTED.json',payload)
    return report

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--triage',default=str(ROOT/'local-evidence'/'WINDOWS_TRIAGE.json'))
    ap.add_argument('--output',default=str(ROOT/'local-evidence'/'AI_MISSY_SHIP_SUPPORT.zip'))
    ap.add_argument('--no-tests',action='store_true')
    args=ap.parse_args()
    try:
        report=write_bundle(args.output,args.triage,not args.no_tests)
        print('SHIP_SUPPORT_TESTS='+report['local_tests']['status'])
        print('SHIP_SUPPORT_TEST_COUNT='+str(report['local_tests']['count']))
        print('SHIP_SUPPORT_QVAC_OFFLINE=NOT_VERIFIED')
        print('SHIP_SUPPORT_ZIP='+str(Path(args.output).resolve()))
        sys.exit(0 if report['local_tests']['status']!='FAIL' else 1)
    except Exception as exc:
        print('SHIP_SUPPORT_FAILED='+type(exc).__name__+': '+str(exc),file=sys.stderr)
        sys.exit(1)
