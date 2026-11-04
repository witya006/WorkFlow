param([switch]$CleanRebuild, [switch]$HelperLab)
$ErrorActionPreference = 'Stop'
$workspace = Split-Path -Parent $PSScriptRoot
$behavior = Get-Content -LiteralPath (Join-Path $workspace 'inventory/client-behavior-patches.json') -Raw | ConvertFrom-Json
foreach ($patch in $behavior) {
    if ((Get-FileHash -LiteralPath (Join-Path $workspace $patch.file) -Algorithm SHA256).Hash.ToLowerInvariant() -ne $patch.patched_sha256) { throw '455 behavior patch changed since evidence verification.' }
}
$verified = Get-Content -LiteralPath (Join-Path $workspace 'inventory/msvc-verification.json') -Raw | ConvertFrom-Json
$cmake = Join-Path $verified.installation_path 'Common7/IDE/CommonExtensions/Microsoft/CMake/CMake/bin/cmake.exe'
$source = Join-Path $workspace 'work/client-build'
$build = Join-Path $source 'build-character-diagnostic'
if ($HelperLab) { $build = Join-Path $source 'build-helper-lab' }
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
if ($HelperLab) { $logs = Join-Path $workspace 'artifacts/client-helper-lab' }
$dx = Get-Content -LiteralPath (Join-Path $workspace 'inventory/directx81b-sdk.json') -Raw | ConvertFrom-Json
New-Item -ItemType Directory -Force -Path $logs | Out-Null
$arguments = @('-S', $source, '-B', $build, '-G', 'Visual Studio 18 2026', '-A', 'Win32', '-T', 'v145', '-DCMAKE_SYSTEM_VERSION=10.0.26100.0',
    '-DCMAKE_CXX_FLAGS=/DWIN32 /D_WINDOWS /W3 /GR /EHsc',
    '-DCMAKE_CXX_FLAGS_RELEASE=/O2 /Ob2 /DNDEBUG',
    "-DRF_LEGACY_DX8_INCLUDE=$(Join-Path $workspace 'local/directx81b/include-overlay')",
    "-DRF_LEGACY_DX8_LIBRARY=$(Join-Path $dx.sdk_root 'lib')",
    "-DRF_RECOVERED_CHARACTER_INCLUDE=$(Join-Path $recovered 'include')",
    "-DRF_CHARACTER_STD_DIAGNOSTIC=$(Join-Path $recovered 'diagnostic_std.hpp')",
    '-DRF_CLIENT_455_DRAW_ARGUMENTS=ON')
$logger = Get-Content -LiteralPath (Join-Path $workspace 'inventory/client455-effect-log.json') -Raw | ConvertFrom-Json
$loggerLibrary = Join-Path $workspace $logger.library
if ((Get-FileHash -LiteralPath $loggerLibrary -Algorithm SHA256).Hash.ToLowerInvariant() -ne $logger.library_sha256 -or
    $logger.cases.Count -ne 14 -or $logger.native_checks -lt 66) { throw '455 effect logger verification is stale or incomplete.' }
