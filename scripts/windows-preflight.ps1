$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
Write-Host '=== AI MISSY BUILD07 WINDOWS PREFLIGHT ==='
Write-Host "ROOT=$root"
if (-not [Environment]::Is64BitOperatingSystem) { throw 'QVAC_REQUIRES_WINDOWS_X64' }
$nodeCommand = Get-Command node -ErrorAction SilentlyContinue
if (-not $nodeCommand) { throw 'NODE_NOT_INSTALLED: Install Node 22.21+ or 24.9+ first.' }
$nodeVersionText = (& node --version).Trim()
if ($LASTEXITCODE -ne 0) { throw 'NODE_VERSION_FAILED' }
try { $nodeVersion = [version]($nodeVersionText.TrimStart('v').Split('-')[0]) }
catch { throw "NODE_VERSION_UNPARSABLE=$nodeVersionText" }
$nodeOk = (($nodeVersion.Major -eq 22 -and $nodeVersion -ge [version]'22.21.0') -or ($nodeVersion.Major -ge 24 -and $nodeVersion -ge [version]'24.9.0'))
if (-not $nodeOk) { throw "NODE_UNSUPPORTED=$nodeVersionText (requires ^22.21.0 or >=24.9.0)" }
Write-Host "BUILD07_NODE_GATE=PASS ($nodeVersionText)"
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) { throw 'NPM_NOT_INSTALLED' }
if (-not (Get-Command py -ErrorAction SilentlyContinue)) { throw 'PYTHON_LAUNCHER_NOT_INSTALLED' }
Write-Host "NPM=$(& npm --version)"
Write-Host "PYTHON=$(& py --version)"
$os = Get-CimInstance Win32_OperatingSystem
$ram = [long](Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory
if ($ram -lt 2GB) { throw "RAM_INSUFFICIENT=$ram" }
Write-Host "OS=$($os.Caption) VERSION=$($os.Version)"
Write-Host "RAM_BYTES=$ram"
Get-CimInstance Win32_VideoController | Select-Object Name,DriverVersion | Format-Table -AutoSize
Write-Host '=== VULKAN CHECK ==='
if (Get-Command vulkaninfo -ErrorAction SilentlyContinue) {
  & vulkaninfo --summary
  if ($LASTEXITCODE -ne 0) { throw 'VULKANINFO_FAILED: check Vulkan driver/runtime.' }
  Write-Host 'BUILD07_VULKAN_DIAGNOSTIC=RAN; inspect the output for Vulkan >= 1.4.'
} else {
  Write-Host 'BUILD07_VULKAN_DIAGNOSTIC=UNVERIFIED: vulkaninfo is absent; QVAC requires Vulkan >=1.4 on Windows even for CPU inference.'
}
Write-Host '=== NETWORK ADAPTERS (informational, online preflight) ==='
Get-NetAdapter | Select-Object Name,Status,InterfaceDescription | Format-Table -AutoSize
Write-Host 'Do not publish unredacted host manifests or patient data.'
Write-Host 'BUILD07_PREFLIGHT=PASS_WITH_VULKAN_CHECK_AS_REPORTED'
