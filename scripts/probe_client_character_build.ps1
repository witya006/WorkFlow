$ErrorActionPreference = 'Stop'
$workspace = Split-Path -Parent $PSScriptRoot
$verified = Get-Content -LiteralPath (Join-Path $workspace 'inventory/msvc-verification.json') -Raw | ConvertFrom-Json
$cmake = Join-Path $verified.installation_path 'Common7/IDE/CommonExtensions/Microsoft/CMake/CMake/bin/cmake.exe'
$source = Join-Path $workspace 'work/client-build'
$build = Join-Path $source 'build-character-diagnostic'
$recovered = Join-Path $workspace 'work/recovered/character-legacy'
$contract = Get-Content -LiteralPath (Join-Path $workspace 'inventory/character-header-recovery.json') -Raw | ConvertFrom-Json
if ($contract.native_verification.compile_exit -ne 0 -or $contract.client_global_diagnostic.compile_exit -ne 0) {
    throw 'Run check_character_header.py and resolve the standalone/global.cpp compile before a full diagnostic build.'
}
if ((Get-FileHash -LiteralPath (Join-Path $recovered 'include/Character.h') -Algorithm SHA256).Hash.ToLowerInvariant() -ne $contract.header_sha256 -or
    (Get-FileHash -LiteralPath (Join-Path $recovered 'diagnostic_std.hpp') -Algorithm SHA256).Hash.ToLowerInvariant() -ne $contract.client_global_diagnostic.diagnostic_std_sha256) {
    throw 'Recovered header or compatibility shim changed since the preflight check.'
}
$logs = Join-Path $workspace 'artifacts/client-character-diagnostic'
$dx = Get-Content -LiteralPath (Join-Path $workspace 'inventory/directx81b-sdk.json') -Raw | ConvertFrom-Json
New-Item -ItemType Directory -Force -Path $logs | Out-Null
$arguments = @('-S', $source, '-B', $build, '-G', 'Visual Studio 18 2026', '-A', 'Win32', '-T', 'v145', '-DCMAKE_SYSTEM_VERSION=10.0.26100.0',
    "-DRF_LEGACY_DX8_INCLUDE=$(Join-Path $workspace 'local/directx81b/include-overlay')",
    "-DRF_LEGACY_DX8_LIBRARY=$(Join-Path $dx.sdk_root 'lib')",
    "-DRF_RECOVERED_CHARACTER_INCLUDE=$(Join-Path $recovered 'include')",
    "-DRF_CHARACTER_STD_DIAGNOSTIC=$(Join-Path $recovered 'diagnostic_std.hpp')")
& $cmake @arguments *> (Join-Path $logs 'configure.txt')
if ($LASTEXITCODE -ne 0) { Get-Content -LiteralPath (Join-Path $logs 'configure.txt') -Tail 15; exit $LASTEXITCODE }
& $cmake --build $build --config Release --target RF_Online --parallel 4 *> (Join-Path $logs 'build.txt')
$result = $LASTEXITCODE
& (Join-Path $PSScriptRoot 'Invoke-Python.ps1') scripts/summarize_executable_build.py --build-exit $result --log artifacts/client-character-diagnostic/build.txt --build-dir work/client-build/build-character-diagnostic --output inventory/client-character-diagnostic.json --max-details 80
Write-Output "Diagnostic RF_Online build exit: $result"
exit $result
