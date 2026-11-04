param(
    [Parameter(Mandatory=$true, Position=0)][string]$Script,
    [Parameter(ValueFromRemainingArguments=$true)][string[]]$ScriptArguments
)
$ErrorActionPreference = 'Stop'
$workspace = Split-Path -Parent $PSScriptRoot
$paths = Get-Content -LiteralPath (Join-Path $workspace 'config/paths.json') -Raw | ConvertFrom-Json
if (-not (Test-Path -LiteralPath $paths.audit_python)) { throw 'Audit Python is missing; update config/paths.json.' }
$scriptPath = if ([IO.Path]::IsPathRooted($Script)) { $Script } else { Join-Path $workspace $Script }
& $paths.audit_python $scriptPath @ScriptArguments
exit $LASTEXITCODE
