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
    behavior_path = WS/'inventory/client-behavior-patches.json'
    behaviors = {x['file']:x for x in json.loads(behavior_path.read_text(encoding='utf-8'))} if behavior_path.exists() else {}
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
            accepted = {expected,expected_copy}
            behavior = behaviors.get(copy.relative_to(WS).as_posix())
            if behavior:
                if behavior['original_sha256'] != expected or behavior['input_sha256'] != expected_copy:
                    raise RuntimeError(f'Behavior patch input has changed: {p}')
                accepted.add(behavior['patched_sha256'])
            if copy.exists() and digest(copy) not in accepted:
                raise RuntimeError(f'Preserving modified work file: {copy}')
            copy.parent.mkdir(parents=True, exist_ok=True)
            if not copy.exists():
                shutil.copyfile(p, copy)
            if digest(copy) not in accepted:
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
option(RF_CLIENT_455_HELPER_LOADER "Select verified 455 helper-loader behavior" OFF)
option(RF_CLIENT_455_WEATHER "Restore two-layer weather and helper interior integration" OFF)
option(RF_CLIENT_455_CLOCK "Restore exact x87 day and real-time clock arithmetic" OFF)
option(RF_CLIENT_455_TIME_COMMANDS "Restore grade-gated local time text commands" OFF)
if(RF_CLIENT_455_TIME_COMMANDS)
  if(NOT RF_CLIENT_455_CLOCK)
    message(FATAL_ERROR "Time commands require restored clock routines")
  endif()
  target_sources(R3EngineClientMT PRIVATE "${CMAKE_CURRENT_LIST_DIR}/../../scripts/native/client455_time_commands.cpp")
  target_compile_definitions(R3EngineClientMT PUBLIC RF_CLIENT_455_TIME_COMMANDS)
endif()
option(RF_CLIENT_455_MAP_TIME "Restore map packet/cache and successful-load clock setup" OFF)
if(RF_CLIENT_455_MAP_TIME)
  if(NOT RF_CLIENT_455_CLOCK)
    message(FATAL_ERROR "Map time requires restored clock routines")
  endif()
  target_sources(R3EngineClientMT PRIVATE "${CMAKE_CURRENT_LIST_DIR}/../../scripts/native/client455_map_time.cpp")
  target_compile_definitions(R3EngineClientMT PUBLIC RF_CLIENT_455_MAP_TIME)
endif()
if(RF_CLIENT_455_CLOCK)
  if(NOT RF_CLIENT_455_WEATHER)
    message(FATAL_ERROR "Clock restoration currently requires the weather frame hook")
  endif()
  target_sources(R3EngineClientMT PRIVATE "${CMAKE_CURRENT_LIST_DIR}/../../scripts/native/client455_clock.cpp")
  target_include_directories(R3EngineClientMT PUBLIC "${CMAKE_CURRENT_LIST_DIR}/../../scripts/native")
  target_compile_definitions(R3EngineClientMT PUBLIC RF_CLIENT_455_CLOCK)
endif()
option(RF_CLIENT_455_RESOURCE_IO "Restore RPK resource opens, group lifecycle and SPT end boundaries" OFF)
if(RF_CLIENT_455_RESOURCE_IO)
  target_sources(R3EngineClientMT PRIVATE "${CMAKE_CURRENT_LIST_DIR}/../../scripts/native/client455_resource_io.cpp")
  target_include_directories(R3EngineClientMT PUBLIC "${CMAKE_CURRENT_LIST_DIR}/../../scripts/native")
  target_compile_definitions(R3EngineClientMT PUBLIC RF_CLIENT_455_RESOURCE_IO)
endif()
if(RF_CLIENT_455_WEATHER)
  target_sources(R3EngineClientMT PRIVATE "${CMAKE_CURRENT_LIST_DIR}/../../scripts/native/client455_weather.cpp")
  target_include_directories(R3EngineClientMT PUBLIC "${CMAKE_CURRENT_LIST_DIR}/../../scripts/native")
  target_compile_definitions(R3EngineClientMT PUBLIC RF_CLIENT_455_WEATHER)
endif()
if(RF_CLIENT_455_HELPER_LOADER)
  target_compile_definitions(R3EngineClientMT PUBLIC RF_CLIENT_455_HELPER_LOADER)
