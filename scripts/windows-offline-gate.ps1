$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
$evidence = Join-Path $root 'local-evidence'
New-Item -ItemType Directory -Force -Path $evidence | Out-Null
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$transcript = Join-Path $evidence "offline-$stamp.txt"
$smoke = Join-Path $evidence "qvac-smoke-$stamp.jsonl"
$parse = Join-Path $evidence "qvac-parse-$stamp.jsonl"
$receipt = Join-Path $evidence "qvac-verified-$stamp.json"
$e2e = Join-Path $evidence "qvac-http-e2e-$stamp.json"
Start-Transcript -Path $transcript -ErrorAction Stop | Out-Null
$passed = $false
try {
  Write-Host 'AI MISSY BUILD 07 - WINDOWS REAL OFFLINE GATE'
  Write-Host 'Disconnect ALL Wi-Fi, Ethernet, VPN, tethering and cellular interfaces. Record continuous video.'
  $answer = Read-Host 'Type OFFLINE after physically disconnecting all internet connections'
  if ($answer -cne 'OFFLINE') { throw 'USER_DID_NOT_CONFIRM_DISCONNECTION' }
  $adapters = @(Get-NetAdapter -ErrorAction Stop | Select-Object Name,Status,InterfaceDescription)
  $adapters | Format-Table -AutoSize
  $active = @($adapters | Where-Object {$_.Status -eq 'Up'})
  if ($active.Count -gt 0) { throw 'NETWORK_ADAPTER_STILL_UP (disable adapters before offline gate)' }
  Write-Host 'NETWORK_ADAPTER_GATE=PASS (host-observed; not independently attested)'
  $os = Get-CimInstance Win32_OperatingSystem
  $cs = Get-CimInstance Win32_ComputerSystem
  $gpu = @(Get-CimInstance Win32_VideoController | Select-Object Name,DriverVersion)
  $manifest = [ordered]@{
    generated_local = (Get-Date).ToString('o')
    scope = 'SYNTHETIC_ONLY'
    network_status = 'All adapters reported down; continuous screen recording required'
    os = $os.Caption
    os_version = $os.Version
    ram_bytes = [long]$cs.TotalPhysicalMemory
    gpu = $gpu
    node = (& node --version)
    npm = (& npm --version)
    python = (& py --version)
    model = 'LLAMA_3_2_1B_INST_Q4_0'
    sdk = '@qvac/sdk@0.22.0'
    source_hashes = @(Get-FileHash -Algorithm SHA256 .\scripts\offline-smoke.mjs,.\scripts\qvac-parse.mjs,.\core.py,.\server.py | Select-Object Path,Hash)
  }
  $manifest | ConvertTo-Json -Depth 8 | Set-Content -Encoding UTF8 (Join-Path $evidence "hardware-$stamp.json")
  Write-Host '=== QVAC COLD LOAD + GENERATION ==='
  & node .\scripts\offline-smoke.mjs 2>&1 | Tee-Object -FilePath $smoke
  if ($LASTEXITCODE -ne 0) { throw 'QVAC_SMOKE_FAILED' }
  Write-Host '=== QVAC INTENT EXTRACTION (stdin avoids PowerShell quoting) ==='
  '{"text":"Log 200 ml water"}' | & node .\scripts\qvac-parse.mjs --stdin 2>&1 | Tee-Object -FilePath $parse
  if ($LASTEXITCODE -ne 0) { throw 'QVAC_PARSE_FAILED' }
  Write-Host '=== VERIFY QVAC OUTPUTS ==='
  & py .\scripts\verify_offline_receipts.py $smoke $parse $receipt
  if ($LASTEXITCODE -ne 0) { throw 'QVAC_SEMANTIC_VERIFICATION_FAILED' }
  Write-Host '=== REAL HTTP -> QVAC SDK -> SQLITE E2E (NO MOCK) ==='
  & py .\scripts\live_http_e2e.py --output $e2e
  if ($LASTEXITCODE -ne 0) { throw 'REAL_HTTP_QVAC_E2E_FAILED' }
  Write-Host 'BUILD07_REAL_HTTP_E2E=HOST_OBSERVED_PASS'
  Write-Host '=== CORE + MOCKED HTTP REGRESSION TESTS ==='
  & py -m unittest discover -s tests -v
  if ($LASTEXITCODE -ne 0) { throw 'PYTHON_TEST_GATE_FAILED' }
  Write-Host 'BUILD07_LOCAL_OFFLINE_GATE=HOST_OBSERVED_PASS'
  Write-Host "VERIFIED_RECEIPT=$receipt"
  Write-Host "REAL_HTTP_E2E_RECEIPT=$e2e"
  Write-Host 'LIMITATION: host-observed result only; independent proof requires continuous offline video.'
  $passed = $true
} catch {
  Write-Host "BUILD07_LOCAL_OFFLINE_GATE=FAIL $($_.Exception.Message)" -ForegroundColor Red
  throw
} finally {
  Stop-Transcript | Out-Null
  Write-Host "EVIDENCE_TRANSCRIPT=$transcript"
  if (-not $passed) { Write-Host 'SHIP_GATE=NO_GO' -ForegroundColor Red }
}
