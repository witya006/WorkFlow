param([string]$DirectXInclude = '', [switch]$CleanRebuild, [ValidateSet('R3Engine','RF_Online')][string]$Target = 'R3Engine')
$ErrorActionPreference = 'Stop'
$workspace = Split-Path -Parent $PSScriptRoot
$verified = Get-Content -LiteralPath (Join-Path $workspace 'inventory/msvc-verification.json') -Raw | ConvertFrom-Json
$cmakePath = Join-Path $verified.installation_path 'Common7/IDE/CommonExtensions/Microsoft/CMake/CMake/bin/cmake.exe'
$sourcePath = Join-Path $workspace 'work/client-build'
$buildPath = Join-Path $sourcePath 'build-vs2026'
$logPath = Join-Path $workspace $(if ($Target -eq 'RF_Online') { 'artifacts/client-executable-build' } else { 'artifacts/client-build' })
New-Item -ItemType Directory -Force -Path $logPath | Out-Null
$cmakeArgs = @('-S', $sourcePath, '-B', $buildPath, '-G', 'Visual Studio 18 2026', '-A', 'Win32', '-T', 'v145', '-DCMAKE_SYSTEM_VERSION=10.0.26100.0')
if ($DirectXInclude) { $cmakeArgs += "-DRF_LEGACY_DX8_INCLUDE=$DirectXInclude" }
& $cmakePath @cmakeArgs *> (Join-Path $logPath 'configure.txt')
if ($LASTEXITCODE -ne 0) { Get-Content -LiteralPath (Join-Path $logPath 'configure.txt') -Tail 20; exit $LASTEXITCODE }
$buildArgs = @('--build', $buildPath, '--config', 'Release', '--target', $Target, '--parallel', '4')
if ($CleanRebuild) { $buildArgs += '--clean-first' }
& $cmakePath @buildArgs *> (Join-Path $logPath 'build.txt')
$buildExit = $LASTEXITCODE
if ($Target -eq 'R3Engine') { & (Join-Path $PSScriptRoot 'Invoke-Python.ps1') scripts/summarize_client_build.py --build-exit $buildExit }
else { & (Join-Path $PSScriptRoot 'Invoke-Python.ps1') scripts/summarize_executable_build.py --build-exit $buildExit }
Write-Output "$Target build exit: $buildExit"
if ($buildExit -ne 0) {
    Select-String -LiteralPath (Join-Path $logPath 'build.txt') -Pattern 'error [A-Z]+\d+:' | Select-Object -First 8 -ExpandProperty Line
}
else { Get-Content -LiteralPath (Join-Path $logPath 'build.txt') -Tail 2 }
exit $buildExit
