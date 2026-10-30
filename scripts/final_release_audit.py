"""Reproducible local-only audit. Never reports QVAC offline success."""
from pathlib import Path
import subprocess,sys,hashlib,json,datetime
ROOT=Path(__file__).resolve().parents[1]
OUTPUT=ROOT/'local-evidence'/'FINAL_LOCAL_CODE_AUDIT.json'
REQUIRED=['FINAL_WINDOWS_RUN.ps1','START_HERE_WINDOWS.ps1','RUN_SHIP_DIAGNOSTICS.ps1','core.py','server.py','scripts/qvac-parse.mjs','scripts/offline-smoke.mjs','scripts/preload-model.mjs','scripts/windows-offline-gate.ps1','scripts/publish-new-repo.ps1','package.json','web/index.html','web/app.js','web/style.css','data/demo_case.json']
missing=[f for f in REQUIRED if not (ROOT/f).is_file()]
cmd=[sys.executable,'-m','unittest','discover','-s','tests','-v']
run=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,timeout=120)
import re
m=re.search(r'Ran (\d+) tests?',run.stderr)
node_checks={}
for f in ['scripts/qvac-parse.mjs','scripts/offline-smoke.mjs','scripts/preload-model.mjs','web/app.js']:
    try:
        p=subprocess.run(['node','--check',str(ROOT/f)],capture_output=True,text=True,timeout=15)
        node_checks[f]='PASS' if p.returncode==0 else 'FAIL'
    except (OSError,subprocess.TimeoutExpired):node_checks[f]='NOT_RUN'
result={'schema':'ai-missy-final-local-audit/1','generated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
'missing_files':missing,'python_tests':{'exit_code':run.returncode,'count':int(m.group(1)) if m else None,'result':'PASS' if run.returncode==0 else 'FAIL'},
'javascript_syntax':node_checks,'source_sha256':{f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in REQUIRED if (ROOT/f).is_file()},
'windows_qvac_offline':'NOT_TESTED_IN_THIS_ENVIRONMENT','uncut_video':'NOT_VERIFIED','github_published':'NOT_VERIFIED','dorahacks_submitted':'NOT_VERIFIED'}
result['local_code_status']='PASS' if not missing and run.returncode==0 and all(v=='PASS' for v in node_checks.values()) else 'FAIL'
OUTPUT.parent.mkdir(exist_ok=True)
OUTPUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('FINAL_LOCAL_CODE_AUDIT='+result['local_code_status'])
print('TEST_COUNT='+str(result['python_tests']['count']))
print('QVAC_OFFLINE=NOT_VERIFIED')
print('AUDIT_PATH='+str(OUTPUT))
sys.exit(0 if result['local_code_status']=='PASS' else 1)
