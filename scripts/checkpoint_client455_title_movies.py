"""Pin the original Title movie routes and verify playback/skip with installed assets."""

import argparse
import json
import struct
from pathlib import Path

from build_client455_x87_math import read_va
from checkpoint_client455_monster_force_damage import run_fixture
from checkpoint_client455_party_window import path, read, save
from checkpoint_client455_rvp_effects import check, require, sha
from client455_normal_link_evidence import validate_normal_link
from client455_own_probe import build_full_object_probe
from client455_reference_regions import verify_regions
from client455_runtime_inputs import copy_title_movies
from client455_ui_checkpoint import record
from compare_client_binaries import WS


REFERENCE = WS / 'artifacts/client455-progress/title-movies211/reference.json'


def verify_ordinary(name, link, link_sha):
    file = REFERENCE.parent.parent / f'client455-title-escape-{name}-taiwan-native.json'
    report = json.loads(file.read_text())
    require(report['normal_link_sha256'] == link_sha and report['executable'] == link['executable']
            and sha(WS / report['staged_executable']) == link['executable']['sha256'], 'Exact ordinary client')
    require(report['debugger_exit'] == 0 and report['first_login_frame_captured']
            and report['login_render_returned_after_capture'] and report['device_state']['windowed'],
            'Actual first Login frame after Title')
    require(report['title_escape'] == [dict(kind='title_escape_posted', own_child_validated=True, sent=True)],
            'Escape reached only the owned child window')
    check(report['events'])
    check(report['captured_frame'])
    events = [json.loads(line) for line in (WS / report['events']['file']).read_text().splitlines()]
    require(not any(event['kind'] == 'exception' and not event['first_chance'] for event in events),
            'No unhandled startup exception')
    debug = [event['value'] for event in events if event['kind'] == 'debug_string']
    start = debug.index('RF455 Protocol:title-movie-start:1:0:0')
    if name == 'prologue':
        end = debug.index('RF455 Protocol:title-movie-end:1:1:0')
        next_start = debug.index('RF455 Protocol:title-movie-start:2:0:0')
        require(start < end < next_start, 'Logo finishes naturally before the prologue starts')
        start = next_start
    stage = 1 if name == 'logo' else 2
    skip = debug.index(f'RF455 Protocol:title-movie-skip:{stage}:27:0')
    login = next(i for i, value in enumerate(debug) if value.startswith('RF455 LoginFrame:00000000:'))
    require(start < skip < login, 'Stock movie starts, Escape ends it, Login renders')
    return dict(report=record(file), login_frame=report['captured_frame'])


def verify_reference():
    proof = verify_regions(REFERENCE)
    raw = json.loads(REFERENCE.read_text())
    require(raw['closed']['success'] and raw['closed']['saved'], 'Owned IDA session closed')
    for pin in proof['references']:
        binary = (WS / pin['file']).read_bytes()
        branch = read_va(binary, 0x557fbd, 5)
        require(branch[0] == 0xe9 and 0x557fc2 + struct.unpack('<i', branch[1:])[0] == 0x558282,
                'The pinned FrameMove bypasses the retained video branch')
        for addr, value in ((0xab0e84, b'PlayAvi\0'), (0xab0f34, b'Play%d\0'), (0xab0f3c, b'PlayedNum\0')):
            require(read_va(binary, addr, len(value)) == value, 'Original title video profile keys')
    save('title-movies-reference', dict(
        **proof, raw=record(REFERENCE), bypass_rva='0x157fbd', profile='CcrLogo.dat',
        logo='PlayAvi/Logo', prologue='PlayAvi/Play<timeGetTime modulo PlayedNum>',
        restored_on_explicit_request=True))
    return proof


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--reference-only', action='store_true')
    args = parser.parse_args()
    proof = verify_reference()
    if args.reference_only:
        print({key: proof[key] for key in ('full_functions', 'full_instructions', 'positive_cfg_blocks')})
        return
    link = read('normal-link')
    link_sha = sha(path('normal-link'))
    require(validate_normal_link(link) == 'PASS', 'Exact current client build')
    startup = read('startup-taiwan-native')
    require(startup['normal_link_sha256'] == link_sha and startup['debugger_exit'] == 0 and
            startup['summary']['after_sound_reached'], 'Exact early Taiwan startup')

    source = WS / 'scripts/native/client455_title_movies_probe.cpp'
    exe = build_full_object_probe('title-movies', source)
    client = Path(json.loads((WS / 'config/paths.json').read_text())['client_455'])
    inputs = copy_title_movies(client, exe.parent, 'zh-tw')
    require(len(inputs) == 4, 'Stock Taiwan profile and all three configured movies')
    config = exe.parent / 'R3Engine.ini'
    config.write_text('[Setup]\nLanguage=Taiwan\n[Sound]\nMusic=FALSE\n', encoding='ascii')
    logo, logo_log = run_fixture(exe, [], [], 'skip-logo')
    prologue, prologue_log = run_fixture(exe, [], ['--prologue'], 'skip-prologue')
    for name, result in (('logo', logo), ('prologue', prologue)):
        require(result == dict(status='PASS', skipped=name, login_stage=1, video_window_closed=True),
                f'Escape releases the stock {name} window')
    ordinary = {name: verify_ordinary(name, link, link_sha) for name in ('logo', 'prologue')}
    names = ('normal-link', 'normal-preparation', 'normal-build', 'normal-consumers',
             'own-entry', 'startup-audit', 'startup-taiwan-native', 'title-movies-reference')
    sources = ('client455_title_movies_port.py', 'native/client455_title_movies.inc',
               'native/client455_title_movies_probe.cpp', 'client455_runtime_inputs.py',
               'prepare_client455_normal.py', 'link_client455_normal.py', 'probe_client455_device_startup.py',
               'native/own_client_startup_debugger.cpp')
    save('title-movies-checkpoint', dict(
        status='PARTIAL_ORDINARY_TITLE_MOVIES',
        scope='Ordinary Title plays its configured logo and prologue and honors Escape.',
        normal_executable=link['executable'], normal_link_sha256=link_sha,
        component=[logo, prologue], component_executable=record(exe),
        consoles=[logo_log, prologue_log], inputs=inputs + [record(config)], ordinary=ordinary,
        script=record(Path(__file__)), sources=[record(WS / 'scripts' / name) for name in sources],
        fresh_evidence={name: record(path(name)) for name in names},
        gaps=['Full-screen playback, other regions, full start menu, FireGuard and new-character tutorial.'],
        own_live_run=False, M6='OPEN', M9='OPEN'))
    print(json.dumps(dict(executable=link['executable']['sha256'], components=[logo, prologue], ordinary=ordinary)))


if __name__ == '__main__':
    main()
