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
    -not $meshSource.native_test.actual_init_vertex -or $meshSource.source_function_count -ne 8 -or
    $meshSource.native_init_test.checks_passed -ne 6732 -or $meshSource.native_init_test.cases -ne 144 -or
    $meshSource.native_init_test.precision_rounding_modes -ne 12) { throw 'Recovered Character mesh/InitVertex source/archive proof is missing or stale.' }
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
$mesh08 = Get-Content -LiteralPath (Join-Path $workspace 'inventory/client455-mesh08.json') -Raw | ConvertFrom-Json
$mesh08Library = Join-Path $workspace $mesh08.library
if ((Get-FileHash -LiteralPath $mesh08Library -Algorithm SHA256).Hash.ToLowerInvariant() -ne $mesh08.library_sha256 -or
    $mesh08.native_test.failures -ne 0 -or $mesh08.native_test.boundary_cases -ne 1309 -or
    $mesh08.native_test.checks -lt 6304 -or -not $mesh08.native_test.guard_pages_used) { throw 'MESH08 source proof missing or stale.' }
foreach ($property in $mesh08.source_sha256.PSObject.Properties) {
    if ((Get-FileHash -LiteralPath (Join-Path $workspace "scripts/native/$($property.Name)") -Algorithm SHA256).Hash.ToLowerInvariant() -ne $property.Value) { throw 'MESH08 source changed since verification.' }
}
if ((Get-FileHash -LiteralPath (Join-Path $workspace 'inventory/character-mesh08-corpus.json') -Algorithm SHA256).Hash.ToLowerInvariant() -ne $mesh08.corpus_report_sha256) { throw 'MESH08 corpus proof changed.' }
$arguments += '-DRF_CLIENT_455_MESH08=ON'
$arguments += "-DRF_CLIENT_455_MESH08_LIBRARY=$mesh08Library"
$mesh455 = Get-Content -LiteralPath (Join-Path $workspace 'inventory/client455-mesh-bindings.json') -Raw | ConvertFrom-Json
$mesh455Library = Join-Path $workspace $mesh455.library
if ((Get-FileHash -LiteralPath $mesh455Library -Algorithm SHA256).Hash.ToLowerInvariant() -ne $mesh455.library_sha256 -or
    $mesh455.native_test.failures -ne 0 -or $mesh455.native_test.real_pairs -ne 12 -or
    $mesh455.native_test.parts -ne 393 -or $mesh455.native_test.overlap_cases -ne 20) { throw '455 mesh binding source proof missing or stale.' }
foreach ($property in $mesh455.source_sha256.PSObject.Properties) {
    if ((Get-FileHash -LiteralPath (Join-Path $workspace "scripts/native/$($property.Name)") -Algorithm SHA256).Hash.ToLowerInvariant() -ne $property.Value) { throw '455 mesh binding source changed since verification.' }
}
if ((Get-FileHash -LiteralPath (Join-Path $workspace 'inventory/character-mesh08-bone-pairs.json') -Algorithm SHA256).Hash.ToLowerInvariant() -ne $mesh455.pair_report_sha256 -or
    (Get-FileHash -LiteralPath (Join-Path $workspace 'inventory/client455-mesh-bindings-reference.json') -Algorithm SHA256).Hash.ToLowerInvariant() -ne $mesh455.reference_report_sha256) { throw '455 mesh binding inputs changed.' }
$arguments += '-DRF_CLIENT_455_MESH_BINDINGS=ON'
$arguments += "-DRF_CLIENT_455_MESH_BINDINGS_LIBRARY=$mesh455Library"
$meshRuntime = Get-Content -LiteralPath (Join-Path $workspace 'inventory/client455-mesh-runtime.json') -Raw | ConvertFrom-Json
$meshRuntimeLibrary = Join-Path $workspace $meshRuntime.library
if ((Get-FileHash -LiteralPath $meshRuntimeLibrary -Algorithm SHA256).Hash.ToLowerInvariant() -ne $meshRuntime.library_sha256 -or
    $meshRuntime.native_test.failures -ne 0 -or $meshRuntime.native_test.real_files -ne 12 -or
    $meshRuntime.native_test.parts -ne 393 -or $meshRuntime.native_test.precision_rounding_modes -ne 12 -or
    $meshRuntime.native_test.material_cases -ne 8 -or $meshRuntime.native_test.checks -lt 14562) { throw '455 mesh runtime source proof missing or stale.' }
