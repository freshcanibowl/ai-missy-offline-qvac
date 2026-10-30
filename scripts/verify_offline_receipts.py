"""Verify semantic shape of QVAC evidence. Cannot independently attest disconnected network."""
import json, sys, pathlib, datetime, hashlib

def read_one(path):
    raw=pathlib.Path(path).read_bytes()
    if raw.startswith(b'\xff\xfe') or raw.startswith(b'\xfe\xff'):
        lines=raw.decode('utf-16').splitlines()
    else:
        lines=raw.decode('utf-8-sig').splitlines()
    objs=[]
    for line in lines:
        try: obj=json.loads(line)
        except json.JSONDecodeError: continue
        if isinstance(obj,dict): objs.append(obj)
    if len(objs)!=1: raise ValueError('EXPECTED_ONE_JSON_RESULT')
    return objs[0]

def verify(smoke,parse):
    if smoke.get('engine')!='QVAC_LOCAL' or smoke.get('model')!='LLAMA_3_2_1B_INST_Q4_0' or smoke.get('model_loaded') is not True or smoke.get('offline_inference_completed') is not True:
        raise ValueError('QVAC_SMOKE_NOT_PROVEN')
    if 'LOCAL' not in smoke.get('generated_text','').upper():raise ValueError('SMOKE_SEMANTIC_FAIL')
    if parse.get('engine')!='QVAC_LOCAL' or parse.get('model')!='LLAMA_3_2_1B_INST_Q4_0':raise ValueError('QVAC_PARSE_NOT_PROVEN')
    p=parse.get('parsed')
    if not isinstance(p,dict) or set(p)!={'action','volume_ml','unit','confidence'}:raise ValueError('PARSE_SCHEMA_FAIL')
    if p.get('action')!='LOG_FLUID' or type(p.get('volume_ml')) is not int or p['volume_ml']!=200 or p.get('unit')!='ml':raise ValueError('PARSE_SEMANTIC_FAIL')
    if type(p.get('confidence')) not in (int,float) or not 0.8<=p['confidence']<=1:raise ValueError('PARSE_CONFIDENCE_FAIL')
    return {'receipt_schema':'ai-missy-qvac-build06/1','receipt_status':'HOST_OBSERVED_QVAC_PASS','limitations':'Network isolation, hardware and genuine SDK provenance require continuous independent video; this validator only checks receipt shape and semantic content.','generated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'model':smoke['model'],'smoke_latency_ms':smoke.get('latency_ms'),'parse_latency_ms':parse.get('latency_ms')}

def main(argv):
    if len(argv)!=4:raise ValueError('USAGE: verify_offline_receipts.py SMOKE_JSONL PARSE_JSONL OUTPUT_JSON')
    smoke=read_one(argv[1]);parse=read_one(argv[2]);receipt=verify(smoke,parse)
    for name,path in [('smoke_sha256',argv[1]),('parse_sha256',argv[2])]:receipt[name]=hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()
    pathlib.Path(argv[3]).write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print('BUILD06_QVAC_SEMANTIC_GATE=PASS')
    print('HOST_OBSERVED_ONLY=true')
    return 0
if __name__=='__main__':
    try:sys.exit(main(sys.argv))
    except Exception as e:print('BUILD06_QVAC_SEMANTIC_GATE=FAIL '+str(e),file=sys.stderr);sys.exit(1)
