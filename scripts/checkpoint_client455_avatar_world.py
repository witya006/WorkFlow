"""Bind live avatar creation, first render completion and spawn reply to one PE."""
import json
from pathlib import Path

from checkpoint_client455_party_window import path, read, save
from checkpoint_client455_rvp_effects import check, require, sha
from client455_normal_link_evidence import validate_normal_link
from client455_ui_checkpoint import own_symbols, record
from compare_client_binaries import WS


GAPS = [
    'Camera and movement input, observed avatar displacement and a post-spawn frame capture',
    'Complete spawn response side effects and world update dispatch',
    'NPCs, inventory, Force, Linker owners, quest journal, guild and complete chat behavior',
]


def main():
    names = ('normal-link', 'avatar-world-reference', 'initial-download-native', 'character-selection-live-taiwan-native')
    link, reference, native, live = (read(name) for name in names)
    link_sha = sha(path('normal-link'))
    require(validate_normal_link(link) == 'PASS' and link_sha == live['normal_link_sha256'] == native['normal_link_sha256']
            and live['executable']['sha256'] == link['executable']['sha256'], 'Exact ordinary client evidence')
    require(native['status'] == 'PASS' and native['native']['store_stride'] == 16, 'Store decoder regression')
    bsp = next(row for row in live['inputs'] if row['file'].lower().endswith('/map/neutralb/neutralb.bsp'))
    shader = next(row for row in live['inputs'] if row['file'].lower().endswith('/system/shader/litgrass1.vso'))
    for item in [reference['raw'], reference['decompilation'], *reference['sources'], bsp, shader, *(native[key] for key in
                 ('source', 'header', 'script', 'executable', 'console')), *(live[key] for key in
                 ('events', 'captured_frame', 'capture_metadata'))]:
        check(item)
    events = [json.loads(line) for line in (WS / live['events']['file']).read_text().splitlines()]
    messages = [e['value'].removeprefix('RF455 Protocol:') for e in events if e['kind'] == 'debug_string' and
                e.get('value', '').startswith('RF455 Protocol:')]
    observed = read('store-download-checkpoint')['observed_sequence'] + [
        'avatar-ready:0:0:0', 'tx:3:1:1', 'world-frame:0:0:0', 'rx:3:2:1', 'position-mode:0:0:0']
    require(all(e in messages for e in observed) and [messages.index(e) for e in observed] ==
            sorted(messages.index(e) for e in observed), 'Actual avatar, scene completion and start-position sequence')
    subsequent = [e for e in messages[messages.index('position-mode:0:0:0') + 1:] if e.startswith('rx:')]
    require(any(e.startswith('rx:4:') for e in subsequent), 'World updates arrived after position acceptance')
    require(live['debugger_exit'] == 0 and live['live_server']['private_handoff_removed'] and
            any(row.get('own_child_validated') and row.get('sent') for row in live['selection_input']) and
            any(e['kind'] == 'selection_observation_end' for e in events) and
            not any(e['kind'] == 'exception' and not e.get('first_chance') for e in events), 'Ordinary observation ended without a fatal exception')

    prepared = WS / 'work/client455-port/normal/source'
    methods = [('SetCombatMode', 'CAvatar', 'character/avatar/cavatar_etc.cpp', reference['avatar']['mode_rva']),
               ('Create_Avatar', 'CGP_MainGame', 'gameprogress/cgp_maingame.cpp', reference['avatar']['create_rva']),
               ('Init', 'CGUIChatInputWindow', 'userinterface/gamewindow/guichatwindow.cpp', reference['chat']['init_rva']),
               ('Draw', 'CGUIChatInputWindow', 'userinterface/gamewindow/guichatwindow.cpp', reference['chat']['draw_rva'])]
    bindings = []
    symbols = own_symbols(link)
    for name, owner, relative, address in methods:
        source = prepared / relative
        rvas = [hex(at) for at, symbol in symbols if symbol.startswith(f'?{name}@{owner}@@')]
        qualified = owner + '::' + name
        code = source.read_bytes()
        require((qualified + '(').encode() in code, 'Own source ' + qualified)
        caller_rvas = []
        if qualified == 'CGUIChatInputWindow::Init' and not rvas:
            require(b'm_pChatInputWin->Init( &m_uiInputField );' in code, 'Compact chat initializer caller')
            caller_rvas = [hex(at) for at, symbol in symbols if symbol.startswith('?SetChatInputWindow@CGUIChatWindow@@')]
        require(rvas or caller_rvas, 'Linked own ' + qualified)
        bindings.append(dict(rva=address, symbol=qualified, source=record(source), ordinary_symbol_rvas=rvas,
                             linked_caller_rvas=caller_rvas, complete_equivalence=False))
    save('avatar-world-bindings', dict(schema_version=1, reference_sha256=reference['references'][0]['sha256'],
                                      architecture='x86', image_base='0x400000', normal_executable=link['executable'],
                                      functions=bindings))
    names += ('avatar-world-bindings', 'normal-preparation', 'normal-build', 'normal-consumers', 'own-entry',
              'startup-audit', 'startup-taiwan-native', 'live-launcher-native', 'live-server')
    scope = ('The ordinary client creates the avatar on NeutralB, completes its first scene, receives the accepted '
             'start position and keeps receiving world updates until the observation ends.')
    private = WS / 'artifacts/client455-progress'
    report = dict(status='PARTIAL_LIVE_WORLD_STARTED_MOVEMENT_OPEN', scope=scope, script=record(Path(__file__)),
                  normal_link_sha256=link_sha, normal_executable=link['executable'],
                  runtime_login_report=record(path('character-selection-live-taiwan-native')),
                  fresh_evidence={name: record(path(name)) for name in names},
                  prior_runtime=record(private / 'before180/manifest.json'), observed_sequence=observed,
                  intermediate_failures=[record(private / name) for name in
                                         ('avatar180-first-frame-failure.json', 'avatar180-sky-failure.json')],
                  explicit_function_bindings=len(bindings), map=dict(index=0, bsp=bsp, lit_grass_shader=shader),
                  avatar_created=True, first_scene_completed=True, start_position_mode=0,
                  subsequent_packets=len(subsequent), world_started=True, movement_verified=False,
                  world_frame_captured=False, full_client=False, private_handoff_removed=True,
                  input_exe_executed=False, server_modified=False, gaps=GAPS, M6='OPEN', M6F='OPEN', M7='OPEN', M9='OPEN')
    save('avatar-world-checkpoint', report)

    registry_path = WS / 'inventory/client-features.json'
    registry = json.loads(registry_path.read_text())
    identity = 'CLIENT455-AVATAR-WORLD-180'
    registry['features'] = [row for row in registry['features'] if row['id'] != identity]
    for feature in registry['features']:
        if feature.get('runtime_gate_current'):
            feature['runtime_gate_current'] = False
    registry['features'].append(dict(id=identity, area='world', status='partial', runtime_gate_current=True,
                                    evidence=[path(name).relative_to(WS).as_posix() for name in
                                              ('avatar-world-checkpoint', 'avatar-world-reference',
                                               'initial-download-native')], description=scope, gaps=GAPS))
    registry_path.write_text(json.dumps(registry, indent=2) + '\n', encoding='ascii')
    print(f'PARTIAL: live NeutralB started, {len(subsequent)} subsequent replies, movement remains open')


if __name__ == '__main__':
    main()
