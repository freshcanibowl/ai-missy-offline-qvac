# AI Missy Ship Candidate: no automatic network disabling, publishing or submission.
param([ValidateSet('Preflight','PrepareOnline','VerifyOffline','ShipAudit')][string]$Phase='Preflight')
$ErrorActionPreference='Stop'
Set-Location $PSScriptRoot
Write-Host "AI_MISSY_SHIP_PHASE=$Phase"
if (-not (Test-Path '.\scripts\windows-build08.ps1')) { throw 'MISSING_BUILD08_ENTRYPOINT' }
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File '.\scripts\windows-build08.ps1' -Phase $Phase
if ($LASTEXITCODE -ne 0) { throw "AI_MISSY_SHIP_PHASE_FAILED=$Phase EXIT=$LASTEXITCODE" }
Write-Host "AI_MISSY_SHIP_PHASE_COMPLETED=$Phase"
