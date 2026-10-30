param([ValidateSet('Preflight','PrepareOnline','VerifyOffline','ShipAudit')][string]$Phase='Preflight')
$ErrorActionPreference='Stop'
$root=Split-Path -Parent $PSScriptRoot
Set-Location $root
function Check([string]$name) { if ($LASTEXITCODE -ne 0) { throw "$name FAILED (exit=$LASTEXITCODE)" } }
Write-Host "BUILD08_PHASE=$Phase"
switch ($Phase) {
 'Preflight' {
   & powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\windows-preflight.ps1
   Check 'HOST_PREFLIGHT'
   & py .\scripts\build08_release_audit.py
   Check 'CODE_AUDIT'
   Write-Host 'BUILD08_PREFLIGHT=PASS (NOT QVAC INFERENCE)'
 }
 'PrepareOnline' {
   & powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\windows-build08.ps1 -Phase Preflight
   Check 'PREFLIGHT'
   & npm install --ignore-scripts=false
   Check 'NPM_INSTALL'
   & npm run model:preload
   Check 'MODEL_PRELOAD'
   Write-Host 'BUILD08_PREPARE_ONLINE=PASS (NOT OFFLINE PROOF)'
 }
 'VerifyOffline' {
   & powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\windows-offline-gate.ps1
   Check 'OFFLINE_GATE'
   Write-Host 'BUILD08_OFFLINE_HOST_OBSERVED=PASS (REQUIRES VIDEO REVIEW)'
 }
 'ShipAudit' {
   & py .\scripts\build08_release_audit.py
   Check 'CODE_AUDIT'
   & py .\scripts\ship_audit.py
   Check 'SHIP_AUDIT'
   Write-Host 'BUILD08_SHIP_AUDIT=COMPLETE (SEE NO_GO DETAILS)'
 }
}
