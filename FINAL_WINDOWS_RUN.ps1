# Final Windows handoff. Does not alter networking, publish, or submit automatically.
param([ValidateSet('Diagnose','PrepareOnline','VerifyOffline','Audit','Demo','PublishDryRun')][string]$Stage='Diagnose')
$ErrorActionPreference='Stop'
Set-Location $PSScriptRoot
Write-Host "AI_MISSY_FINAL_STAGE=$Stage"
function Invoke-Step([string]$Name,[string]$Script,[string[]]$StepArgs=@()) {
  if (-not (Test-Path $Script)) { throw "MISSING_SCRIPT=$Script" }
  Write-Host "START=$Name"
  & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $Script @StepArgs
  if ($LASTEXITCODE -ne 0) { throw "FAILED=$Name EXIT=$LASTEXITCODE" }
  Write-Host "PASS=$Name"
}
switch ($Stage) {
  'Diagnose' {
    Invoke-Step 'DIAGNOSTICS' '.\RUN_SHIP_DIAGNOSTICS.ps1'
    Write-Host 'This does not test real offline QVAC inference.'
  }
  'PrepareOnline' {
    Invoke-Step 'PREFLIGHT' '.\START_HERE_WINDOWS.ps1' @('-Phase','Preflight')
    Invoke-Step 'PRELOAD' '.\START_HERE_WINDOWS.ps1' @('-Phase','PrepareOnline')
    Write-Host 'ONLINE_PREPARED=HOST_OBSERVED; NOT OFFLINE PROOF'
    Write-Host 'Next: disconnect all networks and record continuous video. Then run -Stage VerifyOffline.'
  }
  'VerifyOffline' {
    Invoke-Step 'REAL_OFFLINE_GATE' '.\START_HERE_WINDOWS.ps1' @('-Phase','VerifyOffline')
    Invoke-Step 'EVIDENCE_AUDIT' '.\START_HERE_WINDOWS.ps1' @('-Phase','ShipAudit')
    Write-Host 'HOST_OBSERVED_ONLY: check audit and uncut video before claiming offline proof.'
  }
  'Audit' {
    Invoke-Step 'RELEASE_AUDIT' '.\START_HERE_WINDOWS.ps1' @('-Phase','ShipAudit')
    & py .\scripts\final_release_audit.py
    if ($LASTEXITCODE -ne 0) { throw 'FINAL_RELEASE_AUDIT_FAILED' }
  }
  'Demo' {
    if (-not (Get-Command py -ErrorAction SilentlyContinue)) { throw 'PYTHON_NOT_FOUND' }
    Write-Host 'Opening localhost-only demo at http://127.0.0.1:8766'
    & py .\server.py
    if ($LASTEXITCODE -ne 0) { throw 'LOCAL_DEMO_FAILED' }
  }
  'PublishDryRun' {
    Invoke-Step 'GITHUB_DRY_RUN' '.\scripts\publish-new-repo.ps1'
    Write-Host 'No GitHub repository was created.'
  }
}
Write-Host "AI_MISSY_FINAL_STAGE_COMPLETED=$Stage"
