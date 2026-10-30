# Build 23: isolated host code gate. No network, model inference, or production changes.
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
$evidence = Join-Path $root 'local-evidence'
New-Item -ItemType Directory -Force -Path $evidence | Out-Null

$tests = 'NOT_RUN'
$nodeSyntax = 'NOT_RUN'
$errors = @()
$testLog = Join-Path $evidence 'BUILD23_UNIT_TESTS.log'
$nodeLog = Join-Path $evidence 'BUILD23_JS_SYNTAX.log'

try {
    & py -m unittest discover -s tests -v *>&1 |
        Out-File -FilePath $testLog -Encoding utf8
    if ($LASTEXITCODE -ne 0) { throw "PYTHON_TESTS_EXIT_$LASTEXITCODE" }
    $tests = 'PASS'
} catch {
    $tests = 'FAIL'
    $errors += $_.Exception.Message
}
try {
    & node --check .\web\app.js *>&1 |
        Out-File -FilePath $nodeLog -Encoding utf8
    if ($LASTEXITCODE -ne 0) { throw "NODE_SYNTAX_EXIT_$LASTEXITCODE" }
    $nodeSyntax = 'PASS'
} catch {
    $nodeSyntax = 'FAIL'
    $errors += $_.Exception.Message
}

$status = if ($tests -eq 'PASS' -and $nodeSyntax -eq 'PASS') { 'PASS' } else { 'FAIL' }
$receipt = [ordered]@{
    build = 23
    stage = 'HOST_CODE_GATE'
    status = $status
    python_tests = $tests
    js_syntax = $nodeSyntax
    qvac_offline_e2e = 'NOT_RUN'
    timeline_ui = 'NOT_RUN'
    timestamp_utc = [DateTime]::UtcNow.ToString('o')
    errors = $errors
    note = 'Synthetic-only, code checks. No production or clinical validation.'
}
$path = Join-Path $evidence 'BUILD23_HOST_RECEIPT.json'
$receipt | ConvertTo-Json -Depth 5 |
    Set-Content -Path $path -Encoding UTF8
Write-Host "BUILD23_CODE_GATE=$status"
Write-Host "BUILD23_RECEIPT=$path"
if ($status -ne 'PASS') { exit 1 }
