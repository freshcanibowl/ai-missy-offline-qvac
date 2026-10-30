"""Check repo upload readiness. No network access, no automatic publishing."""
import json,re,sys,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REQUIRED=['README.md','SHIP_README.md','SHIP_STATUS.json','START_HERE_WINDOWS.ps1','RUN_SHIP_DIAGNOSTICS.ps1','scripts/ship_support.py','scripts/qvac-parse.mjs','scripts/preload-model.mjs','scripts/triage_windows.ps1','scripts/windows-build08.ps1','docs/DORAHACKS_SUBMISSION_DRAFT.md','docs/PRIOR_WORK_DISCLOSURE.md','package.json','.gitignore']
FORBIDDEN=['.env','local-evidence','node_modules','missy_demo.sqlite3']
missing=[x for x in REQUIRED if not (ROOT/x).is_file()]
ignore=(ROOT/'.gitignore').read_text(encoding='utf8')
ignored_missing=[x for x in ['node_modules/','local-evidence/','*.sqlite3','.env'] if x not in ignore]
text='\n'.join((ROOT/x).read_text(encoding='utf8',errors='replace') for x in ['README.md','SHIP_README.md','docs/DORAHACKS_SUBMISSION_DRAFT.md'])
# Strong warning if published copy claims unverified host inference is complete.
misleading=bool(re.search(r'(windows[_ ]qvac[_ ]offline|offline[_ ]inference)\s*[:=]\s*(pass|complete|verified)',text,re.I))
result={'schema':'ai-missy-submission-preflight/1','missing':missing,'gitignore_missing':ignored_missing,'misleading_claim':misleading,'sdk':json.loads((ROOT/'package.json').read_text())['dependencies'].get('@qvac/sdk'),'status':'PASS' if not missing and not ignored_missing and not misleading else 'FAIL','limitations':['does not run QVAC','does not verify GitHub or DoraHacks submission','does not verify offline video']}
print(json.dumps(result,indent=2))
sys.exit(0 if result['status']=='PASS' else 1)
