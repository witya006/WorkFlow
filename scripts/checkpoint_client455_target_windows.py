"""Record real character selection and the 455 base download exchange."""
import json
from pathlib import Path

from checkpoint_client455_party_window import path, read, save
from checkpoint_client455_rvp_effects import check, require, sha
from client455_normal_link_evidence import validate_normal_link
from client455_ui_checkpoint import own_symbols, record
from compare_client_binaries import WS


BASE = 0x400000
METHODS = {
    'CGUISelectedCharWin': dict(Init=0x679b50, SetSprite=0x679ca0, SetCharName=0x679d40,
                              SetAttackState=0x679de0, SetSelectState=0x679e40, SetHPRate=0x679ea0),
    'CGUISelectedMobInfoWin': dict(Init=0x67a620, SetSprite=0x67a9d0, SetMobName=0x67b4f0,
                                 SetLevel455=0x67b600, SetHP=0x67b6f0),
    'CGUISelectedCharMenu': dict(Init=0x678920, SetSprite=0x678b30, SetMenuType=0x678c10, SetPartyMenu=0x679440),
    'CGUIKillingCounter': dict(Init=0x721ea0, SetSprite=0x721ef0),
}


def bindings(link, ref):
    native = WS / 'scripts/native'
    source = WS / 'work/client455-port/normal/source/userinterface/gamewindow'
    target = (native / 'client455_target_windows.inc', source / 'guiselectedcharwin.cpp')
    sources = {
        'CGUISelectedCharWin': target,
        'CGUISelectedMobInfoWin': target,
        'CGUISelectedCharMenu': (native / 'client455_target_menu.inc', source / 'guiselectedcharmenu.cpp'),
        'CGUIKillingCounter': (native / 'client455_dungeon_counter.inc', source / 'dungeon/guidungeon.cpp'),
    }
    symbols = own_symbols(link)
    verified = {row['rva'] for row in ref['references'][0]['functions']}
    rows = []
    for owner, methods in METHODS.items():
        for method, va in methods.items():
            rva, name = hex(va - BASE), f'{owner}::{method}'
            item = next((p for p in sources[owner] if (name + '(').encode() in p.read_bytes()), None)
            require(rva in verified and item is not None, 'Selected target binding ' + name)
            addresses = [hex(at) for at, symbol in symbols if symbol.startswith(f'?{method}@{owner}@@')]
            rows.append(dict(rva=rva, symbol=name, source=record(item), ordinary_symbol_rvas=addresses,
                             standalone_symbol_retained=bool(addresses), complete_equivalence=False))
    save('target-windows-bindings', dict(schema_version=1, reference_sha256=ref['references'][0]['sha256'],
                                        architecture='x86', image_base='0x400000', normal_executable=link['executable'],
                                        scope='Partial target panels, target menu and dungeon counter skin.', functions=rows))
    return rows