endif()
option(RF_CLIENT_455_X87_MATH "Preserve verified 455 x87 math instructions" OFF)
set(RF_CLIENT_455_X87_MATH_LIBRARY "" CACHE FILEPATH "Verified x86 MT compatibility math archive")
if(RF_CLIENT_455_X87_MATH)
  if(NOT EXISTS "${RF_CLIENT_455_X87_MATH_LIBRARY}")
    message(FATAL_ERROR "455 x87 math requires its instruction-verified archive")
  endif()
  get_filename_component(RF_X87_INCLUDE "${RF_CLIENT_455_X87_MATH_LIBRARY}" DIRECTORY)
  target_include_directories(R3EngineClientMT PRIVATE "${RF_X87_INCLUDE}")
  target_compile_definitions(R3EngineClientMT PUBLIC RF_CLIENT_455_X87_MATH)
  target_link_libraries(R3EngineClientMT PUBLIC "${RF_CLIENT_455_X87_MATH_LIBRARY}")
endif()
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
set(RF_CHARACTER_RECOVERED_MANAGERS_LIBRARY "" CACHE FILEPATH "Verified recovered manager constructor archive")
set(RF_CHARACTER_EXCEPTIONS_LIBRARY "" CACHE FILEPATH "Verified reconstructed legacy string exception helpers")
set(RF_CHARACTER_SETTERS_LIBRARY "" CACHE FILEPATH "Verified recovered texture path/detail setters")
option(RF_CHARACTER_MESH_SOURCE "Use verified own legacy mesh CPU bindings" OFF)
set(RF_CHARACTER_MESH_SOURCE_LIBRARY "" CACHE FILEPATH "Verified recovered mesh CPU binding archive")
option(RF_CLIENT_455_MESH08 "Build455MESH08format reader;full runtime renderer integration separate" OFF)
set(RF_CLIENT_455_MESH08_LIBRARY "" CACHE FILEPATH "Verified source MESH08reader/writer archive")
option(RF_CLIENT_455_MESH_BINDINGS "Build455packed CPU bindings;full runtime model loader separate" OFF)
set(RF_CLIENT_455_MESH_BINDINGS_LIBRARY "" CACHE FILEPATH "Verified source455mesh parent/bone bindings")
option(RF_CLIENT_455_MESH_RUNTIME "Build455mesh header/material CPU kernels;normal loader separate" OFF)
set(RF_CLIENT_455_MESH_RUNTIME_LIBRARY "" CACHE FILEPATH "Verified source455mesh construction/header/material requests")
option(RF_CLIENT_455_TEXTURE "Build source455Character RFS/DDS/D3D9texture backend;normal loader separate" OFF)
set(RF_CLIENT_455_TEXTURE_LIBRARY "" CACHE FILEPATH "Verified source455Character texture backend")
option(RF_CLIENT_455_SHARED_BUFFERS "Build source455Character shared GPU buffers;normal loader separate" OFF)
set(RF_CLIENT_455_SHARED_BUFFERS_LIBRARY "" CACHE FILEPATH "Verified source455Character shared GPU buffers")
option(RF_CLIENT_455_MODELS "Build source455 mesh lifetime/MESH08model pipeline;normal dispatch separate" OFF)
set(RF_CLIENT_455_MODELS_LIBRARY "" CACHE FILEPATH "Verified source455model lifecycle/MESH08pipeline")
option(RF_CLIENT_455_CHARACTER_MANAGER "Build source455 record/manager/cache/raw-MSH route;normal dispatch separate" OFF)
set(RF_CLIENT_455_CHARACTER_MANAGER_LIBRARY "" CACHE FILEPATH "Verified source455 Character record/manager archive")
option(RF_CLIENT_455_LEGACY_RUNTIME "Build source455 legacy MSH/BN converter/IO;normal dispatcher separate" OFF)
option(RF_CLIENT_455_ANIMATION "Build source455 ANI/character dispatcher;normal consumers separate" OFF)
set(RF_CLIENT_455_ANIMATION_LIBRARY "" CACHE FILEPATH "Verified source455 ANI/dispatcher")
option(RF_CLIENT_455_POSE "Build source455 pose phases;secondary/normal consumers separate" OFF)
set(RF_CLIENT_455_POSE_LIBRARY "" CACHE FILEPATH "Verified source455 pose")
set(RF_CLIENT_455_LEGACY_RUNTIME_LIBRARY "" CACHE FILEPATH "Verified source455 legacy model runtime")
set(RF_CLIENT_455_LEGACY_READER_LIBRARY "" CACHE FILEPATH "Verified source455 intermediate legacy reader")
set(RF_CLIENT_455_EFFECT_LOG_LIBRARY "" CACHE FILEPATH "Verified reconstructed 455 effect logger")
set(RF_DIAGNOSTIC_DEFER_LIBRARIES "" CACHE STRING "Unavailable default libraries deferred to expose unresolved symbols; diagnostic only")
option(RF_LEGACY_NEW_UI "Enable UI branch required by current client item classes (present in legacy Debug)" ON)
option(RF_CLIENT_455_DRAW_ARGUMENTS "Use verified 455 scale/scroll arguments at selected client draw sites" OFF)
option(RF_CLIENT_455_EFFECT_LOG "Use reconstructed 455 effect-log behavior; preserve legacy branch otherwise" OFF)
option(RF_CLIENT_455_LOBBY_TRANSITION "Use confirmed 455 connection-success to lobby transition" OFF)
add_executable(RF_Online WIN32 EXCLUDE_FROM_ALL
''' + ''.join(f'  "${{RFC}}/{p}"\n' for p in client_units) + ''')
target_include_directories(RF_Online PRIVATE
  "${RFC}" "${R3}" "${R3}/extension" "${R3}/1stclass" "${R3}/2ndclass"
  "${R3}/common" "${R3}/d3d/include")