foreach ($property in $meshRuntime.source_sha256.PSObject.Properties) {
    if ((Get-FileHash -LiteralPath (Join-Path $workspace "scripts/native/$($property.Name)") -Algorithm SHA256).Hash.ToLowerInvariant() -ne $property.Value) { throw '455 mesh runtime source changed.' }
}
if ((Get-FileHash -LiteralPath (Join-Path $workspace 'inventory/character-mesh08-headers.json') -Algorithm SHA256).Hash.ToLowerInvariant() -ne $meshRuntime.header_report_sha256 -or
    (Get-FileHash -LiteralPath (Join-Path $workspace 'inventory/client455-mesh-runtime-reference.json') -Algorithm SHA256).Hash.ToLowerInvariant() -ne $meshRuntime.reference_report_sha256 -or
    (Get-FileHash -LiteralPath $meshRuntime.matrix_provider.path -Algorithm SHA256).Hash.ToLowerInvariant() -ne $meshRuntime.matrix_provider.sha256) { throw '455 mesh runtime input/provider proof changed.' }
$arguments += '-DRF_CLIENT_455_MESH_RUNTIME=ON'
$arguments += "-DRF_CLIENT_455_MESH_RUNTIME_LIBRARY=$meshRuntimeLibrary"
$texture = Get-Content -LiteralPath (Join-Path $workspace 'inventory/client455-texture-build.json') -Raw | ConvertFrom-Json
$textureGpu = Get-Content -LiteralPath (Join-Path $workspace 'inventory/client455-texture-gpu.json') -Raw | ConvertFrom-Json
$textureLibrary = Join-Path $workspace $texture.library
if ($texture.compile_only -or $textureGpu.native.status -ne 'PASS' -or $textureGpu.native.gpu_texture_pairs -ne 68 -or
    $textureGpu.native.material_parts -ne 97 -or $textureGpu.native.material_texture_bindings -ne 59 -or
    (Get-FileHash -LiteralPath $textureLibrary -Algorithm SHA256).Hash.ToLowerInvariant() -ne $texture.library_sha256 -or
    (Get-FileHash -LiteralPath (Join-Path $workspace 'inventory/client455-texture-build.json') -Algorithm SHA256).Hash.ToLowerInvariant() -ne $textureGpu.build_report_sha256 -or
    (Get-FileHash -LiteralPath (Join-Path $workspace 'inventory/character-texture-inputs.json') -Algorithm SHA256).Hash.ToLowerInvariant() -ne $textureGpu.fixture_manifest_sha256) { throw '455 Character texture component GPU proof missing or stale.' }
foreach ($property in $texture.source_sha256.PSObject.Properties) {
    if ((Get-FileHash -LiteralPath (Join-Path $workspace "scripts/native/$($property.Name)") -Algorithm SHA256).Hash.ToLowerInvariant() -ne $property.Value) { throw '455 Character texture source proof stale.' }
}
$arguments += '-DRF_CLIENT_455_TEXTURE=ON'
$arguments += "-DRF_CLIENT_455_TEXTURE_LIBRARY=$textureLibrary"
$buffers = Get-Content -LiteralPath (Join-Path $workspace 'inventory/client455-shared-buffers-build.json') -Raw | ConvertFrom-Json
$bufferGpu = Get-Content -LiteralPath (Join-Path $workspace 'inventory/client455-shared-buffers-gpu.json') -Raw | ConvertFrom-Json
$bufferLibrary = Join-Path $workspace $buffers.library
if ($bufferGpu.native.status -ne 'PASS' -or $bufferGpu.native.gpu_draws -ne 4 -or $bufferGpu.native.model_parts -ne 393 -or
    $bufferGpu.native.gpu_model_uploads -ne 276 -or
    (Get-FileHash -LiteralPath $bufferLibrary -Algorithm SHA256).Hash.ToLowerInvariant() -ne $buffers.library_sha256 -or
    (Get-FileHash -LiteralPath (Join-Path $workspace 'inventory/client455-shared-buffers-build.json') -Algorithm SHA256).Hash.ToLowerInvariant() -ne $bufferGpu.build_report_sha256) { throw '455 shared buffer native/GPU proof missing or stale.' }
