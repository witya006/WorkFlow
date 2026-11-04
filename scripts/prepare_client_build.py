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
            if copy.exists() and digest(copy) != expected:
                raise RuntimeError(f'Preserving modified work file: {copy}')
            copy.parent.mkdir(parents=True, exist_ok=True)
            if not copy.exists():
                shutil.copyfile(p, copy)
            if digest(copy) != expected:
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
target_compile_options(R3Engine PRIVATE "$<$<COMPILE_LANGUAGE:CXX>:/W3>" "$<$<COMPILE_LANGUAGE:CXX>:/EHsc>")
set_target_properties(R3Engine PROPERTIES
  CXX_STANDARD 14 CXX_STANDARD_REQUIRED YES
  MSVC_RUNTIME_LIBRARY MultiThreadedDLL
  ARCHIVE_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/lib")
# No RTMOVIE definition in the selected original CPP settings.
# /MD is an explicit modern baseline; original configuration has no CRT switch.
# Legacy source charset / execution charset and CRT ABI are still unverified.
'''
    cmake_path = destination / 'CMakeLists.txt'
    if cmake_path.exists() and cmake_path.read_text(encoding='utf-8') != cmake:
        raise RuntimeError(f'Preserving modified build project: {cmake_path}')
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