option(RF_CLIENT_HELPER_LAB "Diagnostic helper-only entry in the full client; no normal game startup" OFF)
if(RF_CLIENT_HELPER_LAB)
  target_sources(RF_Online PRIVATE "${CMAKE_CURRENT_LIST_DIR}/../../scripts/native/client_helper_lab.cpp")
  target_compile_definitions(RF_Online PRIVATE WinMain=RFOriginalWinMain RF_CLIENT_HELPER_LAB)
  target_link_options(RF_Online PRIVATE "/INCLUDE:_RFOriginalWinMain@16")
  # Original game DLL code is not needed by this CPU-only diagnostic entry.
  target_link_libraries(RF_Online PRIVATE delayimp.lib)
  foreach(RF_LAB_DELAY_DLL IN ITEMS mss32.dll ABuse.dll Adv.dll PDLL.dll)
    target_link_options(RF_Online PRIVATE "/DELAYLOAD:${RF_LAB_DELAY_DLL}")
  endforeach()
endif()
if(RF_CLIENT_455_X87_MATH)
  target_link_options(RF_Online PRIVATE "/MAP:${CMAKE_BINARY_DIR}/RF_Online-$<CONFIG>.map")
endif()
if(RF_RECOVERED_CHARACTER_INCLUDE)
  target_include_directories(RF_Online BEFORE PRIVATE "${RF_RECOVERED_CHARACTER_INCLUDE}")
endif()
if(RF_CHARACTER_STD_DIAGNOSTIC)
  target_compile_options(RF_Online PRIVATE "/FI${RF_CHARACTER_STD_DIAGNOSTIC}" /MP4 /Od)
endif()
if(RF_LEGACY_NEW_UI)
  target_compile_definitions(RF_Online PRIVATE _NEW_UI_)
endif()
if(RF_CLIENT_455_DRAW_ARGUMENTS)
  target_compile_definitions(RF_Online PRIVATE RF_CLIENT_455_DRAW_ARGUMENTS)
endif()
if(RF_CLIENT_455_EFFECT_LOG)
  if(NOT EXISTS "${RF_CLIENT_455_EFFECT_LOG_LIBRARY}")
    message(FATAL_ERROR "455 effect logging requires the verified implementation library")
  endif()
  target_compile_definitions(RF_Online PRIVATE RF_CLIENT_455_EFFECT_LOG)
  target_link_libraries(RF_Online PRIVATE "${RF_CLIENT_455_EFFECT_LOG_LIBRARY}")
endif()
if(RF_CLIENT_455_LOBBY_TRANSITION)
  target_compile_definitions(RF_Online PRIVATE RF_CLIENT_455_LOBBY_TRANSITION)
endif()
if(RF_LEGACY_DX8_INCLUDE)
  target_include_directories(RF_Online PRIVATE "${RF_LEGACY_DX8_INCLUDE}")
endif()
target_compile_definitions(RF_Online PRIVATE WIN32 NDEBUG _WINDOWS _MBCS)
target_compile_options(RF_Online PRIVATE /W3 /EHsc /Zc:forScope-)
target_link_libraries(RF_Online PRIVATE R3EngineClientMT)
if(RF_CLIENT_455_MESH08)
  if(NOT EXISTS "${RF_CLIENT_455_MESH08_LIBRARY}")
    message(FATAL_ERROR "MESH08 format support requires the verified source archive")
  endif()
  target_link_libraries(RF_Online PRIVATE "${RF_CLIENT_455_MESH08_LIBRARY}")
  target_compile_definitions(RF_Online PRIVATE RF_CLIENT_455_MESH08)
