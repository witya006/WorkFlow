"""Record five-bank startup integration and the actual next UnitTuning failure."""
import json
import re
import struct
import subprocess
from pathlib import Path

from compare_client_binaries import WS
from build_client455_x87_math import read_va
from client455_normal_link_evidence import validate_normal_link
from client455_ui_checkpoint import own_symbols, record
from checkpoint_client455_rvp_effects import sha, check, require
from inspect_client455_failure import inspect


def load(name):
    return json.loads((WS/'inventory'/f'client455-{name}.json').read_text())


def main():
    link = load('normal-link')
    require(validate_normal_link(link) == 'PASS', 'Current successful own link')
    digest = sha(WS/'inventory/client455-normal-link.json')
    ref, native, visual, live = [load(name) for name in [
        'board-startup-reference', 'linker-window-native', 'linker-window-visual-review',
        'character-selection-live-taiwan-native']]
    for item in [ref['raw'], ref['script']] + ref['sources'] + ref['generated'] + ref['helpers']:
        check(item)
    require(ref['full_functions'] == 6 and ref['full_instructions'] == 3032 and
            ref['source_constructed_boards'] == 17 and len(ref['missing_target_owners']) == 37,
            'Exact partial factory evidence')
    require(native['normal_link_sha256'] == live['normal_link_sha256'] == digest,
            'Current exact runtime evidence')
    require(native['main_game_linker_startup'] and native['natural_exit'] == 0 and
            native['native']['status'] == 'PASS' and native['native']['actual_owned_icons'] == 50,
            'Actual fifty-slot ordinary startup/owner test')
    require(native['script_sha256'] == sha(WS/'scripts/probe_client455_linker_window.py') and
            native['builder_sha256'] == sha(WS/'scripts/client455_own_probe.py'), 'Current probe helpers')
    for item in native['inputs'] + [native['source'],native['exe'],native['map'],native['console'],native['output']]:
        check(item)
    require(visual['native_sha256'] == sha(WS/'inventory/client455-linker-window-native.json') and
            visual['reviewed'] and visual['frames'] == native['frames'] and len(native['frames']) == 8,
            'Eight exact visually reviewed frames')
    for item in native['frames']:
        check(item)
        check(item['preview'])
    require(live['first_login_frame_captured'] and live['login_render_returned_after_capture'] and
            live['live_server']['private_handoff_removed'], 'Actual selection frame and cleanup')
    for key in ['events', 'captured_frame', 'capture_metadata']:
        check(live[key])
    require(any(x.get('own_child_validated') and x.get('sent') for x in live['selection_input']),
            'Addressed own-child selection input')
    for value in ['RF455 Protocol:tx:1:14:1', 'RF455 Protocol:rx:1:15:22', 'RF455 Protocol:select-result:0:0:0']:
        require(value in live['protocol_observations'], 'Actual selection ' + value)
    failure = inspect(link, live)
    require(failure['fault_rva_is_own'] and failure['exception']['code'] == '0xc0000005' and
            failure['own_fault']['symbol'].startswith('?GetSpriteXL@CSprite@@'), 'Actual next skin failure')
    symbols = own_symbols(link)

    def address(prefix):
        found = [a for a,n in symbols if n.startswith(prefix)]
        require(len(found) == 1, 'Unique own symbol ' + prefix)
        return found[0]

    for name in ['SetSprite', 'Init']:
        require(any(c['is_code'] and c['symbol'].startswith('?'+name+'@CGUIUnitTuningWindow@@')
                    for c in failure['candidates']), 'UnitTuning failure candidate ' + name)
    caller = next(c for c in failure['candidates'] if c['symbol'].startswith('?Create_Board@CGP_MainGame@@'))
    base_caller = next(c for c in failure['candidates'] if c['symbol'].startswith('?InitWindow@CBaseBoard@@'))
    raw = (WS/link['executable']['file']).read_bytes()
    table = address('??_7CGUIUnitTuningWindow@@6BCGUIContainer@@@')
    init = struct.unpack('<I', read_va(raw,0x400000+table+0x6c,4))[0]-0x400000
    require(init == address('?Init@CGUIUnitTuningWindow@@'), 'Actual UnitTuning Init vtable slot')
    ret = int(base_caller['rva'],16)
    require(read_va(raw,0x400000+ret-3,3) == b'\xff\x50\x6c', 'BaseBoard actual virtual Init call')
    # Decode the exact own prefix to prove the Linker startup call precedes
    # this UnitTuning candidate. Never interpret arbitrary E8 bytes as calls.
    begin, stop = address('?Create_Board@CGP_MainGame@@'), int(caller['rva'],16)
    helper = address('?InitializeMainGame455@CLinkBoard@@')
    info = json.loads((WS/'inventory/msvc-verification.json').read_text())
    dumpbin = Path(info['compiler_path'].splitlines()[0]).with_name('dumpbin.exe')
    result = subprocess.run([str(dumpbin), '/DISASM:BYTES',
                             f'/RANGE:0x{0x400000+begin:x},0x{0x400000+stop:x}',
                             str(WS/link['executable']['file'])], capture_output=True,
                            creationflags=subprocess.CREATE_NO_WINDOW)
    require(result.returncode == 0, 'Own prefix disassembly')
    decoded_path = WS/'artifacts/client455-progress/board166-own-prefix.txt'
    decoded_path.write_bytes(result.stdout)
    calls = []
    for line in result.stdout.decode(errors='replace').splitlines():
        match = re.match(r'^\s+([0-9A-F]{8}): ((?:[0-9A-F]{2} )+)\s+(\w+)\s*(.*?)\s*$',line)
        if not match:
            continue
        at, code = int(match[1],16), bytes.fromhex(match[2])
        require(read_va(raw,at,len(code)) == code, 'Own decoded bytes')
        if match[3] == 'call' and len(code) == 5 and code[0] == 0xe8 and at+5+struct.unpack('<i',code[1:])[0] == 0x400000+helper:
            calls.append(dict(call_rva=hex(at-0x400000), return_rva=hex(at+5-0x400000),
                              bytes=code.hex(), callee_rva=hex(helper)))
    require(len(calls) == 1 and begin < int(calls[0]['return_rva'],16) < stop,
            'Verified completed ordinary Linker startup before UnitTuning')
    source = WS/'work/client455-port/normal/source/gameprogress/cgp_maingame.cpp'
    body = source.read_bytes()
    require(body.index(b'InitializeMainGame455()') < body.index(b'_GetUnitTuningBoard()->InitWindow'),
            'Actual source startup order')
    failure.update(kind='UNIT_TUNING_SKIN_AFTER_FIVE_BANK_LINKER',
                   verified_prior_linker_call=calls[0], own_prefix_disassembly=record(decoded_path),
                   unit_tuning_vtable=dict(rva=hex(table),slot_offset='0x6c',init_rva=hex(init)),
                   verified_base_Init_call=dict(return_rva=hex(ret),bytes='ff506c'),
                   cause='Old CGUIUnitTuningWindow SetSprite/Init follows completed measured Linker startup;restore real455 window and remaining stage graph',
                   whole_client_run_succeeded=False)
    names = ['board-startup-reference', 'linker-window-native', 'linker-window-visual-review',
             'normal-preparation', 'normal-build', 'normal-consumers', 'normal-link', 'own-entry',
             'startup-audit', 'startup-taiwan-native', 'live-launcher-native',
             'character-selection-live-taiwan-native', 'live-server']
    gate = dict(status='PARTIAL_KNOWN_FAILURE',
                scope='Ordinary MainGame Linker now creates five ten-slot banks/window3;actual fifty owners and HWND-to-manager-to-bank4 route tested;live startup passes Linker and fails next old UnitTuning window;world not entered',
                script=record(Path(__file__)),helpers=[record(WS/'scripts/client455_ui_checkpoint.py'),record(WS/'scripts/inspect_client455_failure.py'),record(WS/'scripts/preserve_client455_checkpoint.py')],
                probe_scripts=[record(WS/'scripts/probe_client455_linker_window.py'),record(WS/'scripts/review_client455_linker_window.py')],
                normal_link_sha256=digest,normal_executable=link['executable'],
                runtime_login_report=record(WS/'inventory/client455-character-selection-live-taiwan-native.json'),
                fresh_evidence={name:record(WS/'inventory'/f'client455-{name}.json') for name in names},
                prior_runtime=record(WS/'artifacts/client455-progress/before166/manifest.json'),
                post_selection_failure=failure,ordinary_linker_startup_connected=True,
                live_linker_startup_returned=True,actual_fifty_slots_component_tested=True,
                actual_window3_manager_bank4_route_tested=True,boards_created=False,
                full_factory=False,world_entered=False,full_client=False,
                component_frames_visually_inspected=True,source_Create_Board=record(source),
                gaps=ref['gaps'],private_handoff_removed=True,input_exe_executed=False,
                server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    gate_path = WS/'inventory/client455-board-startup-checkpoint.json'
    gate_path.write_text(json.dumps(gate,indent=2)+'\n')
    registry_path=WS/'inventory/client-features.json'
    registry=json.loads(registry_path.read_text())
    for feature in registry['features']:
        if feature.get('runtime_gate_current'):
            feature['runtime_gate_current']=False
    feature=dict(id='CLIENT455-BOARD-STARTUP-166',area='ui',status='partial',runtime_gate_current=True,
                 evidence=[gate_path.relative_to(WS).as_posix(),'inventory/client455-board-startup-reference.json',
                           'inventory/client455-linker-window-native.json'],description=gate['scope'],gaps=gate['gaps'])
    registry['features']=[f for f in registry['features'] if f['id']!=feature['id']]+[feature]
    temporary = registry_path.with_suffix('.json.tmp')
    temporary.write_text(json.dumps(registry,indent=2)+'\n', encoding='ascii')
    temporary.replace(registry_path)
    print('PARTIAL_KNOWN_FAILURE:five-bank startup/50owners/actual manager route PASS;live next UnitTuning skin;world/M9 OPEN')


if __name__ == '__main__':
    main()
