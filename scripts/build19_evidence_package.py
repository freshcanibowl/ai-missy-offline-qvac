"""Build 19: local, redacted evidence manifest. Does not publish or attest network isolation."""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path

MODEL = 'LLAMA_3_2_1B_INST_Q4_0'
ENGINE = 'QVAC_LOCAL'

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest().upper()

def latest_pair(folder: Path):
    for qvac in sorted(folder.glob('qvac-verified-*.json'), reverse=True):
        stamp = qvac.name.removeprefix('qvac-verified-').removesuffix('.json')
        e2e = folder / ('qvac-http-e2e-' + stamp + '.json')
        if e2e.is_file():
            return qvac, e2e
    raise ValueError('NO_MATCHING_QVAC_E2E_RECEIPTS')

def build(folder: Path, expected_qvac: str, expected_e2e: str, video: Path | None = None):
    qvac_file, e2e_file = latest_pair(folder)
    hashes = {'qvac_receipt': sha256(qvac_file), 'http_e2e_receipt': sha256(e2e_file)}
    q = json.loads(qvac_file.read_text(encoding='utf-8-sig'))
    e = json.loads(e2e_file.read_text(encoding='utf-8-sig'))
    checks = {
        'qvac_receipt_hash_matches': hashes['qvac_receipt'] == expected_qvac.upper(),
        'http_e2e_hash_matches': hashes['http_e2e_receipt'] == expected_e2e.upper(),
        'qvac_semantics': q.get('receipt_status') == 'HOST_OBSERVED_QVAC_PASS' and q.get('model') == MODEL,
        'real_http_e2e': e.get('result') == 'HOST_OBSERVED_E2E_PASS' and e.get('engine') == ENGINE and e.get('model') == MODEL,
        'synthetic_fluid_confirmation': e.get('synthetic') is True and e.get('initial_recorded_ml') == 700 and e.get('confirmed_recorded_ml') == 900 and e.get('confirmation_persisted') is True,
        'safety_checks': e.get('replay_rejected') is True and e.get('food_abstention') is True,
    }
    video_record = {'provided': False, 'independent_review': 'PENDING'}
    if video is not None:
        if not video.is_file():
            raise ValueError('VIDEO_FILE_NOT_FOUND')
        video_record = {'provided': True, 'sha256': sha256(video), 'bytes': video.stat().st_size,
                        'independent_review': 'PENDING'}
    status = 'PASS' if all(checks.values()) else 'FAIL'
    return {
        'schema': 'ai-missy-build19-redacted-evidence/1',
        'generated_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
        'scope': 'SYNTHETIC_DEMO_ONLY',
        'source_receipt_filenames': [qvac_file.name, e2e_file.name],
        'sha256': hashes,
        'checks': checks,
        'technical_receipt_integrity': status,
        'offline_host_gate': 'HOST_REPORTED_PASS_NOT_INDEPENDENTLY_ATTESTED' if status == 'PASS' else 'UNVERIFIED',
        'video': video_record,
        'third_party_licenses': 'PENDING_REVIEW',
        'organizer_eligibility': 'PENDING_REVIEW',
        'public_release': 'NO_GO',
        'dorahacks_submission': 'NOT_SUBMITTED',
        'privacy': 'Redacted metadata only; raw logs, health data, paths and video bytes excluded.',
    }

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--evidence-dir', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--expected-qvac-sha256', required=True)
    p.add_argument('--expected-e2e-sha256', required=True)
    p.add_argument('--video', type=Path)
    args = p.parse_args()
    try:
        report = build(args.evidence_dir, args.expected_qvac_sha256, args.expected_e2e_sha256, args.video)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
        print('BUILD19_TECHNICAL_RECEIPTS=' + report['technical_receipt_integrity'])
        print('BUILD19_PUBLIC_RELEASE=NO_GO')
        print('BUILD19_VIDEO_REVIEW=' + report['video']['independent_review'])
        print('BUILD19_REPORT=' + str(args.output))
        return 0 if report['technical_receipt_integrity'] == 'PASS' else 1
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print('BUILD19_TECHNICAL_RECEIPTS=FAIL ' + type(exc).__name__ + ': ' + str(exc))
        print('BUILD19_PUBLIC_RELEASE=NO_GO')
        return 1

if __name__ == '__main__':
    raise SystemExit(main())