foreach ($property in $buffers.source_sha256.PSObject.Properties) {
    if ((Get-FileHash -LiteralPath (Join-Path $workspace "scripts/native/$($property.Name)") -Algorithm SHA256).Hash.ToLowerInvariant() -ne $property.Value) { throw '455 shared buffer source proof stale.' }
}
$arguments += '-DRF_CLIENT_455_SHARED_BUFFERS=ON'
$arguments += "-DRF_CLIENT_455_SHARED_BUFFERS_LIBRARY=$bufferLibrary"
$models = Get-Content -LiteralPath (Join-Path $workspace 'inventory/client455-models-build.json') -Raw | ConvertFrom-Json
$modelGpu = Get-Content -LiteralPath (Join-Path $workspace 'inventory/client455-models-gpu.json') -Raw | ConvertFrom-Json
$modelLibrary = Join-Path $workspace $models.library
if ($models.compile_only -or $modelGpu.native.status -ne 'PASS' -or $modelGpu.native.model_parts -ne 393 -or
    $modelGpu.native.physical_uploaded_parts -ne 276 -or $modelGpu.native.positive_texture_bindings -ne 59 -or
    (Get-FileHash -LiteralPath $modelLibrary -Algorithm SHA256).Hash.ToLowerInvariant() -ne $models.library_sha256 -or
    (Get-FileHash -LiteralPath (Join-Path $workspace 'inventory/client455-models-build.json') -Algorithm SHA256).Hash.ToLowerInvariant() -ne $modelGpu.build_report_sha256) { throw '455 model lifecycle/pipeline proof missing or stale.' }
foreach ($property in $models.source_sha256.PSObject.Properties) {
    if ((Get-FileHash -LiteralPath (Join-Path $workspace "scripts/native/$($property.Name)") -Algorithm SHA256).Hash.ToLowerInvariant() -ne $property.Value) { throw '455 model source proof stale.' }
}
$arguments += '-DRF_CLIENT_455_MODELS=ON'
$arguments += "-DRF_CLIENT_455_MODELS_LIBRARY=$modelLibrary"
$character455 = Get-Content -LiteralPath (Join-Path $workspace 'inventory/client455-character-manager-build.json') -Raw | ConvertFrom-Json
$character455Gpu = Get-Content -LiteralPath (Join-Path $workspace 'inventory/client455-character-manager-gpu.json') -Raw | ConvertFrom-Json
$character455Library = Join-Path $workspace $character455.library
if ($character455Gpu.native.status -ne 'PASS' -or $character455Gpu.native.ctor_fp_modes -ne 12 -or
    $character455Gpu.native.raw_files -ne 18 -or $character455Gpu.native.model_parts -ne 393 -or
    $character455Gpu.native.physical_parts -ne 276 -or $character455Gpu.native.positive_texture_pointers -ne 59 -or
    (Get-FileHash -LiteralPath $character455Library -Algorithm SHA256).Hash.ToLowerInvariant() -ne $character455.library_sha256 -or
    (Get-FileHash -LiteralPath (Join-Path $workspace 'inventory/client455-character-manager-build.json') -Algorithm SHA256).Hash.ToLowerInvariant() -ne $character455Gpu.build_report_sha256) { throw '455 record/manager proof missing or stale.' }
