param([string]$DirectXInclude = '', [switch]$CleanRebuild)
$ErrorActionPreference = 'Stop'
$workspace = Split-Path -Parent $PSScriptRoot
$verified = Get-Content -LiteralPath (Join-Path $workspace 'inventory/msvc-verification.json') -Raw | ConvertFrom-Json
$cmakePath = Join-Path $verified.installation_path 'Common7/IDE/CommonExtensions/Microsoft/CMake/CMake/bin/cmake.exe'
$sourcePath = Join-Path $workspace 'work/client-build'
$buildPath = Join-Path $sourcePath 'build-vs2026'
$logPath = Join-Path $workspace 'artifacts/client-build'
New-Item -ItemType Directory -Force -Path $logPath | Out-Null
$cmakeArgs = @('-S', $sourcePath, '-B', $buildPath, '-G', 'Visual Studio 18 2026', '-A', 'Win32', '-T', 'v145', '-DCMAKE_SYSTEM_VERSION=10.0.26100.0')
if ($DirectXInclude) { $cmakeArgs += "-DRF_LEGACY_DX8_INCLUDE=$DirectXInclude" }
& $cmakePath @cmakeArgs *> (Join-Path $logPath 'configure.txt')
if ($LASTEXITCODE -ne 0) { Get-Content -LiteralPath (Join-Path $logPath 'configure.txt') -Tail 20; exit $LASTEXITCODE }
$buildArgs = @('--build', $buildPath, '--config', 'Release', '--target', 'R3Engine', '--parallel', '4')
if ($CleanRebuild) { $buildArgs += '--clean-first' }
& $cmakePath @buildArgs *> (Join-Path $logPath 'build.txt')
$buildExit = $LASTEXITCODE
& (Join-Path $PSScriptRoot 'Invoke-Python.ps1') scripts/summarize_client_build.py --build-exit $buildExit
Write-Output "R3Engine build exit: $buildExit"
Get-Content -LiteralPath (Join-Path $logPath 'build.txt') -Tail 18
exit $buildExit
