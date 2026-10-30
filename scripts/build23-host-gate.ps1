# Build 23.1: Windows PowerShell 5.1-safe host gate.
# Python unittest -v writes normal progress to STDERR. Do not treat it as failure.
# Capture native STDOUT and STDERR separately; decide solely from process exit code.
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
$evidence = Join-Path $root 'local-evidence'
New-Item -ItemType Directory -Force -Path $evidence | Out-Null

$tests = 'NOT_RUN'
$nodeSyntax = 'NOT_RUN'
$testExit = $null
$nodeExit = $null
$errors = @()
$testStdout = Join-Path $evidence 'BUILD23_UNIT_TESTS.stdout.log'
$testStderr = Join-Path $evidence 'BUILD23_UNIT_TESTS.stderr.log'
$nodeStdout = Join-Path $evidence 'BUILD23_JS_SYNTAX.stdout.log'
$nodeStderr = Join-Path $evidence 'BUILD23_JS_SYNTAX.stderr.log'

try {
    $python = (Get-Command py -CommandType Application -ErrorAction Stop).Source
    $proc = Start-Process -FilePath $python -ArgumentList @('-m','unittest','discover','-s','tests','-v') -WorkingDirectory $root -NoNewWindow -Wait -PassThru -RedirectStandardOutput $testStdout -RedirectStandardError $testStderr
    $testExit = $proc.ExitCode
    if ($testExit -ne 0) { throw "PYTHON_TESTS_EXIT_$testExit" }
    $tests = 'PASS'
} catch {
    $tests = 'FAIL'
    $errors += $_.Exception.Message
}

try {
    $node = (Get-Command node -CommandType Application -ErrorAction Stop).Source
    $proc = Start-Process -FilePath $node -ArgumentList @('--check','web/app.js') -WorkingDirectory $root -NoNewWindow -Wait -PassThru -RedirectStandardOutput $nodeStdout -RedirectStandardError $nodeStderr
    $nodeExit = $proc.ExitCode
    if ($nodeExit -ne 0) { throw "NODE_SYNTAX_EXIT_$nodeExit" }
    $nodeSyntax = 'PASS'
} catch {
    $nodeSyntax = 'FAIL'
    $errors += $_.Exception.Message
}

$status = if ($tests -eq 'PASS' -and $nodeSyntax -eq 'PASS') { 'PASS' } else { 'FAIL' }
$receipt = [ordered]@{
    build = 23
    gate_revision = '23.1'
    stage = 'HOST_CODE_GATE'
    status = $status
    python_tests = $tests
    python_exit_code = $testExit
    js_syntax = $nodeSyntax
    node_exit_code = $nodeExit
    qvac_offline_e2e = 'NOT_RUN'
    timeline_ui = 'NOT_RUN'
    timestamp_utc = [DateTime]::UtcNow.ToString('o')
    errors = $errors
    log_paths = @{
        python_stdout = $testStdout
        python_stderr = $testStderr
        node_stdout = $nodeStdout
        node_stderr = $nodeStderr
    }
    note = 'Only process exit codes determine PASS/FAIL. Synthetic-only code gate.'
}
$path = Join-Path $evidence 'BUILD23_HOST_RECEIPT.json'
$receipt | ConvertTo-Json -Depth 6 | Set-Content -Path $path -Encoding UTF8
Write-Host "BUILD23_PYTHON_EXIT=$testExit"
Write-Host "BUILD23_NODE_EXIT=$nodeExit"
Write-Host "BUILD23_CODE_GATE=$status"
Write-Host "BUILD23_RECEIPT=$path"
if ($status -ne 'PASS') {
    if (Test-Path $testStderr) {
        Write-Host '=== PYTHON STDERR TAIL ==='
        Get-Content $testStderr -Tail 35
    }
    exit 1
}