foreach ($property in $logger.source_sha256.PSObject.Properties) {
    if ((Get-FileHash -LiteralPath (Join-Path $workspace "scripts/native/$($property.Name)") -Algorithm SHA256).Hash.ToLowerInvariant() -ne $property.Value) { throw '455 effect logger source changed since verification.' }
}
if (-not ($behavior | Where-Object { $_.build_option -eq 'RF_CLIENT_455_EFFECT_LOG' -and $_.implementation_library_sha256 -eq $logger.library_sha256 })) { throw '455 effect logger source selection is missing or stale.' }
$arguments += '-DRF_CLIENT_455_EFFECT_LOG=ON'
$arguments += "-DRF_CLIENT_455_EFFECT_LOG_LIBRARY=$loggerLibrary"
if (-not ($behavior | Where-Object { $_.build_option -eq 'RF_CLIENT_455_LOBBY_TRANSITION' })) { throw '455 lobby transition evidence/selection is missing.' }
$arguments += '-DRF_CLIENT_455_LOBBY_TRANSITION=ON'
if (-not ($behavior | Where-Object { $_.build_option -eq 'RF_CLIENT_455_HELPER_LOADER' })) { throw '455 helper-loader evidence/selection is missing.' }
$arguments += '-DRF_CLIENT_455_HELPER_LOADER=ON'
if (-not ($behavior | Where-Object { $_.build_option -eq 'RF_CLIENT_455_WEATHER' })) { throw '455 weather source selection is missing.' }
$arguments += '-DRF_CLIENT_455_WEATHER=ON'
$clock = Get-Content -LiteralPath (Join-Path $workspace 'inventory/client455-clock.json') -Raw | ConvertFrom-Json
if ($clock.native_test.failures -ne 0 -or $clock.native_test.precision_rounding_modes -ne 12 -or $clock.native_test.checks -lt 1443) { throw '455 clock component proof missing.' }
foreach ($property in $clock.source_sha256.PSObject.Properties) {
    if ((Get-FileHash -LiteralPath (Join-Path $workspace "scripts/native/$($property.Name)") -Algorithm SHA256).Hash.ToLowerInvariant() -ne $property.Value) { throw '455 clock source proof stale.' }
}
$arguments += '-DRF_CLIENT_455_CLOCK=ON'
$commands = Get-Content -LiteralPath (Join-Path $workspace 'inventory/client455-time-commands.json') -Raw | ConvertFrom-Json
if ($commands.native_test.failures -ne 0 -or $commands.native_test.checks -lt 2628 -or $commands.native_test.cases -ne 432) { throw '455 time command component proof missing.' }
if ($commands.clock_library_sha256 -ne $clock.library_sha256) { throw 'Time commands were not tested against the current clock component.' }
foreach ($property in $commands.source_sha256.PSObject.Properties) {
    if ((Get-FileHash -LiteralPath (Join-Path $workspace "scripts/native/$($property.Name)") -Algorithm SHA256).Hash.ToLowerInvariant() -ne $property.Value) { throw '455 time command source proof stale.' }
}
if (-not ($behavior | Where-Object { $_.build_option -eq 'RF_CLIENT_455_TIME_COMMANDS' })) { throw '455 time command source selection missing.' }
$arguments += '-DRF_CLIENT_455_TIME_COMMANDS=ON'
$mapTime = Get-Content -LiteralPath (Join-Path $workspace 'inventory/client455-map-time.json') -Raw | ConvertFrom-Json
if ($mapTime.native_test.failures -ne 0 -or $mapTime.native_test.checks -lt 314 -or $mapTime.native_test.precision_rounding_modes -ne 12) { throw '455 map time component proof missing.' }
if ($mapTime.clock_library_sha256 -ne $clock.library_sha256) { throw 'Map time was not tested against the current clock component.' }
foreach ($property in $mapTime.source_sha256.PSObject.Properties) {
    if ((Get-FileHash -LiteralPath (Join-Path $workspace "scripts/native/$($property.Name)") -Algorithm SHA256).Hash.ToLowerInvariant() -ne $property.Value) { throw '455 map time source proof stale.' }
}
if (-not ($behavior | Where-Object { $_.build_option -eq 'RF_CLIENT_455_MAP_TIME' })) { throw '455 map time source selection missing.' }
$arguments += '-DRF_CLIENT_455_MAP_TIME=ON'
$resources = Get-Content -LiteralPath (Join-Path $workspace 'inventory/client455-resource-io.json') -Raw | ConvertFrom-Json
if ($resources.native_checks -lt 18895 -or $resources.archives.Count -ne 78) { throw 'Native resource-I/O proof missing.' }
foreach ($property in $resources.source_sha256.PSObject.Properties) {
    if ((Get-FileHash -LiteralPath (Join-Path $workspace "scripts/native/$($property.Name)") -Algorithm SHA256).Hash.ToLowerInvariant() -ne $property.Value) { throw 'Resource I/O source proof stale.' }
}
$arguments += '-DRF_CLIENT_455_RESOURCE_IO=ON'
$math = Get-Content -LiteralPath (Join-Path $workspace 'inventory/client455-x87-math.json') -Raw | ConvertFrom-Json
$mathLibrary = Join-Path $workspace $math.library
if ((Get-FileHash -LiteralPath $mathLibrary -Algorithm SHA256).Hash.ToLowerInvariant() -ne $math.library_sha256 -or
    $math.native_test.checks -lt 338 -or $math.native_test.failures -ne 0 -or $math.native_test.precision_rounding_modes -ne 12) { throw '455 x87 math proof is missing or stale.' }
foreach ($property in $math.source_sha256.PSObject.Properties) {
    if ((Get-FileHash -LiteralPath (Join-Path $workspace "scripts/native/$($property.Name)") -Algorithm SHA256).Hash.ToLowerInvariant() -ne $property.Value) { throw '455 x87 math source changed since verification.' }
}
if (-not ($behavior | Where-Object { $_.build_option -eq 'RF_CLIENT_455_X87_MATH' -and $_.implementation_library_sha256 -eq $math.library_sha256 })) { throw '455 x87 math source selection is missing or stale.' }
$arguments += '-DRF_CLIENT_455_X87_MATH=ON'
$arguments += "-DRF_CLIENT_455_X87_MATH_LIBRARY=$mathLibrary"
$arguments += "-DRF_CLIENT_HELPER_LAB=$(if ($HelperLab) { 'ON' } else { 'OFF' })"
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
$meshSource = Get-Content -LiteralPath (Join-Path $workspace 'inventory/character-mesh-source.json') -Raw | ConvertFrom-Json
$meshLibrary = Join-Path $workspace $meshSource.library
$meshArchive = Join-Path $workspace $meshSource.adapted_archive
if ((Get-FileHash -LiteralPath $meshLibrary -Algorithm SHA256).Hash.ToLowerInvariant() -ne $meshSource.library_sha256 -or
    (Get-FileHash -LiteralPath $meshArchive -Algorithm SHA256).Hash.ToLowerInvariant() -ne $meshSource.adapted_archive_sha256 -or
    $meshSource.base_archive_sha256 -ne $stdio.adapted_archive_sha256 -or $meshSource.header_sha256 -ne $contract.header_sha256 -or
    $meshSource.native_test.source_functions -ne 4 -or $meshSource.native_test.checks_passed -ne 245 -or
    -not $meshSource.native_test.actual_init_vertex) { throw 'Recovered Character mesh source/archive proof is missing or stale.' }
