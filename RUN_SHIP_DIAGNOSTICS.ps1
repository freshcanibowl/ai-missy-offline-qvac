# Read-only diagnostic entrypoint: no model downloads, network changes, GitHub writes or submission.
$ErrorActionPreference='Stop'
Set-Location $PSScriptRoot
if (-not (Get-Command py -ErrorAction SilentlyContinue)) { throw 'PYTHON_LAUNCHER_MISSING: install Python or use py.exe' }
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\triage_windows.ps1
if ($LASTEXITCODE -ne 0) { throw 'WINDOWS_TRIAGE_FAILED' }
& py .\scripts\ship_support.py
if ($LASTEXITCODE -ne 0) { throw 'SHIP_SUPPORT_FAILED' }
Write-Host 'SHARE_ONLY=local-evidence\AI_MISSY_SHIP_SUPPORT.zip'
Write-Host 'This bundle does NOT prove real QVAC offline inference.'
