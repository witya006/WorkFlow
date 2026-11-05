"""Extract a compact client compilation status, without committing raw logs."""
import argparse
import collections
import json
import re
import hashlib
from datetime import datetime, timezone
from pathlib import Path

WS = Path(__file__).resolve().parents[1]


def unresolved_symbol(message):
    prefix = re.split(r' в функции | referenced in function | in function ', message, maxsplit=1)[0]
    decorated = re.search(r'\((\?[^ )]+)\)', prefix)
    if decorated:
        return decorated[1]
    raw = re.search(r'(?<!\w)(_[A-Za-z_][A-Za-z0-9_@]*)(?=[\s.,"()]|$)', prefix)
    return raw[1] if raw else None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--build-exit', required=True, type=int)
    parser.add_argument('--log', default='artifacts/client-executable-build/build.txt')
    parser.add_argument('--build-dir', default='work/client-build/build-vs2026')
    parser.add_argument('--output', default='inventory/client-executable-build-result.json')
    parser.add_argument('--max-details', type=int, default=200)
    args = parser.parse_args()
    log = (WS / args.log).read_text(encoding='utf-8-sig', errors='replace')
    errors = []
    for line in log.splitlines():
        m = re.match(r'(.*?)\((\d+),(\d+)\): (?:fatal )?error ([A-Z]+\d+): (.*?) \[', line)
        if not m:
            link = re.match(r'(.*?): (?:fatal )?error (LNK\d+): (.*?) \[', line)
            if link:
                errors.append({'file': link[1], 'line': None, 'code': link[2], 'message': link[3]})
            continue
        p = Path(m[1])
        try:
            name = p.relative_to(WS).as_posix()
        except ValueError:
            name = str(p)
        errors.append({'file': name, 'line': int(m[2]), 'code': m[4], 'message': m[5]})
    groups = collections.Counter((x['file'], x['line'], x['code'], x['message']) for x in errors)
    cache = WS / args.build_dir / 'CMakeCache.txt'
    settings = {}
    if cache.exists():
        for line in cache.read_text(encoding='utf-8').splitlines():
            m = re.match(r'(RF_(?:RECOVERED_CHARACTER_INCLUDE|CHARACTER_STD_DIAGNOSTIC|LEGACY_NEW_UI|LEGACY_DX8_LIBRARY|JPEG_LIBRARY_DIR|CHARACTER_REFERENCE_LIBRARY|CHARACTER_STDIO_ADAPTER_LIBRARY|CHARACTER_RECOVERED_MANAGERS_LIBRARY|CHARACTER_EXCEPTIONS_LIBRARY|CHARACTER_SETTERS_LIBRARY|CLIENT_455_DRAW_ARGUMENTS|CLIENT_455_EFFECT_LOG|CLIENT_455_EFFECT_LOG_LIBRARY|CLIENT_455_LOBBY_TRANSITION|DIAGNOSTIC_DEFER_LIBRARIES)):[^=]+=(.*)', line)
            if m:
                settings[m[1]] = m[2]
    if cache.exists():
        for line in cache.read_text(encoding='utf-8').splitlines():
            m = re.match(r'(RF_CLIENT_(?:455_HELPER_LOADER|HELPER_LAB|455_X87_MATH|455_X87_MATH_LIBRARY|455_WEATHER|455_RESOURCE_IO|455_CLOCK|455_MAP_TIME|455_TIME_COMMANDS|455_ANIMATION_TIMING|455_LOOP_CLOCK|455_FRUSTUM)):[^=]+=(.*)',line)
            if m:
                settings[m[1]] = m[2]
    if cache.exists():
        for line in cache.read_text(encoding='utf-8').splitlines():
            m=re.match(r'(RF_CHARACTER_MESH_SOURCE(?:_LIBRARY)?):[^=]+=(.*)',line)
            if m:settings[m[1]]=m[2]
    if cache.exists():
        for line in cache.read_text(encoding='utf-8').splitlines():
            m=re.match(r'(RF_CLIENT_455_(?:MESH08|MESH_BINDINGS|MESH_RUNTIME|TEXTURE|SHARED_BUFFERS|MODELS|CHARACTER_MANAGER|CHARACTER_DRAW|LEGACY_RUNTIME|LEGACY_READER|ANIMATION|ANIMATION_MANAGER|SHADERS|DRAW|POSE)(?:_LIBRARY)?):[^=]+=(.*)',line)
            if m:settings[m[1]]=m[2]
    report = {'checked_at_utc': datetime.now(timezone.utc).isoformat(), 'target': 'RF_Online',
              'platform': 'Win32', 'configuration': 'Release', 'build_exit': args.build_exit,
              'error_counts': dict(collections.Counter(x['code'] for x in errors)),
              'unresolved_symbols': sorted({symbol for x in errors if x['code'] in {'LNK2001', 'LNK2019'}
                                             if (symbol := unresolved_symbol(x['message']))}),
              'distinct_diagnostics_total': len(groups),
              'distinct_diagnostics': [dict(zip(['file', 'line', 'code', 'message', 'count'], [*key, count])) for key, count in list(groups.items())[:args.max_details]],
              'details_omitted': max(0, len(groups)-args.max_details),
              'generated_objects': len(list((WS / args.build_dir / 'RF_Online.dir/Release').glob('*.obj'))),
              'build_dir': args.build_dir, 'log': args.log,
              'build_settings': settings,
              'scope': 'Client-only compile diagnostic. No input EXE execution; compilation does not prove behavior.'}
    if cache.exists():
        report['compiler_flags']={match[1]:match[2] for line in cache.read_text(encoding='utf-8').splitlines()
            if (match:=re.match(r'(CMAKE_CXX_FLAGS(?:_RELEASE)?):STRING=(.*)',line))}
    if settings.get('RF_CLIENT_HELPER_LAB')=='ON' and args.build_exit==0:
        inputs=['scripts/native/client_helper_lab.cpp',
                'work/client-build/source/R3Engine/2ndclass/extdummy.cpp',
                'work/client-build/source/R3Engine/2ndclass/extdummy.h',
                args.build_dir+'/Release/RF_Online.bin']
        report['lab_input_sha256']={p:hashlib.sha256((WS/p).read_bytes()).hexdigest() for p in inputs}
        if settings.get('RF_CLIENT_455_FRUSTUM')=='ON':
            frustum_inputs=['scripts/native/'+p for p in ['client455_frustum.h','client455_frustum.cpp','client455_frustum_system.cpp','test_client455_frustum.cpp','client_frustum_lab.inc']]+['work/client-build/source/RF_Client/global.cpp','work/client-build/source/RF_Client/cresobject.cpp']
            report['frustum_input_sha256']={p:hashlib.sha256((WS/p).read_bytes()).hexdigest() for p in frustum_inputs}
        if settings.get('RF_CLIENT_455_DRAW')=='ON':
            draw_inputs=['scripts/native/'+p for p in ['client455_draw.cpp','client455_draw.h','test_client455_draw.cpp','client_draw_lab.inc']]
            report['draw_input_sha256']={p:hashlib.sha256((WS/p).read_bytes()).hexdigest() for p in draw_inputs}
        if settings.get('RF_CLIENT_455_CHARACTER_DRAW')=='ON':
            route_inputs=['scripts/native/'+p for p in ['client455_character_draw.h','client455_character_draw_internal.h','client455_character_draw_core.cpp','client455_character_draw.cpp','test_client455_character_draw.cpp','test_client455_draw.cpp','client_character_draw_lab.inc']]
            report['character_draw_input_sha256']={p:hashlib.sha256((WS/p).read_bytes()).hexdigest() for p in route_inputs}
        if settings.get('RF_CLIENT_455_SHADERS')=='ON':
            shader_inputs=['scripts/native/'+p for p in ['client455_shaders.cpp','client455_shaders.h','client455_shader_key.h','test_client455_shaders.cpp','client_shaders_lab.inc']]
            report['shader_input_sha256']={p:hashlib.sha256((WS/p).read_bytes()).hexdigest() for p in shader_inputs}
        if settings.get('RF_CLIENT_455_ANIMATION_MANAGER')=='ON':
            manager_inputs=['scripts/native/'+p for p in ['client455_animation_manager.cpp','client455_animation_manager.h','test_client455_animation_manager.cpp','client_animation_manager_lab.inc']]
            report['animation_manager_input_sha256']={p:hashlib.sha256((WS/p).read_bytes()).hexdigest() for p in manager_inputs}
        if settings.get('RF_CLIENT_455_LOOP_CLOCK')=='ON':
            loop_inputs=['scripts/native/'+p for p in ['client455_loop_clock.cpp','client455_loop_clock.h','client455_loop_clock_bridge.inc','test_client455_loop_clock.cpp','client_loop_clock_lab.inc']]+['work/client-build/source/R3Engine/common/commonutil.cpp']
            report['loop_clock_input_sha256']={p:hashlib.sha256((WS/p).read_bytes()).hexdigest() for p in loop_inputs}
        if settings.get('RF_CLIENT_455_ANIMATION_TIMING')=='ON':
            timing_inputs=['scripts/native/'+p for p in ['client455_animation_timing.cpp','client455_animation_timing.h','test_client455_animation_timing.cpp','client_animation_timing_lab.inc']]+['work/client-build/source/RF_Client/cresobject.cpp']
            report['animation_timing_input_sha256']={p:hashlib.sha256((WS/p).read_bytes()).hexdigest() for p in timing_inputs}
        if settings.get('RF_CLIENT_455_MESH08')=='ON':
            mesh08_inputs=['scripts/native/client455_mesh08.cpp','scripts/native/client455_mesh08.h','scripts/native/test_client455_mesh08.cpp','scripts/native/client_mesh08_lab.inc']
            report['mesh08_input_sha256']={p:hashlib.sha256((WS/p).read_bytes()).hexdigest() for p in mesh08_inputs}
        if settings.get('RF_CLIENT_455_MESH_BINDINGS')=='ON':
            mesh_binding_inputs=['scripts/native/client455_mesh_bindings.cpp','scripts/native/client455_mesh_bindings.h','scripts/native/test_client455_mesh_bindings.cpp','scripts/native/client_mesh_bindings_lab.inc']
            report['mesh_binding_input_sha256']={p:hashlib.sha256((WS/p).read_bytes()).hexdigest() for p in mesh_binding_inputs}
        if settings.get('RF_CLIENT_455_MESH_RUNTIME')=='ON':
            mesh_runtime_inputs=['scripts/native/client455_mesh_runtime.cpp','scripts/native/client455_mesh_runtime.h','scripts/native/test_client455_mesh_runtime.cpp','scripts/native/client_mesh_runtime_lab.inc']
            report['mesh_runtime_input_sha256']={p:hashlib.sha256((WS/p).read_bytes()).hexdigest() for p in mesh_runtime_inputs}
        if settings.get('RF_CLIENT_455_TEXTURE')=='ON':
            texture_inputs=['scripts/native/'+p for p in ['client455_character_rfs.cpp','client455_character_rfs.h','client455_character_dds_key.h','client455_texture.cpp','client455_texture.h','test_client455_texture.cpp','client_texture_lab.inc']]
            report['texture_input_sha256']={p:hashlib.sha256((WS/p).read_bytes()).hexdigest() for p in texture_inputs}
        if settings.get('RF_CLIENT_455_SHARED_BUFFERS')=='ON':
            buffer_inputs=['scripts/native/'+p for p in ['client455_shared_buffers.cpp','client455_shared_buffers.h','test_client455_shared_buffers.cpp','client_shared_buffers_lab.inc']]
            report['shared_buffer_input_sha256']={p:hashlib.sha256((WS/p).read_bytes()).hexdigest() for p in buffer_inputs}
        if settings.get('RF_CLIENT_455_MODELS')=='ON':
            model_inputs=['scripts/native/'+p for p in ['client455_model_lifecycle.cpp','client455_model_lifecycle.h','client455_model_loader.cpp','client455_model_loader.h','test_client455_models.cpp','client_models_lab.inc']]
            report['model_input_sha256']={p:hashlib.sha256((WS/p).read_bytes()).hexdigest() for p in model_inputs}
        if settings.get('RF_CLIENT_455_CHARACTER_MANAGER')=='ON':
            character_manager_inputs=['scripts/native/'+p for p in ['client455_character_manager.cpp','client455_character_manager.h','test_client455_character_manager.cpp','client_character_manager_lab.inc']]
            report['character_manager_input_sha256']={p:hashlib.sha256((WS/p).read_bytes()).hexdigest() for p in character_manager_inputs}
        if settings.get('RF_CLIENT_455_LEGACY_RUNTIME')=='ON':
            legacy_runtime_inputs=['scripts/native/'+p for p in ['client455_legacy_runtime.cpp','client455_legacy_runtime.h','client455_legacy_model.cpp','client455_legacy_model.h','test_client455_legacy_runtime.cpp','client_legacy_runtime_lab.inc']]
            report['legacy_runtime_input_sha256']={p:hashlib.sha256((WS/p).read_bytes()).hexdigest() for p in legacy_runtime_inputs}
        if settings.get('RF_CLIENT_455_ANIMATION')=='ON':
            animation_inputs=['scripts/native/'+p for p in ['client455_animation.cpp','client455_animation.h','test_client455_animation.cpp','client_animation_lab.inc']]
            report['animation_input_sha256']={p:hashlib.sha256((WS/p).read_bytes()).hexdigest() for p in animation_inputs}
        if settings.get('RF_CLIENT_455_POSE')=='ON':
            pose_inputs=['scripts/native/'+p for p in ['client455_pose.cpp','client455_pose.h','test_client455_pose.cpp','client_pose_lab.inc','client455_secondary.cpp','client455_secondary.h','test_client455_secondary.cpp']]
            report['pose_input_sha256']={p:hashlib.sha256((WS/p).read_bytes()).hexdigest() for p in pose_inputs}
        if settings.get('RF_CHARACTER_MESH_SOURCE')=='ON':
            mesh_inputs=['scripts/native/character_mesh_bindings.cpp','scripts/native/test_character_mesh_bindings.cpp','scripts/native/client_character_mesh_lab.inc']
            mesh_inputs+=['scripts/native/character_mesh_init.cpp','scripts/native/character_mesh_format.h','scripts/native/test_character_mesh_init.cpp','scripts/native/client_character_init_lab.inc']
            report['character_mesh_input_sha256']={p:hashlib.sha256((WS/p).read_bytes()).hexdigest() for p in mesh_inputs}
        if settings.get('RF_CLIENT_455_WEATHER')=='ON':
            weather_inputs=['scripts/native/client455_weather.cpp','scripts/native/client455_weather_format.h','scripts/native/client_weather_lab.inc']
            if settings.get('RF_CLIENT_455_CLOCK')=='ON':
                weather_inputs+=['scripts/native/client455_clock.cpp','scripts/native/client455_clock.h','scripts/native/test_client455_clock.cpp']
            if settings.get('RF_CLIENT_455_MAP_TIME')=='ON':
                weather_inputs+=['scripts/native/client455_map_time.cpp','scripts/native/client455_map_time.h','scripts/native/test_client455_map_time.cpp']
                weather_inputs+=['work/client-build/source/RF_Client/cland.cpp','work/client-build/source/RF_Client/cland.h','work/client-build/source/RF_Client/network/netmsgprocessor/map/cnetmsgprocessor_map.cpp']
            if settings.get('RF_CLIENT_455_TIME_COMMANDS')=='ON':
                weather_inputs+=['scripts/native/client455_time_commands.cpp','scripts/native/client455_time_commands.h','scripts/native/test_client455_time_commands.cpp','scripts/native/client_time_commands_lab.inc','work/client-build/source/RF_Client/character/avatar/cavatar_relationinfo2.cpp']
            report['weather_input_sha256']={p:hashlib.sha256((WS/p).read_bytes()).hexdigest() for p in weather_inputs}
        if settings.get('RF_CLIENT_455_RESOURCE_IO')=='ON':
            resource_inputs=['scripts/native/client455_resource_io.cpp','scripts/native/client455_resource_io.h','scripts/native/client_resource_lab.inc',
                             'work/client-build/source/R3Engine/1stclass/r3particle.cpp']
            report['resource_input_sha256']={p:hashlib.sha256((WS/p).read_bytes()).hexdigest() for p in resource_inputs}
            graphics_inputs=['scripts/native/client_graphics_lab.inc','work/client-build/source/R3Engine/1stclass/entity.cpp',
                             'work/client-build/source/R3Engine/1stclass/r3d3dtex.cpp','work/client-build/source/R3Engine/1stclass/renderentity.cpp']
            report['graphics_input_sha256']={p:hashlib.sha256((WS/p).read_bytes()).hexdigest() for p in graphics_inputs}
        report['scope']='Full client project with own CPU/hidden-window GPU lab entry; normal game initialization bypassed, game DLLs delayed. Build record only, runtime recorded separately.'
    (WS / args.output).write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k: report[k] for k in ['build_exit', 'error_counts', 'generated_objects']}, ensure_ascii=True))


if __name__ == '__main__':
    main()
