"""Build 20: fail-closed, redacted judge review bundle. Never publishes."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path

EXPECTED = {
    'qvac_receipt': '771EB2353788CCE68C357939AC000E9F46EFB24DD6A0143974059EF2972EDB04',
    'http_e2e_receipt': 'BF376766950DD34222E62466C9C72AAE3B7FDB86A4756D438BBA3D0CCB44360A',
}
EXPECTED_CHECKS = (
    'qvac_receipt_hash_matches', 'http_e2e_hash_matches',
    'qvac_semantics', 'real_http_e2e',
    'synthetic_fluid_confirmation', 'safety_checks',
)
NAMES = ('qvac-verified-', 'qvac-http-e2e-')
SUFFIX = re.compile(r'^202[0-9]{5}-[0-9]{6}\.json$')

def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest().upper()

def verify(manifest: dict, evidence_dir: Path, video: Path | None = None) -> dict:
    if manifest.get('schema') != 'ai-missy-build19-redacted-evidence/1':
        raise ValueError('BUILD19_SCHEMA_MISMATCH')
    names = manifest.get('source_receipt_filenames')
    if not isinstance(names, list) or len(names) != 2:
        raise ValueError('SOURCE_RECEIPT_NAMES_INVALID')
    for name, prefix in zip(names, NAMES):
        if not isinstance(name, str) or not name.startswith(prefix) or not SUFFIX.fullmatch(name[len(prefix):]):
            raise ValueError('SOURCE_RECEIPT_NAME_UNSAFE')
    if names[0][len(NAMES[0]):] != names[1][len(NAMES[1]):]:
        raise ValueError('RECEIPT_TIMESTAMP_MISMATCH')
    checks = manifest.get('checks')
    if not isinstance(checks, dict) or any(checks.get(k) is not True for k in EXPECTED_CHECKS):
        raise ValueError('BUILD19_CHECKS_NOT_ALL_PASS')
    if manifest.get('technical_receipt_integrity') != 'PASS':
        raise ValueError('BUILD19_NOT_PASS')
    hashes = manifest.get('sha256')
    if not isinstance(hashes, dict):
        raise ValueError('BUILD19_HASHES_MISSING')
    for key, name in zip(EXPECTED, names):
        if hashes.get(key) != EXPECTED[key]:
            raise ValueError('EXPECTED_HASH_MISMATCH_' + key.upper())
        path = evidence_dir / name
        if not path.is_file() or digest(path) != EXPECTED[key]:
            raise ValueError('ON_DISK_HASH_MISMATCH_' + key.upper())
    video_evidence = {'provided': False, 'independent_review': 'PENDING'}
    if video is not None:
        if not video.is_file():
            raise ValueError('VIDEO_FILE_NOT_FOUND')
        video_evidence = {'provided': True, 'sha256': digest(video),
                          'bytes': video.stat().st_size, 'independent_review': 'PENDING'}
    return {
        'schema': 'ai-missy-build20-submission-readiness/1',
        'generated_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
        'scope': 'SYNTHETIC_ONLY',
        'technical_evidence': 'PASS_HASHES_AND_SEMANTIC_RECEIPTS',
        'receipt_filenames': names,
        'sha256': EXPECTED,
        'video': video_evidence,
        'network_isolation_independent_review': 'PENDING',
        'qvac_sdk_license_review': 'PENDING',
        'model_license_review': 'PENDING',
        'dependency_license_review': 'PENDING',
        'dorahacks_rules_and_eligibility': 'PENDING',
        'prior_work_disclosure_review': 'PENDING',
        'privacy_review': 'PENDING',
        'public_release_authorization': 'NOT_GRANTED',
        'public_release': 'NO_GO',
        'submission': 'NOT_SUBMITTED',
        'readiness': 'NO_GO',
        'limitations': 'Host-reported evidence only; no independent video or network-isolation attestation.',
    }

def write_package(report: dict, output: Path, bundle: Path):
    output.parent.mkdir(parents=True, exist_ok=True)
    bundle.parent.mkdir(parents=True, exist_ok=True)
    payload = (json.dumps(report, indent=2, ensure_ascii=False) + '\n').encode('utf-8')
    output.write_bytes(payload)
    notes = (
        '# AI Missy Offline — Judge review (synthetic demo)\n\n'
        'Technical receipts: hashes and required fields match the user-provided baseline.\n'
        'This does NOT independently attest offline network isolation, model provenance or an uncut video.\n'
        'Video, license, organizer eligibility, prior-work, privacy and release authorization: PENDING.\n'
        'No patient data, model weights, raw logs, video or private repository contents are included.\n'
        'Do not publish or submit this bundle as a final cleared release.\n'
    )
    with zipfile.ZipFile(bundle, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('BUILD20_SUBMISSION_READINESS.json', payload)
        z.writestr('JUDGE_REVIEW_README.md', notes)

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', required=True, type=Path)
    parser.add_argument('--evidence-dir', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--bundle', required=True, type=Path)
    parser.add_argument('--video', type=Path)
    a = parser.parse_args()
    try:
        if a.manifest.stat().st_size > 1024 * 1024:
            raise ValueError('MANIFEST_TOO_LARGE')
        manifest = json.loads(a.manifest.read_text(encoding='utf-8-sig'))
        report = verify(manifest, a.evidence_dir, a.video)
        write_package(report, a.output, a.bundle)
        print('BUILD20_TECHNICAL_EVIDENCE=PASS')
        print('BUILD20_VIDEO_REVIEW=PENDING')
        print('BUILD20_SUBMISSION_READINESS=NO_GO')
        print('BUILD20_REPORT=' + str(a.output))
        print('BUILD20_BUNDLE=' + str(a.bundle))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print('BUILD20_TECHNICAL_EVIDENCE=FAIL ' + type(exc).__name__ + ': ' + str(exc))
        print('BUILD20_SUBMISSION_READINESS=NO_GO')
        return 1

if __name__ == '__main__':
    sys.exit(main())
)

def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest().upper()

def verify(manifest: dict, evidence_dir: Path, video: Path | None = None) -> dict:
    if manifest.get('schema') != 'ai-missy-build19-redacted-evidence/1':
        raise ValueError('BUILD19_SCHEMA_MISMATCH')
    names = manifest.get('source_receipt_filenames')
    if not isinstance(names, list) or len(names) != 2:
        raise ValueError('SOURCE_RECEIPT_NAMES_INVALID')
    for name, prefix in zip(names, NAMES):
        if not isinstance(name, str) or not name.startswith(prefix) or not SUFFIX.fullmatch(name[len(prefix):]):
            raise ValueError('SOURCE_RECEIPT_NAME_UNSAFE')
    if names[0][len(NAMES[0]):] != names[1][len(NAMES[1]):]:
        raise ValueError('RECEIPT_TIMESTAMP_MISMATCH')
    checks = manifest.get('checks')
    if not isinstance(checks, dict) or any(checks.get(k) is not True for k in EXPECTED_CHECKS):
        raise ValueError('BUILD19_CHECKS_NOT_ALL_PASS')
    if manifest.get('technical_receipt_integrity') != 'PASS':
        raise ValueError('BUILD19_NOT_PASS')
    hashes = manifest.get('sha256')
    if not isinstance(hashes, dict):
        raise ValueError('BUILD19_HASHES_MISSING')
    for key, name in zip(EXPECTED, names):
        if hashes.get(key) != EXPECTED[key]:
            raise ValueError('EXPECTED_HASH_MISMATCH_' + key.upper())
        path = evidence_dir / name
        if not path.is_file() or digest(path) != EXPECTED[key]:
            raise ValueError('ON_DISK_HASH_MISMATCH_' + key.upper())
    video_evidence = {'provided': False, 'independent_review': 'PENDING'}
    if video is not None:
        if not video.is_file():
            raise ValueError('VIDEO_FILE_NOT_FOUND')
        video_evidence = {'provided': True, 'sha256': digest(video),
                          'bytes': video.stat().st_size, 'independent_review': 'PENDING'}
    return {
        'schema': 'ai-missy-build20-submission-readiness/1',
        'generated_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
        'scope': 'SYNTHETIC_ONLY',
        'technical_evidence': 'PASS_HASHES_AND_SEMANTIC_RECEIPTS',
        'receipt_filenames': names,
        'sha256': EXPECTED,
        'video': video_evidence,
        'network_isolation_independent_review': 'PENDING',
        'qvac_sdk_license_review': 'PENDING',
        'model_license_review': 'PENDING',
        'dependency_license_review': 'PENDING',
        'dorahacks_rules_and_eligibility': 'PENDING',
        'prior_work_disclosure_review': 'PENDING',
        'privacy_review': 'PENDING',
        'public_release_authorization': 'NOT_GRANTED',
        'public_release': 'NO_GO',
        'submission': 'NOT_SUBMITTED',
        'readiness': 'NO_GO',
        'limitations': 'Host-reported evidence only; no independent video or network-isolation attestation.',
    }

def write_package(report: dict, output: Path, bundle: Path):
    output.parent.mkdir(parents=True, exist_ok=True)
    bundle.parent.mkdir(parents=True, exist_ok=True)
    payload = (json.dumps(report, indent=2, ensure_ascii=False) + '\n').encode('utf-8')
    output.write_bytes(payload)
    notes = (
        '# AI Missy Offline — Judge review (synthetic demo)\n\n'
        'Technical receipts: hashes and required fields match the user-provided baseline.\n'
        'This does NOT independently attest offline network isolation, model provenance or an uncut video.\n'
        'Video, license, organizer eligibility, prior-work, privacy and release authorization: PENDING.\n'
        'No patient data, model weights, raw logs, video or private repository contents are included.\n'
        'Do not publish or submit this bundle as a final cleared release.\n'
    )
    with zipfile.ZipFile(bundle, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('BUILD20_SUBMISSION_READINESS.json', payload)
        z.writestr('JUDGE_REVIEW_README.md', notes)

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', required=True, type=Path)
    parser.add_argument('--evidence-dir', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--bundle', required=True, type=Path)
    parser.add_argument('--video', type=Path)
    a = parser.parse_args()
    try:
        if a.manifest.stat().st_size > 1024 * 1024:
            raise ValueError('MANIFEST_TOO_LARGE')
        manifest = json.loads(a.manifest.read_text(encoding='utf-8-sig'))
        report = verify(manifest, a.evidence_dir, a.video)
        write_package(report, a.output, a.bundle)
        print('BUILD20_TECHNICAL_EVIDENCE=PASS')
        print('BUILD20_VIDEO_REVIEW=PENDING')
        print('BUILD20_SUBMISSION_READINESS=NO_GO')
        print('BUILD20_REPORT=' + str(a.output))
        print('BUILD20_BUNDLE=' + str(a.bundle))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print('BUILD20_TECHNICAL_EVIDENCE=FAIL ' + type(exc).__name__ + ': ' + str(exc))
        print('BUILD20_SUBMISSION_READINESS=NO_GO')
        return 1

if __name__ == '__main__':
    sys.exit(main())
