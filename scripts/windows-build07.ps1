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
Write-Host "BUILD07_PHASE=$Phase"
switch ($Phase) {
  'Preflight' {
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\windows-preflight.ps1
    AssertExit 'PREFLIGHT'
    & py -W error::ResourceWarning -m unittest discover -s tests -q
    AssertExit 'TESTS'
    & py .\scripts\build07_release_audit.py
    AssertExit 'RELEASE_AUDIT'
    Write-Host 'BUILD07_PREFLIGHT=PASS (NOT REAL QVAC PROOF)'
  }
  'PrepareOnline' {
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\windows-build07.ps1 -Phase Preflight
    AssertExit 'PREFLIGHT'
    & npm install
    AssertExit 'NPM_INSTALL'
    & npm run model:preload
    AssertExit 'MODEL_PRELOAD'
    Write-Host 'BUILD07_PREPARE_ONLINE=PASS (NOT YET OFFLINE)'
  }
  'VerifyOffline' {
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\windows-offline-gate.ps1
    AssertExit 'REAL_OFFLINE_GATE'
    Write-Host 'BUILD07_OFFLINE_HOST_OBSERVED=PASS (VIDEO REVIEW STILL REQUIRED)'
  }
  'ShipAudit' {
    & py .\scripts\build07_release_audit.py
    AssertExit 'RELEASE_AUDIT'
    & py .\scripts\ship_audit.py
    AssertExit 'SHIP_AUDIT'
    Write-Host 'BUILD07_SHIP_AUDIT=COMPLETE (CHECK NO_GO STATUS)'
  }
}
