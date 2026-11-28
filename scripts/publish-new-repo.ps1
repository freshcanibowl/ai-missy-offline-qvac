# AI Missy safe publication preflight (Build 18).
# Intentionally read-only: no public repository creation, no git push.
# A separate, explicitly authorized release workflow is required to publish.
[CmdletBinding()]
param(
    [switch]$CheckOnly
)
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$required = @(
    'START_HERE_WINDOWS.ps1',
    'SHIP_README.md',
    'scripts/submission_preflight.py'
)
$missing = @($required | Where-Object {
    -not (Test-Path -LiteralPath (Join-Path $root $_) -PathType Leaf)
})
if ($missing.Count -gt 0) {
    Write-Error ("PUBLISH_PREFLIGHT=FAIL; MISSING=" + ($missing -join ','))
    exit 1
}
Write-Output 'PUBLISH_PREFLIGHT=PASS'
Write-Output 'PUBLICATION=NOT_PERFORMED'
Write-Output 'PATIENT_DATA=NOT_AUTHORIZED'
Write-Output 'HOST_QVAC_OFFLINE=PENDING_UNLESS_INDEPENDENTLY_VERIFIED'
if (-not $CheckOnly) {
    Write-Output 'PUBLISH_STATUS=NO_GO; explicit approval and a separate audited release process required'
}
exit 0
