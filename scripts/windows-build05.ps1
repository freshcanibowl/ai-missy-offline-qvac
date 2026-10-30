param([ValidateSet('Preflight','PrepareOnline','VerifyOffline','ShipAudit')][string]$Phase='Preflight')
$ErrorActionPreference='Stop'
$root=Split-Path -Parent $PSScriptRoot
Set-Location $root
function CheckExit([string]$Label){ if($LASTEXITCODE -ne 0){throw "$Label FAILED exit=$LASTEXITCODE"} }
Write-Host "BUILD05_PHASE=$Phase"
if($Phase -eq 'Preflight' -or $Phase -eq 'PrepareOnline'){
  & powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\windows-preflight.ps1
  CheckExit 'PREFLIGHT'
  & py -m unittest discover -s tests -v
  CheckExit 'PYTHON_TESTS'
  if($Phase -eq 'PrepareOnline'){
    Write-Host 'ONLINE PREPARATION: installing dependencies and downloading model.'
    & npm install
    CheckExit 'NPM_INSTALL'
    & npm run model:preload
    CheckExit 'QVAC_PRELOAD'
    Write-Host 'BUILD05_PREPARE_ONLINE=PASS; disconnect networks before VerifyOffline.'
  }
}elseif($Phase -eq 'VerifyOffline'){
  & powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\windows-offline-gate.ps1
  CheckExit 'OFFLINE_GATE'
}elseif($Phase -eq 'ShipAudit'){
  & py .\scripts\ship_audit.py
  CheckExit 'SHIP_AUDIT'
}
