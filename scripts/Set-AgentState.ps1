# Write agent state from a shell workflow step.
# Usage: .\scripts\Set-AgentState.ps1 <agent> <state> [message]
#
# Examples:
#   .\scripts\Set-AgentState.ps1 developer typing "Writing code for PR #42"
#   .\scripts\Set-AgentState.ps1 architect reviewing "Checking design patterns"
#   .\scripts\Set-AgentState.ps1 tester approved "All tests pass"
param(
    [string]$Agent   = 'developer',
    [string]$State   = 'idle',
    [string]$Message = ''
)

$root = Split-Path $PSScriptRoot
Set-Location $root

# Auto-start animation window if not already running (safe — duplicate guard is in Start-Animation.ps1)
Start-Process powershell -ArgumentList "-WindowStyle Hidden -NonInteractive -File `"$PSScriptRoot\Start-Animation.ps1`"" -NoNewWindow

python -c @"
from agent_animation.state import write
write('$Agent', '$State', '$Message')
print(f'State: $Agent / $State')
"@
