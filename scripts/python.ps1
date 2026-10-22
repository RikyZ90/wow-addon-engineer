# Resolve a real Python interpreter, including installations outside PATH.
param(
    [Parameter(Mandatory = $true)][string]$Script,
    [Parameter(ValueFromRemainingArguments = $true)][string[]]$ScriptArguments
)
$ErrorActionPreference = 'Stop'
if ($env:WAE_PYTHON) {
    $candidates = @($env:WAE_PYTHON)
} else {
    $candidates = @('py', 'python', 'python3')
}
foreach ($candidate in $candidates) {
    $command = Get-Command $candidate -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $command -or $command.Source -like '*\Microsoft\WindowsApps\*') { continue }
    $prefix = @()
    if ($command.Name -eq 'py.exe') { $prefix = @('-3') }
    & $command.Source @prefix -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' 2>$null
    if ($LASTEXITCODE -ne 0) { continue }
    & $command.Source @prefix (Join-Path $PSScriptRoot $Script) @ScriptArguments
    exit $LASTEXITCODE
}
[Console]::Error.WriteLine('Python 3.10+ was not found. Install Python yourself or set WAE_PYTHON to its executable path.')
exit 2
