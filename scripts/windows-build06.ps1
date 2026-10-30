param(
  [ValidateSet('Preflight','PrepareOnline','VerifyOffline','ShipAudit')]
  [string]$Phase='Preflight'
)
$ErrorActionPreference='Stop'
$root=Split-Path -Parent $PSScriptRoot
Set-Location $root
function AssertExit([string]$label) {
  if ($LASTEXITCODE -ne 0) { throw "$label failed (exit $LASTEXITCODE)" }
}
Write-Host "BUILD06_PHASE=$Phase"
switch ($Phase) {
  'Preflight' {
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\windows-preflight.ps1
    AssertExit 'PREFLIGHT'
    & py -m unittest discover -s tests -v
    AssertExit 'UNIT_AND_HTTP_TESTS'
    & py .\scripts\build06_release_audit.py
    AssertExit 'RELEASE_AUDIT'
    Write-Host 'BUILD06_PREFLIGHT=PASS (NOT QVAC offline proof)'
  }
  'PrepareOnline' {
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\windows-build06.ps1 -Phase Preflight
    AssertExit 'PREFLIGHT'
    & npm install
    AssertExit 'NPM_INSTALL'
    & npm run model:preload
    AssertExit 'MODEL_PRELOAD'
    Write-Host 'BUILD06_PREPARE_ONLINE=PASS (disconnect all networks for the next phase)'
  }
  'VerifyOffline' {
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\windows-offline-gate.ps1
    AssertExit 'REAL_OFFLINE_GATE'
    Write-Host 'BUILD06_OFFLINE_HOST_OBSERVED=PASS (continuous video still required)'
  }
  'ShipAudit' {
    & py .\scripts\build06_release_audit.py
    AssertExit 'RELEASE_AUDIT'
    & py .\scripts\ship_audit.py
    AssertExit 'SHIP_AUDIT'
    Write-Host 'BUILD06_SHIP_AUDIT=COMPLETE (check NO_GO/PENDING statuses)'
  }
}
