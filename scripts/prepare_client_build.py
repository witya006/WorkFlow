"""Stage byte-identical client inputs and generate an explicit R3Engine CMake project.

Existing differing copies are preserved by failing, never overwritten.
"""
import hashlib
import json
import shutil
from pathlib import Path
from audit_build import parse_project, resolve

WS = Path(__file__).resolve().parents[1]


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    paths = json.loads((WS / 'config/paths.json').read_text(encoding='utf-8'))
    original = Path(paths['legacy_source'])
    destination = WS / 'work/client-build'
    engine = original / 'R3Engine/R3Engine'
    client = original / 'RF Client Side/RF_Client'
    manifest = []
    patch_path = WS / 'inventory/client-source-patches.json'
    patches = {x['file']: x for x in json.loads(patch_path.read_text(encoding='utf-8'))} if patch_path.exists() else {}
    for folder, target, exclude in [(engine, destination / 'source/R3Engine', {'Util', 'Client Debug'}),
                                     (client, destination / 'source/RF_Client', set())]:
        for p in sorted(folder.rglob('*')):
            relative = p.relative_to(folder)
            if not p.is_file() or any(x in exclude for x in relative.parts):
                continue
            if p.suffix.lower() in {'.ncb', '.opt', '.plg', '.aps', '.scc', '.obj', '.pch', '.pdb', '.idb'}:
                continue
            copy = target / relative
            expected = digest(p)
            expected_copy = expected
            patch = patches.get(copy.relative_to(WS).as_posix())
            if patch:
                if patch['original_sha256'] != expected:
                    raise RuntimeError(f'Patch input has changed: {p}')
                expected_copy = patch['patched_sha256']
            if copy.exists() and digest(copy) not in {expected, expected_copy}:
                raise RuntimeError(f'Preserving modified work file: {copy}')
            copy.parent.mkdir(parents=True, exist_ok=True)
            if not copy.exists():
                shutil.copyfile(p, copy)
            if digest(copy) not in {expected, expected_copy}:
                raise RuntimeError(f'Copy verification failed: {copy}')
            manifest.append({'original': p.relative_to(original).as_posix(), 'copy': copy.relative_to(WS).as_posix(), 'sha256': expected})
    dsp = engine / 'R3Engine.dsp'
    _, configs, sources, _ = parse_project(dsp)
    selected = 'R3Engine - Win32 RTMovie Release'
    units = []
    for s in sources:
        p = resolve(dsp.parent, s['reference'])
        if p.suffix.lower() in {'.cpp', '.c', '.rc'}:
            units.append(p.relative_to(engine).as_posix())
    cmake = '''cmake_minimum_required(VERSION 3.24)
project(RFClientLegacyPort LANGUAGES CXX RC)
if(NOT MSVC OR NOT CMAKE_SIZEOF_VOID_P EQUAL 4)
  message(FATAL_ERROR "This port baseline requires MSVC with Win32/x86 target")
endif()
set(R3 "${CMAKE_CURRENT_LIST_DIR}/source/R3Engine")
set(RF_LEGACY_DX8_INCLUDE "" CACHE PATH "Directory containing genuine legacy DirectX headers")
add_library(R3Engine STATIC
''' + ''.join(f'  "${{R3}}/{p}"\n' for p in units) + ''')
target_include_directories(R3Engine PRIVATE
  "${R3}" "${R3}/extension" "${R3}/1stclass" "${R3}/2ndclass"
  "${R3}/common" "${R3}/d3d/include")
if(RF_LEGACY_DX8_INCLUDE)
  target_include_directories(R3Engine PRIVATE "${RF_LEGACY_DX8_INCLUDE}")
endif()
target_compile_definitions(R3Engine PRIVATE WIN32 NDEBUG _MBCS _LIB)
target_compile_options(R3Engine PRIVATE "$<$<COMPILE_LANGUAGE:CXX>:/W3>" "$<$<COMPILE_LANGUAGE:CXX>:/EHsc>" "$<$<COMPILE_LANGUAGE:CXX>:/Zc:forScope->")
set_target_properties(R3Engine PROPERTIES
  CXX_STANDARD 14 CXX_STANDARD_REQUIRED YES
  MSVC_RUNTIME_LIBRARY MultiThreadedDLL
  ARCHIVE_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/lib")
# No RTMOVIE definition in the selected original CPP settings.
# /MD is an explicit modern baseline; original configuration has no CRT switch.
# Legacy source charset / execution charset and CRT ABI are still unverified.
# /Zc:forScope- temporarily preserves VC6 loop scope; compiler support tested.

# Build an actual /MT client variant; do not rename the /MD M1 archive.
get_target_property(RF_ENGINE_SOURCES R3Engine SOURCES)
get_target_property(RF_ENGINE_INCLUDES R3Engine INCLUDE_DIRECTORIES)
add_library(R3EngineClientMT STATIC EXCLUDE_FROM_ALL ${RF_ENGINE_SOURCES})
target_include_directories(R3EngineClientMT PRIVATE ${RF_ENGINE_INCLUDES})
target_compile_definitions(R3EngineClientMT PRIVATE WIN32 NDEBUG _MBCS _LIB)
target_link_libraries(R3EngineClientMT PUBLIC "${R3}/mss32.lib")
target_compile_options(R3EngineClientMT PRIVATE "$<$<COMPILE_LANGUAGE:CXX>:/W3>" "$<$<COMPILE_LANGUAGE:CXX>:/EHsc>" "$<$<COMPILE_LANGUAGE:CXX>:/Zc:forScope->" "$<$<COMPILE_LANGUAGE:CXX>:/MP4>")
set_target_properties(R3EngineClientMT PROPERTIES CXX_STANDARD 14 CXX_STANDARD_REQUIRED YES
  MSVC_RUNTIME_LIBRARY MultiThreaded OUTPUT_NAME R3EngineMT
  ARCHIVE_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/lib")
'''
    cmake_path = destination / 'CMakeLists.txt'
    _, _, client_sources, _ = parse_project(client / 'RF_Online.dsp')
    client_units = [resolve(client, s['reference']).relative_to(client).as_posix()
                    for s in client_sources if Path(s['reference']).suffix.lower() in {'.cpp', '.c', '.rc'}]
    cmake += '''
# First real client target: original Release source set; excluded from engine builds.
set(RFC "${CMAKE_CURRENT_LIST_DIR}/source/RF_Client")
set(RF_RECOVERED_CHARACTER_INCLUDE "" CACHE PATH "Incomplete recovered Character header; diagnostic builds only")
set(RF_CHARACTER_STD_DIAGNOSTIC "" CACHE FILEPATH "Separate diagnostic shim for legacy unqualified STL names")
set(RF_LEGACY_DX8_LIBRARY "" CACHE PATH "Genuine DirectX 8 SDK x86 libraries")
set(RF_JPEG_LIBRARY_DIR "" CACHE PATH "Verified JPEG 6b x86 MT archive directory")
set(RF_CHARACTER_REFERENCE_LIBRARY "" CACHE FILEPATH "Unmodified old Character archive for static link diagnostics only")
set(RF_CHARACTER_STDIO_ADAPTER_LIBRARY "" CACHE FILEPATH "Verified isolated classic FILE adapter archive")
set(RF_DIAGNOSTIC_DEFER_LIBRARIES "" CACHE STRING "Unavailable default libraries deferred to expose unresolved symbols; diagnostic only")
option(RF_LEGACY_NEW_UI "Enable UI branch required by current client item classes (present in legacy Debug)" ON)
add_executable(RF_Online WIN32 EXCLUDE_FROM_ALL
''' + ''.join(f'  "${{RFC}}/{p}"\n' for p in client_units) + ''')
target_include_directories(RF_Online PRIVATE
  "${RFC}" "${R3}" "${R3}/extension" "${R3}/1stclass" "${R3}/2ndclass"
  "${R3}/common" "${R3}/d3d/include")
if(RF_RECOVERED_CHARACTER_INCLUDE)
  target_include_directories(RF_Online BEFORE PRIVATE "${RF_RECOVERED_CHARACTER_INCLUDE}")
endif()
if(RF_CHARACTER_STD_DIAGNOSTIC)
  target_compile_options(RF_Online PRIVATE "/FI${RF_CHARACTER_STD_DIAGNOSTIC}" /MP4 /Od)
endif()
if(RF_LEGACY_NEW_UI)
  target_compile_definitions(RF_Online PRIVATE _NEW_UI_)
endif()
if(RF_LEGACY_DX8_INCLUDE)
  target_include_directories(RF_Online PRIVATE "${RF_LEGACY_DX8_INCLUDE}")
endif()
target_compile_definitions(RF_Online PRIVATE WIN32 NDEBUG _WINDOWS _MBCS)
target_compile_options(RF_Online PRIVATE /W3 /EHsc /Zc:forScope-)
target_link_libraries(RF_Online PRIVATE R3EngineClientMT)
target_link_directories(RF_Online PRIVATE "${CMAKE_CURRENT_LIST_DIR}/recovered-imports" "$<TARGET_FILE_DIR:R3EngineClientMT>")
if(RF_LEGACY_DX8_LIBRARY)
  target_link_directories(RF_Online PRIVATE "${RF_LEGACY_DX8_LIBRARY}")
endif()
if(RF_JPEG_LIBRARY_DIR)
  target_link_directories(RF_Online PRIVATE "${RF_JPEG_LIBRARY_DIR}")
endif()
if(RF_CHARACTER_REFERENCE_LIBRARY OR RF_DIAGNOSTIC_DEFER_LIBRARIES)
  if(NOT RF_CHARACTER_STD_DIAGNOSTIC)
    message(FATAL_ERROR "Old Character reference/deferred libraries require the separate diagnostic configuration")
  endif()
  target_link_libraries(RF_Online PRIVATE "${RF_CHARACTER_REFERENCE_LIBRARY}" legacy_stdio_definitions.lib)
  if(RF_CHARACTER_STDIO_ADAPTER_LIBRARY)
    target_link_libraries(RF_Online PRIVATE "${RF_CHARACTER_STDIO_ADAPTER_LIBRARY}")
  endif()
  foreach(RF_DEFERRED_LIB IN LISTS RF_DIAGNOSTIC_DEFER_LIBRARIES)
    target_link_options(RF_Online PRIVATE "/NODEFAULTLIB:${RF_DEFERRED_LIB}")
  endforeach()
endif()
set_target_properties(RF_Online PROPERTIES CXX_STANDARD 14 CXX_STANDARD_REQUIRED YES
  MSVC_RUNTIME_LIBRARY MultiThreaded SUFFIX ".bin")
# Original client /MT retained for diagnosis. CRT alignment and missing legacy
# pragma-linked library variants remain open; no substitution is asserted here.
'''
    if cmake_path.exists() and cmake_path.read_text(encoding='utf-8') != cmake:
        previous_path = WS / 'inventory/client-build-inputs.json'
        previous = json.loads(previous_path.read_text(encoding='utf-8')) if previous_path.exists() else {}
        if digest(cmake_path) != previous.get('cmake_sha256'):
            raise RuntimeError(f'Preserving modified build project: {cmake_path}')
    if not cmake_path.exists() or cmake_path.read_text(encoding='utf-8') != cmake:
        cmake_path.write_text(cmake, encoding='utf-8')
    report = {'scope': 'Client and R3Engine only. No server files copied or changed.',
              'selected_legacy_config': selected, 'legacy_cpp_directives': configs[selected],
              'translation_units': len([x for x in units if x.lower().endswith(('.cpp', '.c'))]),
              'resource_units': len([x for x in units if x.lower().endswith('.rc')]),
              'cmake_sha256': digest(cmake_path), 'files': manifest}
    (WS / 'inventory/client-build-inputs.json').write_text(json.dumps(report, ensure_ascii=True, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'staged_files': len(manifest), 'cpp': report['translation_units'], 'rc': report['resource_units'], 'project': str(cmake_path)}))


if __name__ == '__main__':
    main()
