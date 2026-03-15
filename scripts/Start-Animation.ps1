# Start the agent animation window (skips launch if already running).
# Usage: .\scripts\Start-Animation.ps1 [-Demo]
param([switch]$Demo)

# Only one instance at a time
$existing = Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
    Where-Object { $_.CommandLine -like '*agent_animation.agent_window*' }
if ($existing) { exit 0 }

$root = Split-Path $PSScriptRoot
Set-Location $root
$extraArgs = if ($Demo) { @('--demo') } else { @() }

# Start as independent process so it survives the calling shell exiting
Start-Process python -ArgumentList (@('-m', 'agent_animation.agent_window') + $extraArgs) `
    -WorkingDirectory $root -WindowStyle Hidden
