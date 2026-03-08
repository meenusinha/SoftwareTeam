# Start the agent animation window.
# Usage: .\scripts\Start-Animation.ps1 [-Demo]
param([switch]$Demo)
$root = Split-Path $PSScriptRoot
Set-Location $root
$args = if ($Demo) { '--demo' } else { '' }
python -m agent_animation.agent_window $args