endif()
if(RF_CLIENT_455_MESH_BINDINGS)
  if(NOT RF_CLIENT_455_MESH08 OR NOT EXISTS "${RF_CLIENT_455_MESH_BINDINGS_LIBRARY}")
    message(FATAL_ERROR "455 mesh bindings require MESH08 and the verified source archive")
  endif()
  target_link_libraries(RF_Online PRIVATE "${RF_CLIENT_455_MESH_BINDINGS_LIBRARY}")
  if(RF_CLIENT_HELPER_LAB)
    set_property(SOURCE "${CMAKE_CURRENT_LIST_DIR}/../../scripts/native/client_helper_lab.cpp"
      APPEND PROPERTY COMPILE_DEFINITIONS RF_CLIENT_455_MESH_BINDINGS)
  endif()
endif()
if(RF_CLIENT_455_MESH_RUNTIME)
  if(NOT RF_CLIENT_455_MESH08 OR NOT EXISTS "${RF_CLIENT_455_MESH_RUNTIME_LIBRARY}")
    message(FATAL_ERROR "455 mesh runtime kernels require MESH08 and the verified source archive")
  endif()
  target_link_libraries(RF_Online PRIVATE "${RF_CLIENT_455_MESH_RUNTIME_LIBRARY}")
  if(RF_CLIENT_HELPER_LAB)
    set_property(SOURCE "${CMAKE_CURRENT_LIST_DIR}/../../scripts/native/client_helper_lab.cpp"
      APPEND PROPERTY COMPILE_DEFINITIONS RF_CLIENT_455_MESH_RUNTIME)
  endif()
endif()
target_link_directories(RF_Online PRIVATE "${CMAKE_CURRENT_LIST_DIR}/recovered-imports" "$<TARGET_FILE_DIR:R3EngineClientMT>")
if(RF_CLIENT_455_TEXTURE)
  if(NOT RF_CLIENT_455_MESH_RUNTIME OR NOT EXISTS "${RF_CLIENT_455_TEXTURE_LIBRARY}")
    message(FATAL_ERROR "Character texture backend requires source mesh runtime and verified texture library")
  endif()
  target_link_libraries(RF_Online PRIVATE "${RF_CLIENT_455_TEXTURE_LIBRARY}")
  if(RF_CLIENT_HELPER_LAB)
    target_sources(RF_Online PRIVATE "${CMAKE_CURRENT_LIST_DIR}/../../scripts/native/test_client455_texture.cpp")
    set_property(SOURCE "${CMAKE_CURRENT_LIST_DIR}/../../scripts/native/test_client455_texture.cpp"
      APPEND PROPERTY COMPILE_DEFINITIONS RF455_TEXTURE_EMBEDDED)
    set_property(SOURCE "${CMAKE_CURRENT_LIST_DIR}/../../scripts/native/client_helper_lab.cpp"
      APPEND PROPERTY COMPILE_DEFINITIONS RF_CLIENT_455_TEXTURE)
  endif()
endif()
if(RF_LEGACY_DX8_LIBRARY)
  target_link_directories(RF_Online PRIVATE "${RF_LEGACY_DX8_LIBRARY}")
endif()
if(RF_CLIENT_455_SHARED_BUFFERS)
  if(NOT RF_CLIENT_455_MESH_RUNTIME OR NOT EXISTS "${RF_CLIENT_455_SHARED_BUFFERS_LIBRARY}")
    message(FATAL_ERROR "Shared Character buffers require source mesh runtime and verified archive")
  endif()
  target_link_libraries(RF_Online PRIVATE "${RF_CLIENT_455_SHARED_BUFFERS_LIBRARY}")
  if(RF_CLIENT_HELPER_LAB)
    target_sources(RF_Online PRIVATE "${CMAKE_CURRENT_LIST_DIR}/../../scripts/native/test_client455_shared_buffers.cpp")
    set_property(SOURCE "${CMAKE_CURRENT_LIST_DIR}/../../scripts/native/test_client455_shared_buffers.cpp"
      APPEND PROPERTY COMPILE_DEFINITIONS RF455_SHARED_BUFFERS_EMBEDDED)
    set_property(SOURCE "${CMAKE_CURRENT_LIST_DIR}/../../scripts/native/client_helper_lab.cpp"
      APPEND PROPERTY COMPILE_DEFINITIONS RF_CLIENT_455_SHARED_BUFFERS)
  endif()
