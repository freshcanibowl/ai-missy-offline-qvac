# Read-only host diagnostics. Does NOT install software, download models, or alter network settings.
param([string]$OutputDir = '.\local-evidence')
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
$dest = Join-Path (Resolve-Path $OutputDir).Path 'WINDOWS_TRIAGE.json'
$items = [ordered]@{schema='ai-missy-windows-triage/1'; generated_utc=[DateTime]::UtcNow.ToString('o'); status='DIAGNOSTIC_ONLY'; model_inference='NOT_EXECUTED'; offline_proof='NOT_EXECUTED'}
function CommandVersion([string]$name,[string]$flag) {
  if (-not (Get-Command $name -ErrorAction SilentlyContinue)) {return 'NOT_INSTALLED'}
  try { $v = & $name $flag 2>&1; if ($LASTEXITCODE -ne 0) {return 'ERROR'}; return (($v | Select-Object -First 1) -join '') }
  catch {return 'ERROR'}
}
$items.node = CommandVersion 'node' '--version'
$items.npm = CommandVersion 'npm' '--version'
$items.python = CommandVersion 'py' '--version'
$items.git = CommandVersion 'git' '--version'
$items.github_cli = CommandVersion 'gh' '--version'
$items.qvac_sdk_installed = (Test-Path '.\node_modules\@qvac\sdk\package.json')
$items.node_compatible = $false
if ($items.node -match '^v?(\d+)\.(\d+)\.(\d+)') {
  $major=[int]$Matches[1]; $minor=[int]$Matches[2]; $patch=[int]$Matches[3]
  $items.node_compatible = (($major -eq 22 -and ($minor -gt 21 -or ($minor -eq 21 -and $patch -ge 0))) -or ($major -eq 24 -and ($minor -gt 9 -or ($minor -eq 9 -and $patch -ge 0))) -or ($major -gt 24))
}
$items.windows = [Environment]::OSVersion.Platform -eq [PlatformID]::Win32NT
$items.os_64bit = [Environment]::Is64BitOperatingSystem
$items.vulkaninfo_available = [bool](Get-Command 'vulkaninfo' -ErrorAction SilentlyContinue)
$items.vulkan_1_4_verified = $false
if ($items.vulkaninfo_available) {
  try {
    $vk = (& vulkaninfo --summary 2>&1 | Out-String)
    if ($LASTEXITCODE -eq 0 -and $vk -match 'Vulkan Instance Version:\s*1\.([4-9]|[1-9][0-9])\.') {$items.vulkan_1_4_verified = $true}
    $items.vulkan_diagnostic = if ($LASTEXITCODE -eq 0) {'RAN_CHECK_DETAILS_LOCALLY'} else {'VULKANINFO_FAILED'}
  } catch { $items.vulkan_diagnostic = 'VULKANINFO_ERROR' }
} else {$items.vulkan_diagnostic = 'UNVERIFIED_NO_VULKANINFO'}
$items.next_action = if (-not $items.node_compatible) {'UPDATE_NODE'} elseif (-not $items.qvac_sdk_installed) {'RUN_PREPARE_ONLINE'} elseif (-not $items.vulkan_1_4_verified) {'VERIFY_VULKAN_DRIVER_AND_RUNTIME'} else {'RUN_PREPARE_ONLINE_THEN_VERIFY_OFFLINE'}
$items.privacy_note = 'No usernames, network identifiers, paths, or patient records collected; inspect JSON before sharing.'
$items | ConvertTo-Json -Depth 5 | Set-Content -Encoding UTF8 -Path $dest
Write-Host "AI_MISSY_TRIAGE=$($items.next_action)"
Write-Host "TRIAGE_REPORT=$dest"
Write-Host 'DIAGNOSTIC_ONLY=TRUE; not QVAC proof.'
