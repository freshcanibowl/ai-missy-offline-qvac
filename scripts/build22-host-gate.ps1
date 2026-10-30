# Build22 host verification: deterministic tests + JS syntax, no deployment.
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
$evidence = Join-Path $root 'local-evidence'
New-Item -ItemType Directory -Force -Path $evidence | Out-Null

$testLog = Join-Path $evidence 'BUILD22_UNIT_TESTS.log'
$nodeLog = Join-Path $evidence 'BUILD22_NODE_CHECK.log'
$tests = 'NOT_RUN'
$js = 'NOT_RUN'

try {
    & py -m unittest discover -s tests -v *>&1 | Out-File -FilePath $testLog -Encoding utf8
    if ($LASTEXITCODE -ne 0) { throw "UNIT_TESTS_FAILED exit=$LASTEXITCODE" }
    $tests = 'PASS'

    & node --check (Join-Path $root 'web\app.js') *>&1 | Out-File -FilePath $nodeLog -Encoding utf8
    if ($LASTEXITCODE -ne 0) { throw "NODE_SYNTAX_FAILED exit=$LASTEXITCODE" }
    $js = 'PASS'

    $status = 'PASS'
} catch {
    $status = 'FAIL'
    Write-Warning $_.Exception.Message
}
$receipt = [ordered]@{
    build = 22
    stage = 'HOST_CODE_GATE'
    status = $status
    unit_tests = $tests
    node_syntax = $js
    qvac_offline_e2e = 'NOT_RUN'
    synthetic_ui_export = 'NOT_RUN'
    timestamp_utc = [DateTime]::UtcNow.ToString('o')
    note = 'No production deployment; code gate only.'
}
$path = Join-Path $evidence 'BUILD22_HOST_RECEIPT.json'
$receipt | ConvertTo-Json -Depth 4 | Set-Content -Path $path -Encoding UTF8
Write-Host "BUILD22_CODE_GATE=$status"
Write-Host "BUILD22_RECEIPT=$path"
if ($status -ne 'PASS') { exit 1 }
