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
$jpeg = Get-Content -LiteralPath (Join-Path $workspace 'inventory/jpeg6b-build.json') -Raw | ConvertFrom-Json
$jpegLibrary = Join-Path $workspace $jpeg.library
if ((Get-FileHash -LiteralPath $jpegLibrary -Algorithm SHA256).Hash.ToLowerInvariant() -ne $jpeg.library_sha256) { throw 'JPEG archive changed since verification.' }
$arguments += "-DRF_JPEG_LIBRARY_DIR=$(Split-Path -Parent $jpegLibrary)"
$characterLibrary = Join-Path $source 'source/RF_Client/CharacterMR.lib'
if ((Get-FileHash -LiteralPath $characterLibrary -Algorithm SHA256).Hash.ToLowerInvariant() -ne '483715b927690fc69607682a093dff53635911870456f5849c9f52741702b8a8') { throw 'Character reference digest changed.' }
$stdioReport = Join-Path $workspace 'inventory/character-stdio-adapter.json'
if (Test-Path -LiteralPath $stdioReport) {
    $stdio = Get-Content -LiteralPath $stdioReport -Raw | ConvertFrom-Json
    $characterLibrary = Join-Path $workspace $stdio.adapted_archive
    $adapterLibrary = Join-Path $workspace $stdio.adapter_library
    if ((Get-FileHash -LiteralPath $characterLibrary -Algorithm SHA256).Hash.ToLowerInvariant() -ne $stdio.adapted_archive_sha256 -or
        (Get-FileHash -LiteralPath $adapterLibrary -Algorithm SHA256).Hash.ToLowerInvariant() -ne $stdio.adapter_library_sha256 -or
        (Get-FileHash -LiteralPath $stdio.classic_provider_hash_file -Algorithm SHA256).Hash.ToLowerInvariant() -ne $stdio.classic_provider_sha256) { throw 'Character stdio adapter/provider changed since verification.' }
    $arguments += "-DRF_CHARACTER_STDIO_ADAPTER_LIBRARY=$adapterLibrary"
}
$arguments += "-DRF_CHARACTER_REFERENCE_LIBRARY=$characterLibrary"
$exceptionsReport = Join-Path $workspace 'inventory/character-exceptions.json'
if (Test-Path -LiteralPath $exceptionsReport) {
    $exceptions = Get-Content -LiteralPath $exceptionsReport -Raw | ConvertFrom-Json
    $exceptionsLibrary = Join-Path $workspace $exceptions.library
    if ((Get-FileHash -LiteralPath $exceptionsLibrary -Algorithm SHA256).Hash.ToLowerInvariant() -ne $exceptions.library_sha256) { throw 'Recovered exception library changed since verification.' }
    $arguments += "-DRF_CHARACTER_EXCEPTIONS_LIBRARY=$exceptionsLibrary"
}
$managerReport = Join-Path $workspace 'inventory/character-managers.json'
if (Test-Path -LiteralPath $managerReport) {
    $manager = Get-Content -LiteralPath $managerReport -Raw | ConvertFrom-Json
    $managerLibrary = Join-Path $workspace $manager.library
    if ((Get-FileHash -LiteralPath $managerLibrary -Algorithm SHA256).Hash.ToLowerInvariant() -ne $manager.library_sha256 -or
        $contract.header_sha256 -ne $manager.header_sha256) { throw 'Recovered manager/header changed since runtime verification.' }
    $arguments += "-DRF_CHARACTER_RECOVERED_MANAGERS_LIBRARY=$managerLibrary"
}
$arguments += '-DRF_DIAGNOSTIC_DEFER_LIBRARIES=CharacterR.lib;ziplibm.lib;ZipArchive_STL_M.lib;libci.lib'
$settersReport = Join-Path $workspace 'inventory/character-setters.json'
if (Test-Path -LiteralPath $settersReport) {
    $setters = Get-Content -LiteralPath $settersReport -Raw | ConvertFrom-Json
    $settersLibrary = Join-Path $workspace $setters.library
    if ((Get-FileHash -LiteralPath $settersLibrary -Algorithm SHA256).Hash.ToLowerInvariant() -ne $setters.library_sha256 -or
        $contract.header_sha256 -ne $setters.header_sha256) { throw 'Recovered setters/header changed since verification.' }
    $arguments += "-DRF_CHARACTER_SETTERS_LIBRARY=$settersLibrary"
}
& $cmake @arguments *> (Join-Path $logs 'configure.txt')
if ($LASTEXITCODE -ne 0) { Get-Content -LiteralPath (Join-Path $logs 'configure.txt') -Tail 15; exit $LASTEXITCODE }
& $cmake --build $build --config Release --target RF_Online --parallel 4 *> (Join-Path $logs 'build.txt')
$result = $LASTEXITCODE
& (Join-Path $PSScriptRoot 'Invoke-Python.ps1') scripts/summarize_executable_build.py --build-exit $result --log artifacts/client-character-diagnostic/build.txt --build-dir work/client-build/build-character-diagnostic --output inventory/client-character-diagnostic.json --max-details 80
Write-Output "Diagnostic RF_Online build exit: $result"
exit $result
