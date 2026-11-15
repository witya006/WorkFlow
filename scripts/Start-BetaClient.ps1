param(
    [ValidateSet('ru-ru', 'zh-tw')]
    [string]$Locale,
    [switch]$RecordCrash
)

$ErrorActionPreference = 'Stop'
$workspace = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $workspace
try {
    $Host.UI.RawUI.WindowTitle = 'RF Online 455 - Beta launcher'
    Write-Host 'RF Online 455 - full beta client (1920 x 1080)' -ForegroundColor Cyan
    while (-not $Locale) {
        $choice = (Read-Host 'Launch [1 / Enter: Russian, 2: Taiwan, 3: Russian + crash trace, 4: Taiwan + crash trace]').Trim()
        switch ($choice) {
            ''  { $Locale = 'ru-ru' }
            '1' { $Locale = 'ru-ru' }
            '2' { $Locale = 'zh-tw' }
            '3' { $Locale = 'ru-ru'; $RecordCrash = $true }
            '4' { $Locale = 'zh-tw'; $RecordCrash = $true }
            default { Write-Host 'Choose 1, 2, 3 or 4.' -ForegroundColor Yellow }
        }
    }
    Write-Host 'The local server must be running. Enter the test account below.'
    Write-Host 'Password input is hidden. Close the current game before restarting.'
    $paths = Get-Content -LiteralPath 'config/paths.json' -Raw | ConvertFrom-Json
    $launcherArgs = @('--current-build', '--audio', '--locale', $Locale)
    if ($RecordCrash) { $launcherArgs += '--record-crash' }
    & $paths.audit_python 'scripts/preview_client455.py' @launcherArgs
    if ($LASTEXITCODE -ne 0) { throw "Client launch failed (code $LASTEXITCODE). See the message above." }
} catch {
    Write-Host $_.Exception.Message -ForegroundColor Red
    Read-Host 'Press Enter to close'
    exit 1
}