foreach ($property in $character455.source_sha256.PSObject.Properties) {
    if ((Get-FileHash -LiteralPath (Join-Path $workspace "scripts/native/$($property.Name)") -Algorithm SHA256).Hash.ToLowerInvariant() -ne $property.Value) { throw '455 record/manager source proof stale.' }
}
$arguments += '-DRF_CLIENT_455_CHARACTER_MANAGER=ON'
$arguments += "-DRF_CLIENT_455_CHARACTER_MANAGER_LIBRARY=$character455Library"
$legacyRuntime = Get-Content -LiteralPath (Join-Path $workspace 'inventory/client455-legacy-runtime-build.json') -Raw | ConvertFrom-Json
$legacyRuntimeGpu = Get-Content -LiteralPath (Join-Path $workspace 'inventory/client455-legacy-runtime-gpu.json') -Raw | ConvertFrom-Json
$legacyReader = Get-Content -LiteralPath (Join-Path $workspace 'inventory/client455-legacy-models-build.json') -Raw | ConvertFrom-Json
$legacyRuntimeLibrary = Join-Path $workspace $legacyRuntime.library
$legacyReaderLibrary = Join-Path $workspace $legacyReader.library
if ($legacyRuntime.compile_only -or $legacyRuntimeGpu.native.status -ne 'PASS' -or
    $legacyRuntimeGpu.native.model_runs -ne 34 -or $legacyRuntimeGpu.native.model_parts -ne 972 -or
    $legacyRuntimeGpu.native.physical_indexed_parts -ne 832 -or $legacyRuntimeGpu.native.cpu_retained_parts -ne 2 -or
    $legacyRuntimeGpu.native.paired_files -ne 12 -or $legacyRuntimeGpu.native.paired_physical_parts -ne 276 -or
    (Get-FileHash -LiteralPath $legacyRuntimeLibrary -Algorithm SHA256).Hash.ToLowerInvariant() -ne $legacyRuntime.library_sha256 -or
    (Get-FileHash -LiteralPath $legacyReaderLibrary -Algorithm SHA256).Hash.ToLowerInvariant() -ne $legacyReader.library_sha256 -or
    (Get-FileHash -LiteralPath (Join-Path $workspace 'inventory/client455-legacy-runtime-build.json') -Algorithm SHA256).Hash.ToLowerInvariant() -ne $legacyRuntimeGpu.build_report_sha256) { throw '455 legacy converter runtime proof missing or stale.' }
foreach ($property in $legacyRuntime.source_sha256.PSObject.Properties) {
    if ((Get-FileHash -LiteralPath (Join-Path $workspace "scripts/native/$($property.Name)") -Algorithm SHA256).Hash.ToLowerInvariant() -ne $property.Value) { throw '455 legacy converter source changed since proof.' }
}
$arguments += '-DRF_CLIENT_455_LEGACY_RUNTIME=ON'
$arguments += "-DRF_CLIENT_455_LEGACY_RUNTIME_LIBRARY=$legacyRuntimeLibrary"
$arguments += "-DRF_CLIENT_455_LEGACY_READER_LIBRARY=$legacyReaderLibrary"
$animation = Get-Content -LiteralPath (Join-Path $workspace 'inventory/client455-animation-build.json') -Raw | ConvertFrom-Json
$animationGpu = Get-Content -LiteralPath (Join-Path $workspace 'inventory/client455-animation-gpu.json') -Raw | ConvertFrom-Json
$animationLibrary = Join-Path $workspace $animation.library
if ($animation.compile_only -or $animationGpu.native.status -ne 'PASS' -or
    $animationGpu.native.ani_files -ne 27 -or $animationGpu.native.tracks -ne 1062 -or
    $animationGpu.native.real_ani_matches -ne 22 -or $animationGpu.native.physical_parts -ne 660 -or
    (Get-FileHash -LiteralPath $animationLibrary -Algorithm SHA256).Hash.ToLowerInvariant() -ne $animation.library_sha256 -or
    (Get-FileHash -LiteralPath (Join-Path $workspace 'inventory/client455-animation-build.json') -Algorithm SHA256).Hash.ToLowerInvariant() -ne $animationGpu.build_report_sha256) { throw '455 ANI/dispatcher proof missing or stale.' }
foreach ($property in $animation.source_sha256.PSObject.Properties) {
    if ((Get-FileHash -LiteralPath (Join-Path $workspace "scripts/native/$($property.Name)") -Algorithm SHA256).Hash.ToLowerInvariant() -ne $property.Value) { throw '455 ANI/dispatcher source changed since proof.' }
}
$arguments += '-DRF_CLIENT_455_ANIMATION=ON'
$arguments += "-DRF_CLIENT_455_ANIMATION_LIBRARY=$animationLibrary"
$pose = Get-Content -LiteralPath (Join-Path $workspace 'inventory/client455-pose-build.json') -Raw | ConvertFrom-Json
$poseCpu = Get-Content -LiteralPath (Join-Path $workspace 'inventory/client455-pose-cpu.json') -Raw | ConvertFrom-Json
$poseLibrary = Join-Path $workspace $pose.library
if ($pose.compile_only -or $poseCpu.native.status -ne 'PASS' -or $poseCpu.native.real_pairs -ne 11 -or
    $poseCpu.native.pose_updates -ne 132 -or
    (Get-FileHash -LiteralPath $poseLibrary -Algorithm SHA256).Hash.ToLowerInvariant() -ne $pose.library_sha256 -or
    (Get-FileHash -LiteralPath (Join-Path $workspace 'inventory/client455-pose-build.json') -Algorithm SHA256).Hash.ToLowerInvariant() -ne $poseCpu.build_report_sha256) { throw '455 pose proof missing or stale.' }