endif()
if(RF_JPEG_LIBRARY_DIR)
  target_link_directories(RF_Online PRIVATE "${RF_JPEG_LIBRARY_DIR}")
endif()
if(RF_CLIENT_455_MODELS)
  if(NOT RF_CLIENT_455_TEXTURE OR NOT RF_CLIENT_455_SHARED_BUFFERS OR NOT RF_CLIENT_455_MESH_BINDINGS OR NOT EXISTS "${RF_CLIENT_455_MODELS_LIBRARY}")
    message(FATAL_ERROR "MESH08 model pipeline requires texture/shared buffers/bindings and verified models archive")
  endif()
  target_link_libraries(RF_Online PRIVATE "${RF_CLIENT_455_MODELS_LIBRARY}")
  if(RF_CLIENT_HELPER_LAB)
    target_sources(RF_Online PRIVATE "${CMAKE_CURRENT_LIST_DIR}/../../scripts/native/test_client455_models.cpp")
    set_property(SOURCE "${CMAKE_CURRENT_LIST_DIR}/../../scripts/native/test_client455_models.cpp"
      APPEND PROPERTY COMPILE_DEFINITIONS RF455_MODELS_EMBEDDED)
    set_property(SOURCE "${CMAKE_CURRENT_LIST_DIR}/../../scripts/native/client_helper_lab.cpp"
      APPEND PROPERTY COMPILE_DEFINITIONS RF_CLIENT_455_MODELS)
  endif()
endif()
if(RF_CLIENT_455_CHARACTER_MANAGER)
  if(NOT RF_CLIENT_455_MODELS OR NOT EXISTS "${RF_CLIENT_455_CHARACTER_MANAGER_LIBRARY}")
    message(FATAL_ERROR "Character455 manager requires verified models and manager archives")
  endif()
  target_link_libraries(RF_Online PRIVATE "${RF_CLIENT_455_CHARACTER_MANAGER_LIBRARY}")
  if(RF_CLIENT_HELPER_LAB)
    target_sources(RF_Online PRIVATE "${CMAKE_CURRENT_LIST_DIR}/../../scripts/native/test_client455_character_manager.cpp")
    set_property(SOURCE "${CMAKE_CURRENT_LIST_DIR}/../../scripts/native/test_client455_character_manager.cpp"
      APPEND PROPERTY COMPILE_DEFINITIONS RF455_CHARACTER_MANAGER_EMBEDDED)
    set_property(SOURCE "${CMAKE_CURRENT_LIST_DIR}/../../scripts/native/client_helper_lab.cpp"
      APPEND PROPERTY COMPILE_DEFINITIONS RF_CLIENT_455_CHARACTER_MANAGER)
  endif()
endif()
if(RF_CLIENT_455_LEGACY_RUNTIME)
  if(NOT RF_CLIENT_455_CHARACTER_MANAGER OR NOT RF_CLIENT_455_MODELS OR NOT EXISTS "${RF_CLIENT_455_LEGACY_RUNTIME_LIBRARY}" OR NOT EXISTS "${RF_CLIENT_455_LEGACY_READER_LIBRARY}")
    message(FATAL_ERROR "Legacy455 runtime requires verified manager/models/runtime/reader archives")
  endif()
  target_link_libraries(RF_Online PRIVATE "${RF_CLIENT_455_LEGACY_RUNTIME_LIBRARY}" "${RF_CLIENT_455_LEGACY_READER_LIBRARY}")
  if(RF_CLIENT_HELPER_LAB)
    target_sources(RF_Online PRIVATE "${CMAKE_CURRENT_LIST_DIR}/../../scripts/native/test_client455_legacy_runtime.cpp")
    set_property(SOURCE "${CMAKE_CURRENT_LIST_DIR}/../../scripts/native/test_client455_legacy_runtime.cpp"
      APPEND PROPERTY COMPILE_DEFINITIONS RF455_LEGACY_RUNTIME_EMBEDDED)
    set_property(SOURCE "${CMAKE_CURRENT_LIST_DIR}/../../scripts/native/client_helper_lab.cpp"
      APPEND PROPERTY COMPILE_DEFINITIONS RF_CLIENT_455_LEGACY_RUNTIME)
  endif()
