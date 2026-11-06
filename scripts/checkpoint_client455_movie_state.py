"""Validate checkpoint077 evidence without claiming a complete movie player/client."""
import hashlib
import json
from pathlib import Path

from audit_client455_own_entry import symbol
from build_client455_x87_math import read_va
from client455_normal_link_evidence import validate_normal_link
from compare_client_binaries import WS, pe


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(name):
    return json.loads((WS / 'inventory' / (name + '.json')).read_text())


def check(row):
    if sha(WS / row['file']) != row['sha256']:
        raise ValueError('Changed checkpoint077 evidence: ' + row['file'])


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    link = load('client455-normal-link')
    require(validate_normal_link(link) == 'PASS', 'Normal link failed')
    link_hash = sha(WS / 'inventory/client455-normal-link.json')
    engine = load('client455-startup-engine-build')
    engine_hash = sha(WS / 'inventory/client455-startup-engine-build.json')
    prep = load('client455-normal-preparation')
    check({'file': prep['manifest'], 'sha256': prep['manifest_sha256']})
    reference = load('client455-movie-state-reference')
    require(engine['objects'] == 67 and len(engine['derived_sources']) == 9,
            'Wrong checkpoint077 engine source set')
    check({'file': engine['library'], 'sha256': engine['library_sha256']})
    for row in engine['base_sources'] + engine['derived_sources'] + [engine['baseline_library']]:
        check(row)
    for row in engine['derived_sources']:
        check({'file': row['original'], 'sha256': row['original_sha256']})
    for key in ['movie_state', 'fullscreen_effect']:
        for name, digest in engine[key].items():
            require(sha(WS / 'scripts/native' / name) == digest, 'Changed engine provider: ' + name)
    for name in ['client455_tutorial_intro.h', 'client455_tutorial_intro.cpp',
                 'client455_tutorial_intro_camera.cpp']:
        require(prep['record_inputs'][name] == sha(WS / 'scripts/native' / name), 'Changed intro provider')
    require(sha(WS / 'work/client455-port/normal/include/client455_movie_state.h') ==
            sha(WS / 'scripts/native/client455_movie_state.h'), 'Normal movie header drift')
    for report, name in [(engine, 'build_client455_engine_startup.py'),
                         (prep, 'prepare_client455_normal.py'),
                         (reference, 'audit_client455_movie_state.py')]:
        require(report['script_sha256'] == sha(WS / 'scripts' / name), 'Stale generator/reference script')
    check(reference['raw_evidence'])
    require(len(reference['assemblies']) == 4, 'Missing full movie-state assembly evidence')
    for folder, pin in zip(['current', 'reference-backup'], reference['references']):
        path = WS / 'work/client-reference' / folder / 'RF_Online.bin'
        raw = path.read_bytes()
        require(sha(path) == pin['sha256'] and len(pin['ranges']) == 13, 'Changed455 pin/ranges')
        for row in pin['ranges']:
            require(hashlib.sha256(read_va(raw, 0x400000 + int(row['rva'], 16), row['bytes'])).hexdigest()
                    == row['sha256'], 'Changed455 movie-state range')

    def run(name, script):
        report = load(name)
        require(report['normal_link_sha256'] == link_hash and report['engine_report_sha256'] == engine_hash,
                'Stale native link/engine: ' + name)
        require(report['source_sha256'] == sha(WS / report['source']) and
                report['script_sha256'] == sha(WS / 'scripts' / script) and
                report['builder_sha256'] == sha(WS / 'scripts/client455_own_probe.py'), 'Stale native source')
        for key in ['exe', 'map', 'console', 'output']:
            check(report[key])
        for row in report['inputs'] + report['frames']:
            check(row)
        require(report['natural_exit'] == 0 and report['native']['status'] == 'PASS' and
                report['native'] == json.loads((WS / report['output']['file']).read_text()) and
                pe((WS / report['exe']['file']).read_bytes())['architecture'] == 'x86', 'Native run failed')
        return report

    def review(name, runs, count):
        report = load(name)
        require(report['manually_reviewed'] and len(report['frames']) == count and
                report['script_sha256'] == sha(WS / 'scripts' / (name.replace('client455-', 'review_client455_')
                      .replace('-visual', '').replace('-', '_') + '.py')), 'Missing current visual review')
        for row in report.get('sheets', [report.get('sheet')]):
            check(row)
        for row in report['frames']:
            check(row)
            require(sha(WS / row['preview']) == row['preview_sha256'], 'Changed preview')
            digest = runs[row['race']] if 'race' in row else runs['all']
            require(row.get('native_sha256', report.get('native_sha256')) == digest, 'Stale reviewed frame')

    movie = run('client455-movie-state-native', 'probe_client455_movie_state.py')
    actual = movie['native']
    require(movie['reference_sha256'] == sha(WS / 'inventory/client455-movie-state-reference.json') and
            actual['flag_combinations'] == 8 and actual['GPU_frames'] == 6 and actual['warnings'] == 0 and
            not actual['full_RVP_player'] and not actual['full_Tutorial'], 'Movie-state result/scope mismatch')
    require(all(actual[k] for k in ['real_positive_movie_flags', 'fullrequest_and_upperbits',
            'raw_add_remove_without_display_sideeffects', 'separate_defaultFov_and_projection',
            'real_letterbox_logo_plain_and_fullscreen', 'legacy_request_api_explicit']), 'Movie-state contract failed')
    mapping = (WS / movie['map']['file']).read_text()
    address = symbol(mapping, '?RTMovieFrameMove@@YAXXZ')
    code = read_va((WS / movie['exe']['file']).read_bytes(), address, 16)
    require(code.hex() == movie['player_evidence']['entry_bytes'] and
            movie['player_evidence']['compiled_player_stub'] and code.startswith(bytes.fromhex('558bec5dc3')),
            'Disabled player evidence changed; reassess its completeness')
    review('client455-movie-state-visual', {'all': sha(WS / 'inventory/client455-movie-state-native.json')}, 6)

    fullscreen = run('client455-fullscreen-effect-native', 'probe_client455_fullscreen_effect.py')['native']
    require(fullscreen['GPU_frames'] == 18 and fullscreen['warnings'] == 0 and
            not fullscreen['complete_water_bloom_lifecycle'] and all(fullscreen[k] for k in
            ['actual_R3Begin_FullScreenEffect_End', 'current_scene_opaque_final',
             'framebuffer_depth_viewport_UI_restored', 'texture512_low_video_memory',
             'failed_BeginScene_reported']), 'Fullscreen regression failed')
    review('client455-fullscreen-effect-visual', {'all': sha(WS / 'inventory/client455-fullscreen-effect-native.json')}, 5)
    observations = []
    hashes = {}
    for race, count in [('bellato', 9), ('cora', 9), ('accretia', 8)]:
        name = 'client455-tutorial-intro-' + race + '-native'
        report = run(name, 'probe_client455_tutorial_intro.py')
        check(report['trace'])
        actual = report['native']
        require(report['real_positive_movie_flags'] and report['real_fullscreen_mode_density'] and
                actual['selected'] == actual['captures'] == actual['fade_outs'] == count and
                actual['warnings'] == 0 and actual['memory_before'] == actual['memory_after'] and
                not actual['full_stage_QBI_engine_controls'] and all(actual[k] for k in
                ['real_camera_fade_screen_mouse_avatar_world', 'deferred_skip', 'reload_retains_counters']),
                'Intro regression/scope failed: ' + race)
        trace = [json.loads(line) for line in (WS / report['trace']['file']).read_text().splitlines()]
        require(len(trace) == actual['frames'] and not trace[-1]['active'] and trace[-1]['ordinal'] == count,
                'Intro did not finish')
        hashes[race] = sha(WS / 'inventory' / (name + '.json'))
        observations.append({'race': race, 'cameras': count, 'ticks': actual['frames']})
    review('client455-tutorial-intro-visual', hashes, 29)
    ui = load('client455-ui-startup-native')
    contracts = load('client455-startup-contracts-native')
    require(ui['normal_link_sha256'] == link_hash and ui['completed_existing_client_create'] and
            ui['markers'][-1]['eax'] == 1 and contracts['build_sha256'] == engine_hash,
            'Current exactPE/Create1 and engine contracts required')
    output = {'status': 'PARTIAL', 'movie_state_display_defaultFov': 'PASS_BOUNDED',
              'GPU_movie_frames': 6, 'flag_combinations': 8, 'GPU_fullscreen_frames': 18,
              'reviewed_frames': 40, 'observations': observations, 'exactPE_Create1': 'PASS',
              'player_is_compiled_stub': True, 'normal_link_sha256': link_hash,
              'engine_report_sha256': engine_hash, 'script_sha256': sha(Path(__file__)),
              'gaps': reference['gaps'] + ['Screen-size wrapper: source state500 vs viewport480 in direct InitR3D3D fixture; not repaired by this checkpoint'],
              'input_exe_executed': False, 'server_modified': False,
              'M6': 'OPEN', 'M6F': 'OPEN', 'M7': 'OPEN', 'M9': 'OPEN'}
    (WS / 'inventory/client455-movie-state-checkpoint.json').write_text(json.dumps(output, indent=2) + '\n')
    print('PARTIAL: movie flags8/GPU6, intro26, fullscreen18, reviewed40, exactCreate1 PASS; full RVP/Tutorial/M9 OPEN')


if __name__ == '__main__':
    main()