foreach ($property in $pose.source_sha256.PSObject.Properties) {
    if ((Get-FileHash -LiteralPath (Join-Path $workspace "scripts/native/$($property.Name)") -Algorithm SHA256).Hash.ToLowerInvariant() -ne $property.Value) { throw '455 pose source changed since proof.' }
}
$arguments += '-DRF_CLIENT_455_POSE=ON'
$arguments += "-DRF_CLIENT_455_POSE_LIBRARY=$poseLibrary"
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
    if ($HelperLab) {
        & (Join-Path $PSScriptRoot 'Invoke-Python.ps1') scripts/verify_client_mesh08.py --lab
    } else {
        & (Join-Path $PSScriptRoot 'Invoke-Python.ps1') scripts/verify_client_mesh08.py
    }
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    if ($HelperLab) {
        & (Join-Path $PSScriptRoot 'Invoke-Python.ps1') scripts/verify_client455_mesh_bindings.py --lab
    } else {
        & (Join-Path $PSScriptRoot 'Invoke-Python.ps1') scripts/verify_client455_mesh_bindings.py
    }
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    if ($HelperLab) {
        & (Join-Path $PSScriptRoot 'Invoke-Python.ps1') scripts/verify_client455_mesh_runtime.py --lab
    } else {
        & (Join-Path $PSScriptRoot 'Invoke-Python.ps1') scripts/verify_client455_mesh_runtime.py
    }
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
Write-Output "Diagnostic RF_Online build exit: $result"
if ($result -eq 0) {
    if ($HelperLab) { & (Join-Path $PSScriptRoot 'Invoke-Python.ps1') scripts/verify_client455_pose.py --lab }
    else { & (Join-Path $PSScriptRoot 'Invoke-Python.ps1') scripts/verify_client455_pose.py }
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
if ($result -eq 0) {
    if ($HelperLab) { & (Join-Path $PSScriptRoot 'Invoke-Python.ps1') scripts/verify_client455_animation.py --lab }
    else { & (Join-Path $PSScriptRoot 'Invoke-Python.ps1') scripts/verify_client455_animation.py }
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
if ($result -eq 0) {
    if ($HelperLab) { & (Join-Path $PSScriptRoot 'Invoke-Python.ps1') scripts/verify_client455_legacy_runtime.py --lab }
    else { & (Join-Path $PSScriptRoot 'Invoke-Python.ps1') scripts/verify_client455_legacy_runtime.py }
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
if ($result -eq 0) {
    if ($HelperLab) { & (Join-Path $PSScriptRoot 'Invoke-Python.ps1') scripts/verify_client455_character_manager.py --lab }
    else { & (Join-Path $PSScriptRoot 'Invoke-Python.ps1') scripts/verify_client455_character_manager.py }
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
if ($result -eq 0) {
    if ($HelperLab) { & (Join-Path $PSScriptRoot 'Invoke-Python.ps1') scripts/verify_client455_models.py --lab }
    else { & (Join-Path $PSScriptRoot 'Invoke-Python.ps1') scripts/verify_client455_models.py }
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
if ($result -eq 0) {
    if ($HelperLab) { & (Join-Path $PSScriptRoot 'Invoke-Python.ps1') scripts/verify_client455_shared_buffers.py --lab }
    else { & (Join-Path $PSScriptRoot 'Invoke-Python.ps1') scripts/verify_client455_shared_buffers.py }
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
if ($result -eq 0) {
    if ($HelperLab) { & (Join-Path $PSScriptRoot 'Invoke-Python.ps1') scripts/verify_client455_texture.py --lab }
    else { & (Join-Path $PSScriptRoot 'Invoke-Python.ps1') scripts/verify_client455_texture.py }
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
exit $result