endif()
if(RF_CLIENT_455_ANIMATION)
  if(NOT RF_CLIENT_455_LEGACY_RUNTIME OR NOT RF_CLIENT_455_CHARACTER_MANAGER OR NOT EXISTS "${RF_CLIENT_455_ANIMATION_LIBRARY}")
    message(FATAL_ERROR "ANI455 requires verified manager/legacy runtime/animation archives")
  endif()
  target_link_libraries(RF_Online PRIVATE "${RF_CLIENT_455_ANIMATION_LIBRARY}")
  if(RF_CLIENT_HELPER_LAB)
    target_sources(RF_Online PRIVATE "${CMAKE_CURRENT_LIST_DIR}/../../scripts/native/test_client455_animation.cpp")
    set_property(SOURCE "${CMAKE_CURRENT_LIST_DIR}/../../scripts/native/test_client455_animation.cpp"
      APPEND PROPERTY COMPILE_DEFINITIONS RF455_ANIMATION_EMBEDDED)
    set_property(SOURCE "${CMAKE_CURRENT_LIST_DIR}/../../scripts/native/client_helper_lab.cpp"
      APPEND PROPERTY COMPILE_DEFINITIONS RF_CLIENT_455_ANIMATION)
  endif()
endif()
if(RF_CLIENT_455_POSE)
  if(NOT RF_CLIENT_455_ANIMATION OR NOT EXISTS "${RF_CLIENT_455_POSE_LIBRARY}")
    message(FATAL_ERROR "Pose455 requires verified animation and pose archives")
  endif()
  target_link_libraries(RF_Online PRIVATE "${RF_CLIENT_455_POSE_LIBRARY}")
  if(RF_CLIENT_HELPER_LAB)
    target_sources(RF_Online PRIVATE "${CMAKE_CURRENT_LIST_DIR}/../../scripts/native/test_client455_pose.cpp")
    set_property(SOURCE "${CMAKE_CURRENT_LIST_DIR}/../../scripts/native/test_client455_pose.cpp"
      APPEND PROPERTY COMPILE_DEFINITIONS RF455_POSE_EMBEDDED)
    target_sources(RF_Online PRIVATE "${CMAKE_CURRENT_LIST_DIR}/../../scripts/native/test_client455_secondary.cpp")
    set_property(SOURCE "${CMAKE_CURRENT_LIST_DIR}/../../scripts/native/test_client455_secondary.cpp"
      APPEND PROPERTY COMPILE_DEFINITIONS RF455_SECONDARY_EMBEDDED)
    set_property(SOURCE "${CMAKE_CURRENT_LIST_DIR}/../../scripts/native/client_helper_lab.cpp"
      APPEND PROPERTY COMPILE_DEFINITIONS RF_CLIENT_455_POSE)
  endif()
endif()
if(RF_CHARACTER_REFERENCE_LIBRARY OR RF_DIAGNOSTIC_DEFER_LIBRARIES)
  if(NOT RF_CHARACTER_STD_DIAGNOSTIC)
    message(FATAL_ERROR "Old Character reference/deferred libraries require the separate diagnostic configuration")
  endif()
  target_link_libraries(RF_Online PRIVATE "${RF_CHARACTER_REFERENCE_LIBRARY}" legacy_stdio_definitions.lib)
  if(RF_CHARACTER_MESH_SOURCE)
    if(NOT EXISTS "${RF_CHARACTER_MESH_SOURCE_LIBRARY}")
      message(FATAL_ERROR "Source mesh bindings require the verified implementation archive")
    endif()
    target_link_libraries(RF_Online PRIVATE "${RF_CHARACTER_MESH_SOURCE_LIBRARY}")
    target_compile_definitions(RF_Online PRIVATE RF_CHARACTER_MESH_SOURCE)
  endif()
  if(RF_CHARACTER_STDIO_ADAPTER_LIBRARY)
    target_link_libraries(RF_Online PRIVATE "${RF_CHARACTER_STDIO_ADAPTER_LIBRARY}")
  endif()
  if(RF_CHARACTER_RECOVERED_MANAGERS_LIBRARY)
    target_link_libraries(RF_Online PRIVATE "${RF_CHARACTER_RECOVERED_MANAGERS_LIBRARY}")
  endif()
  if(RF_CHARACTER_EXCEPTIONS_LIBRARY)
    target_link_libraries(RF_Online PRIVATE "${RF_CHARACTER_EXCEPTIONS_LIBRARY}")
  endif()
  if(RF_CHARACTER_SETTERS_LIBRARY)
    target_link_libraries(RF_Online PRIVATE "${RF_CHARACTER_SETTERS_LIBRARY}")
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
