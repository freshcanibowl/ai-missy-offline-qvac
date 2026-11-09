"""Build15 fail-closed assessor for Build14 synthetic host receipts. No clinical release."""
EXPECTED_HTTP=('legacy_status_200','legacy_session_200','plan_denies_activation','unauthorized_write_blocked','authorized_synthetic_write','pair_not_sent','synthetic_readback','real_marked_data_blocked')
def assess(receipt):
    reasons=[]
    if receipt.get('schema')!='missy.build14.host-gate.v1':reasons.append('RECEIPT_SCHEMA_INVALID')
    if receipt.get('status')!='LOCAL_SYNTHETIC_INTEGRATION_PASS':reasons.append('HOST_ACCEPTANCE_NOT_PASS')
    for key in ('legacy_before','legacy_after'):
        if not isinstance(receipt.get(key),dict) or receipt[key].get('exit_code')!=0:reasons.append(key.upper()+'_NOT_PASS')
    g=receipt.get('gates',{})
    if not isinstance(g,dict) or g.get('legacy_python_regression') is not True or g.get('synthetic_http') is not True:reasons.append('GATES_NOT_PASS')
    h=receipt.get('http_tests',{})
    if not isinstance(h,dict) or any(h.get(k) is not True for k in EXPECTED_HTTP):reasons.append('HTTP_INVARIANT_NOT_PASS')
    p=receipt.get('patch_apply',{})
    if not isinstance(p,dict) or p.get('exit_code')!=0 or 'STATUS=PATCH_APPLIED' not in p.get('stdout_tail',''):reasons.append('PATCH_NOT_PROVEN')
    if not receipt.get('server_original_sha256') or not receipt.get('server_patched_sha256'):reasons.append('FINGERPRINT_MISSING')
    return {'schema':'missy.build15.release-decision.v1','host_synthetic_evidence':'PASS' if not reasons else 'FAIL','host_evidence_reasons':reasons,'windows_qvac_offline':'PENDING','real_patient_authorization':'NOT_IMPLEMENTED','pair_handoff':'NOT_ENABLED','clinical_and_production_release':'NO_GO'}
