"""Read-only source and local tests audit. Never certifies QVAC host inference."""
import json, hashlib, subprocess, sys, datetime, shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
FILES=['core.py','server.py','package.json','scripts/qvac-parse.mjs','scripts/offline-smoke.mjs','scripts/windows-build08.ps1','tests/test_build08_safety.py']
def run(args):
    try:
        p=subprocess.run(args,cwd=ROOT,capture_output=True,text=True,timeout=75)
        return {'status':'PASS' if p.returncode==0 else 'FAIL','exit_code':p.returncode,'tail':(p.stdout+p.stderr)[-1400:]}
    except (OSError,subprocess.TimeoutExpired) as e:return {'status':'NOT_RUN','reason':str(e)}
def main():
    missing=[p for p in FILES if not (ROOT/p).is_file()]
    tests=run([sys.executable,'-W','error::ResourceWarning','-m','unittest','discover','-s','tests','-q'])
    js={p:run(['node','--check',p]) for p in ['scripts/qvac-parse.mjs','scripts/offline-smoke.mjs','web/app.js']} if shutil.which('node') else {'node':{'status':'NOT_RUN'}}
    gate='PASS' if not missing and tests['status']=='PASS' and all(x['status']=='PASS' for x in js.values()) else 'FAIL'
    report={'schema':'ai-missy-build08-code-audit/1','generated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'code_gate':gate,'ship_gate':'NO_GO_UNTIL_WINDOWS_QVAC_EVIDENCE_AND_PUBLIC_SUBMISSION',
            'missing_files':missing,'tests':tests,'javascript_syntax':js,
            'source_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in FILES if (ROOT/p).is_file()},
            'not_verified':['QVAC model downloaded','Windows Vulkan','Windows real offline inference','Uncut video','GitHub repository','DoraHacks submission'],
            'limitations':'No model or QVAC SDK in this artifact; no clinical validation.'}
    path=ROOT/'docs/BUILD08_CODE_AUDIT.json';path.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    print('BUILD08_CODE_GATE='+gate);print('BUILD08_SHIP_GATE='+report['ship_gate']);print('BUILD08_AUDIT_FILE='+str(path))
    return 0 if gate=='PASS' else 1
if __name__=='__main__':sys.exit(main())
