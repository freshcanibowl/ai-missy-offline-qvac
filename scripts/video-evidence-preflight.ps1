# AI Missy video evidence preflight. Windows PowerShell 5.1 compatible.
# No recording, network toggling, model inference, uploads, or clinical data collection.
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
$folder = Join-Path $root 'local-evidence\video'
New-Item -ItemType Directory -Force -Path $folder | Out-Null
$gateLog = Join-Path $folder 'build23_gate_console.log'
$gateReceipt = Join-Path $root 'local-evidence\BUILD23_HOST_RECEIPT.json'
$commit = (& git rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0) { throw 'GIT_REV_PARSE_FAILED' }

# Execute the real code gate and preserve output, but never fabricate a PASS.
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $root 'scripts\build23-host-gate.ps1') *> $gateLog
$gateExit = $LASTEXITCODE
$gateStatus = 'UNKNOWN'
$pythonStatus = 'UNKNOWN'
$jsStatus = 'UNKNOWN'
if (Test-Path $gateReceipt) {
    try {
        $receipt = Get-Content $gateReceipt -Raw -Encoding UTF8 | ConvertFrom-Json
        if ($receipt.gate_revision -eq '23.1' -and $receipt.stage -eq 'HOST_CODE_GATE') {
            $gateStatus = [string]$receipt.status
            $pythonStatus = [string]$receipt.python_tests
            $jsStatus = [string]$receipt.js_syntax
        }
    } catch {
        $gateStatus = 'INVALID_RECEIPT'
    }
}
if ($gateExit -ne 0) { $gateStatus = 'FAIL' }
if ($gateStatus -eq 'PASS' -and $gateExit -ne 0) { $gateStatus = 'FAIL' }

$manifest = [ordered]@{
    project = 'AI Missy Offline'
    stage = 'VIDEO_EVIDENCE_PREFLIGHT'
    synthetic_only = $true
    recorded_utc = [DateTime]::UtcNow.ToString('o')
    git_commit = $commit
    code_gate = $gateStatus
    python_tests = $pythonStatus
    js_syntax = $jsStatus
    gate_process_exit = $gateExit
    offline_qvac_retest = 'NOT_RUN'
    confirm_and_persist_retest = 'NOT_RUN'
    timeline_ui_retest = 'NOT_RUN'
    export_ui_retest = 'NOT_RUN'
    wifi_disconnected_observed = 'NOT_RUN'
    video_recorded = 'NOT_RUN'
    medical_or_clinical_validation = 'NOT_CLAIMED'
    source_capture = 'Manual Windows screen recording only'
    notes = 'Do not claim verified functionality without separate screen and log evidence.'
}
$manifestPath = Join-Path $folder 'VIDEO_EVIDENCE_MANIFEST.json'
$manifest | ConvertTo-Json -Depth 6 | Set-Content -Path $manifestPath -Encoding UTF8

$csvPath = Join-Path $folder 'SHOT_EVIDENCE_LOG.csv'
if (-not (Test-Path $csvPath)) {
    @(
        [pscustomobject]@{shot='S01';topic='Problem and intro';status='NOT_RECORDED';evidence_file='';notes='Conceptual intro'}
        [pscustomobject]@{shot='S02';topic='Local server and UI';status='NOT_RECORDED';evidence_file='';notes='Actual localhost screen'}
        [pscustomobject]@{shot='S03';topic='Disconnect Wi-Fi and local inference';status='NOT_RECORDED';evidence_file='';notes='Continuous real recording'}
        [pscustomobject]@{shot='S04';topic='AI proposes human confirms';status='NOT_RECORDED';evidence_file='';notes='Show real model output'}
        [pscustomobject]@{shot='S05';topic='SQLite persistence';status='NOT_RECORDED';evidence_file='';notes='Synthetic records only'}
        [pscustomobject]@{shot='S06';topic='Safety boundaries';status='NOT_RECORDED';evidence_file='';notes='Actual rejection response'}
        [pscustomobject]@{shot='S07';topic='Timeline and export';status='NOT_RECORDED';evidence_file='';notes='Under validation until verified'}
        [pscustomobject]@{shot='S08';topic='PAIR ACE roadmap';status='NOT_RECORDED';evidence_file='';notes='Future roadmap label'}
        [pscustomobject]@{shot='S09';topic='Closing';status='NOT_RECORDED';evidence_file='';notes='Brand ending'}
    ) | Export-Csv -Path $csvPath -NoTypeInformation -Encoding UTF8
}
Write-Host "VIDEO_PREFLIGHT_CODE_GATE=$gateStatus"
Write-Host "VIDEO_EVIDENCE_MANIFEST=$manifestPath"
Write-Host "VIDEO_SHOT_LOG=$csvPath"
Write-Host "IMPORTANT: Offline and UI evidence are NOT_RUN until manually recorded."
if ($gateStatus -ne 'PASS') { exit 1 }