foreach ($property in $meshSource.source_sha256.PSObject.Properties) {
    if ((Get-FileHash -LiteralPath (Join-Path $workspace "scripts/native/$($property.Name)") -Algorithm SHA256).Hash.ToLowerInvariant() -ne $property.Value) { throw 'Character mesh source changed since verification.' }
}
foreach ($property in $meshSource.script_sha256.PSObject.Properties) {
    if ((Get-FileHash -LiteralPath (Join-Path $workspace "scripts/$($property.Name)") -Algorithm SHA256).Hash.ToLowerInvariant() -ne $property.Value) { throw 'Character mesh source substitution changed since verification.' }
}
$characterLibrary = $meshArchive
$arguments += '-DRF_CHARACTER_MESH_SOURCE=ON'
$arguments += "-DRF_CHARACTER_MESH_SOURCE_LIBRARY=$meshLibrary"
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
    $effectProbe = Get-Content -LiteralPath (Join-Path $workspace 'inventory/character-effect-loaders.json') -Raw | ConvertFrom-Json
    if ($effectProbe.setter_library_sha256 -ne $setters.library_sha256 -or
        $effectProbe.header_sha256 -ne $contract.header_sha256 -or
        $effectProbe.native_test.mesh_effects_applied -ne 2) { throw 'Actual legacy effect-loader/application check is stale or missing.' }
    $arguments += "-DRF_CHARACTER_SETTERS_LIBRARY=$settersLibrary"
}
& $cmake @arguments *> (Join-Path $logs 'configure.txt')
if ($LASTEXITCODE -ne 0) { Get-Content -LiteralPath (Join-Path $logs 'configure.txt') -Tail 15; exit $LASTEXITCODE }
$buildArguments = @('--build',$build,'--config','Release','--target','RF_Online','--parallel','4')
if ($CleanRebuild) { $buildArguments += '--clean-first' }
& $cmake @buildArguments *> (Join-Path $logs 'build.txt')
$result = $LASTEXITCODE
if ($HelperLab) {
    & (Join-Path $PSScriptRoot 'Invoke-Python.ps1') scripts/summarize_executable_build.py --build-exit $result --log artifacts/client-helper-lab/build.txt --build-dir work/client-build/build-helper-lab --output inventory/client-helper-lab-build.json --max-details 80
} else {
    & (Join-Path $PSScriptRoot 'Invoke-Python.ps1') scripts/summarize_executable_build.py --build-exit $result --log artifacts/client-character-diagnostic/build.txt --build-dir work/client-build/build-character-diagnostic --output inventory/client-character-diagnostic.json --max-details 80
}
if ($result -eq 0) {
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    if ($HelperLab) {
        & (Join-Path $PSScriptRoot 'Invoke-Python.ps1') scripts/verify_client_x87_math455.py --lab
    } else {
        & (Join-Path $PSScriptRoot 'Invoke-Python.ps1') scripts/verify_client_x87_math455.py
    }
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    if ($HelperLab) {
        & (Join-Path $PSScriptRoot 'Invoke-Python.ps1') scripts/verify_client_clock455.py --lab
    } else {
        & (Join-Path $PSScriptRoot 'Invoke-Python.ps1') scripts/verify_client_clock455.py
    }
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    if ($HelperLab) {
        & (Join-Path $PSScriptRoot 'Invoke-Python.ps1') scripts/verify_client_map_time455.py --lab
    } else {
        & (Join-Path $PSScriptRoot 'Invoke-Python.ps1') scripts/verify_client_map_time455.py
    }
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    if ($HelperLab) {
        & (Join-Path $PSScriptRoot 'Invoke-Python.ps1') scripts/verify_client_time_commands455.py --lab
    } else {
        & (Join-Path $PSScriptRoot 'Invoke-Python.ps1') scripts/verify_client_time_commands455.py
    }
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    if ($HelperLab) {
        & (Join-Path $PSScriptRoot 'Invoke-Python.ps1') scripts/verify_character_mesh_source.py --lab
    } else {
        & (Join-Path $PSScriptRoot 'Invoke-Python.ps1') scripts/verify_character_mesh_source.py
    }
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
Write-Output "Diagnostic RF_Online build exit: $result"
exit $result
