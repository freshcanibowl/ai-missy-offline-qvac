
"""Read-only evidence auditor. No network, no GitHub writes, no fabricated PASS."""
import argparse, json, hashlib, pathlib, datetime, subprocess, sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def audit(evidence, video, repo_url, submission_url):
    evidence=pathlib.Path(evidence)
    results={}
    srcs=['core.py','server.py','scripts/qvac-parse.mjs','scripts/offline-smoke.mjs','scripts/preload-model.mjs','package.json']
    results['source_integrity']={'status':'PASS' if all((ROOT/x).is_file() for x in srcs) else 'FAIL',
                                 'sha256':{x:sha(ROOT/x) for x in srcs if (ROOT/x).is_file()}}
    receipts=sorted(evidence.glob('qvac-verified-*.json')) if evidence.exists() else []
    valid=[]
    for p in receipts:
        try:
            r=json.loads(p.read_text(encoding='utf-8-sig'))
            if r.get('receipt_status')!='HOST_OBSERVED_QVAC_PASS':continue
            if r.get('model')!='LLAMA_3_2_1B_INST_Q4_0':continue
            stamp=p.name.removeprefix('qvac-verified-').removesuffix('.json')
            sm=evidence/f'qvac-smoke-{stamp}.jsonl';pa=evidence/f'qvac-parse-{stamp}.jsonl'
            if not sm.is_file() or not pa.is_file():continue
            if r.get('smoke_sha256')!=sha(sm) or r.get('parse_sha256')!=sha(pa):continue
            # Revalidate the semantic contents, not merely the self-reported status.
            sys.path.insert(0,str(ROOT/'scripts'))
            from verify_offline_receipts import read_one, verify
            verify(read_one(sm),read_one(pa))
            valid.append({'name':p.name,'sha256':sha(p)})
        except (OSError,ValueError,KeyError,TypeError,ImportError):continue
    results['qvac_host_observed']={'status':'HOST_OBSERVED_ONLY' if valid else 'PENDING','valid_receipts':valid,
                                 'limitation':'Not independent proof of network isolation or SDK provenance.'}
    # A second independent application-path gate: HTTP -> real Node QVAC -> SQLite.
    # This receipt is host-generated and cannot by itself prove network isolation.
    e2e_valid=[]
    for ep in sorted(evidence.glob('qvac-http-e2e-*.json')) if evidence.exists() else []:
        try:
            e=json.loads(ep.read_text(encoding='utf-8-sig'))
            if e.get('schema')!='ai-missy-build07-real-http-e2e/1' or e.get('result')!='HOST_OBSERVED_E2E_PASS':continue
            if e.get('synthetic') is not True or e.get('engine')!='QVAC_LOCAL' or e.get('model')!='LLAMA_3_2_1B_INST_Q4_0':continue
            if e.get('initial_recorded_ml')!=700 or e.get('confirmed_recorded_ml')!=900:continue
            if e.get('confirmation_persisted') is not True or e.get('replay_rejected') is not True or e.get('food_abstention') is not True:continue
            if e.get('server_sha256')!=sha(ROOT/'server.py') or e.get('qvac_adapter_sha256')!=sha(ROOT/'scripts/qvac-parse.mjs'):continue
            stamp=ep.name.removeprefix('qvac-http-e2e-').removesuffix('.json')
            if not (evidence/f'qvac-verified-{stamp}.json').is_file():continue
            e2e_valid.append({'name':ep.name,'sha256':sha(ep)})
        except (OSError,ValueError,KeyError,TypeError):continue
    results['qvac_real_http_e2e']={'status':'HOST_OBSERVED_ONLY' if e2e_valid else 'PENDING',
                                   'valid_receipts':e2e_valid,
                                   'limitation':'Receipts are not independently attested; continuous offline video still required.'}
    v=pathlib.Path(video) if video else None
    results['uncut_video']={'status':'FILE_PRESENT_UNREVIEWED' if v and v.is_file() and v.stat().st_size>0 else 'PENDING',
                            'sha256':sha(v) if v and v.is_file() and v.stat().st_size>0 else None,
                            'limitation':'Video content and actual disconnection must be independently reviewed.'}
    results['public_repo']={'status':'URL_PROVIDED_UNVERIFIED' if repo_url and repo_url.startswith('https://github.com/') else 'PENDING','url':repo_url or None}
    results['organizer_submission']={'status':'URL_PROVIDED_UNVERIFIED' if submission_url and submission_url.startswith('https://') else 'PENDING','url':submission_url or None}
    results['model_license_review']={'status':'PENDING','note':'Human review of Meta Llama 3.2 and QVAC SDK terms required.'}
    results['remote_eligibility']={'status':'PENDING','note':'In-person/remote eligibility must be confirmed with organizer.'}
    # We cannot assert SHIP PASS based only on file existence or self-attestation.
    return {'schema':'ai-missy-build07-ship-audit/1','generated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'decision':'NO_GO_UNTIL_EXTERNAL_VERIFICATION','results':results}
def main():
    p=argparse.ArgumentParser();p.add_argument('--evidence',default=str(ROOT/'local-evidence'))
    p.add_argument('--video',default='');p.add_argument('--repo-url',default='');p.add_argument('--submission-url',default='')
    p.add_argument('--output',default=str(ROOT/'local-evidence'/'BUILD07_SHIP_AUDIT.json'))
    a=p.parse_args();result=audit(a.evidence,a.video,a.repo_url,a.submission_url)
    out=pathlib.Path(a.output);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for k,v in result['results'].items():print(k+'='+v['status'])
    print('BUILD07_SHIP_GATE='+result['decision']);print('AUDIT_FILE='+str(out))
if __name__=='__main__':main()