def main():
    link, ref, native, live = (read(name) for name in ('normal-link', 'target-windows-reference',
                                                      'target-windows-native', 'character-selection-live-taiwan-native'))
    require(validate_normal_link(link) == 'PASS', 'Current complete own build and link')
    link_sha = sha(path('normal-link'))
    require(native['normal_link_sha256'] == live['normal_link_sha256'] == link_sha and
            live['executable']['sha256'] == link['executable']['sha256'], 'Current exact runtime evidence')
    result = native['native']
    require(native['status'] == 'PASS' and native['natural_exit'] == 0 and len(native['frames']) == 4 and
            result['player_choices'] == 7 and result['unit_choices'] == 3 and result['tower_choices'] == 1 and
            result['window_messages'] == 1 and not result['live_targeting'], 'Reviewed four target and dungeon fixtures')
    for item in [ref['raw'], *ref['sources'], native['source'], native['script'], native['harness'],
                 native['exe'], native['config'], native['output'], native['console'], *native['inputs']]:
        check(item)
    for frame in native['frames']:
        check(frame)
        check(frame['preview'])
    for key in ('events', 'captured_frame', 'capture_metadata'):
        check(live[key])
    require(live['live_server']['private_handoff_removed'] and live['debugger_exit'] == 0 and
            any(row.get('own_child_validated') and row.get('sent') for row in live['selection_input']),
            'Actual selection and cleaned private handoff')
    expected = ['tx:1:14:1', 'rx:1:15:22', 'select-result:0:0:0', 'tx:3:3:0', 'rx:3:4:431']
    events = [json.loads(line) for line in (WS / live['events']['file']).read_text().splitlines()]
    messages = [e['value'].removeprefix('RF455 Protocol:') for e in events if e.get('kind') == 'debug_string' and
                e.get('value', '').startswith('RF455 Protocol:')]
    require(all(event in messages for event in expected) and [messages.index(e) for e in expected] ==
            sorted(messages.index(e) for e in expected), 'Actual ordered selection and base exchange')
    require(not any(e.startswith(('tx:3:5:', 'tx:3:7:')) for e in messages) and
            not any(e['kind'] == 'exception' and not e.get('first_chance') for e in events),
            'No inventory request or fatal exception in the base response run')
    rows = bindings(link, ref)
    names = ['target-windows-reference', 'target-windows-native', 'target-windows-bindings', 'normal-preparation',
             'normal-build', 'normal-consumers', 'normal-link', 'own-entry', 'startup-audit', 'startup-taiwan-native',
             'live-launcher-native', 'character-selection-live-taiwan-native', 'live-server']
    scope = ('The ordinary client reaches its base request after accepted character selection. '
             'The local server returns the 431-byte 3/4 payload. Its 455 decoder and world entry remain open.')
    private = WS / 'artifacts/client455-progress'
    report = dict(status='PARTIAL_WAITING_FOR_BASE_DECODER', scope=scope, script=record(Path(__file__)),
                  normal_link_sha256=link_sha, normal_executable=link['executable'],
                  runtime_login_report=record(path('character-selection-live-taiwan-native')),
                  fresh_evidence={name: record(path(name)) for name in names},
                  prior_runtime=record(private / 'before174/manifest.json'),
                  base_decoder_analysis=record(private / 'base-download174-idalib.json'),
                  intermediate_failures=[record(private / file) for file in ('target-windows174-initial-failure.json',
                                                                             'target-windows174-post-stage-failure.json')],
                  component_frames_visually_inspected=True, explicit_function_bindings=len(rows),
                  standalone_symbols=sum(row['standalone_symbol_retained'] for row in rows),
                  observed_sequence=expected, base_request_sent=True, base_response_received=True,
                  base_response_decoded=False, full_factory=False, world_entered=False, full_client=False,
                  private_handoff_removed=True, input_exe_executed=False, server_modified=False,
                  gaps=ref['gaps'], M6='OPEN', M6F='OPEN', M7='OPEN', M9='OPEN')
    save('target-windows-checkpoint', report)
    registry_path = WS / 'inventory/client-features.json'
    registry = json.loads(registry_path.read_text())
    identity = 'CLIENT455-TARGET-WINDOWS-174'
    registry['features'] = [row for row in registry['features'] if row['id'] != identity]
    for feature in registry['features']:
        if feature.get('runtime_gate_current'):
            feature['runtime_gate_current'] = False
    registry['features'].append(dict(id=identity, area='ui', status='partial', runtime_gate_current=True,
                                    evidence=[path(name).relative_to(WS).as_posix() for name in
                                              ('target-windows-checkpoint', 'target-windows-reference', 'target-windows-native')],
                                    description=scope, gaps=report['gaps']))
    registry_path.write_text(json.dumps(registry, indent=2) + '\n', encoding='ascii')
    print('PARTIAL_WAITING_FOR_BASE_DECODER: tx 3/3/0, rx 3/4/431; inventory and world open')


if __name__ == '__main__':
    main()
