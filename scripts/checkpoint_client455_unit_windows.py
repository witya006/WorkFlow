"""Tie the recovered unit panels to the current native and live client runs."""
import json
import re
import struct
import subprocess
from pathlib import Path

from build_client455_x87_math import read_va
from checkpoint_client455_rvp_effects import check, require, sha
from client455_normal_link_evidence import validate_normal_link
from client455_ui_checkpoint import own_symbols, record
from compare_client_binaries import WS
from inspect_client455_failure import inspect


BASE = 0x400000
REVIEWED_NATIVE = '8fb5028ee8c0c2629c88e7c68dddb99cdf8b9e1a6ceff72d3ab5de6ad1d81428'


def evidence(name):
    return WS / 'inventory' / f'client455-{name}.json'


def load(name):
    return json.loads(evidence(name).read_text())


def startup_calls(link, failure):
    symbols = own_symbols(link)
    binary = (WS / link['executable']['file']).read_bytes()

    def symbol(prefix):
        candidates = [rva for rva, name in symbols if name.startswith(prefix)]
        require(len(candidates) == 1, 'Unique own symbol ' + prefix)
        return candidates[0]

    def candidate(prefix):
        rows = [row for row in failure['candidates'] if row['is_code'] and row['symbol'].startswith(prefix)]
        require(len(rows) == 1, 'Observed candidate ' + prefix)
        return int(rows[0]['rva'], 16)

    start = symbol('?Create_Board@CGP_MainGame@@')
    end = candidate('?Create_Board@CGP_MainGame@@')
    compiler = Path(json.loads((WS / 'inventory/msvc-verification.json').read_text())['compiler_path'].splitlines()[0])
    result = subprocess.run([str(compiler.with_name('dumpbin.exe')), '/DISASM:BYTES',
                             f'/RANGE:0x{BASE + start:x},0x{BASE + end:x}', str(WS / link['executable']['file'])],
                            capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
    require(result.returncode == 0, 'Own MainGame startup disassembly')
    decoded = WS / 'artifacts/client455-progress/unit167-own-prefix.txt'
    decoded.write_bytes(result.stdout)
    instructions = []
    for line in result.stdout.decode(errors='replace').splitlines():
        match = re.match(r'^\s+([0-9A-F]{8}): ((?:[0-9A-F]{2} )+)\s+(\w+)\s*', line)
        if match:
            at, raw = int(match[1], 16), bytes.fromhex(match[2])
            require(raw == read_va(binary, at, len(raw)), 'Own disassembled bytes')
            instructions.append((at, raw, match[3]))

    get_board = BASE + symbol('?GetBoard@CBoardManager@@')
    calls = []
    for i, (at, raw, op) in enumerate(instructions):
        if i < 8 or raw != b'\xff\x52\x08' or op != 'call':
            continue
        lookup_at, lookup, lookup_op = instructions[i - 6]
        if lookup_op != 'call' or len(lookup) != 5 or lookup[0] != 0xe8:
            continue
        if lookup_at + 5 + struct.unpack('<i', lookup[1:])[0] != get_board:
            continue
        arguments = []
        for j in (8, 3, 4, 5):
            _, value, argument_op = instructions[i - j]
            require(argument_op == 'push' and value[0] in (0x6a, 0x68), 'Own window immediate arguments')
            arguments.append(int.from_bytes(value[1:], 'little', signed=True))
        calls.append(dict(board=arguments[0], window=arguments[1], position=arguments[2:],
                          call_rva=hex(at - BASE), return_rva=hex(at + len(raw) - BASE), bytes=raw.hex()))
    required = [(12, 34, [300, 0], 'CUnitTuningBoard'), (13, 35, [300, 100], 'CUnitStorehouseBoard'),
                (1, 90, [0, 0], 'CEquipBoard'), (7, 6, [200, 60], 'CSkillBoard')]
    require(len(calls) >= 4, 'Four sequential own board InitWindow calls')
    calls = calls[-4:]
    for call, (board, window, position, name) in zip(calls, required):
        require((call['board'], call['window'], call['position']) == (board, window, position), 'Own sequential board identity')
        table = symbol(f'??_7{name}@@6B@')
        init = symbol(f'?InitWindow@{name}@@')
        require(struct.unpack('<I', read_va(binary, BASE + table + 8, 4))[0] == BASE + init, 'Own board InitWindow vtable slot')
        call.update(table_rva=hex(table), slot=8, callee_rva=hex(init))
    require(int(calls[-1]['return_rva'], 16) == end, 'Observed MainGame return site belongs to SkillBoard')
    ret = candidate('?InitWindow@CBaseBoard@@')
    require(read_va(binary, BASE + ret - 3, 3) == b'\xff\x50\x6c', 'Actual own CGUIWindow virtual Init call')
    skill_table = symbol('??_7CGUISkillWindow@@6BCGUIContainer@@@')
    skill_init = symbol('?Init@CGUISkillWindow@@')
    require(struct.unpack('<I', read_va(binary, BASE + skill_table + 0x6c, 4))[0] == BASE + skill_init, 'Own skill window Init vtable slot')
    return dict(main_game_prefix=record(decoded), calls=calls,
                skill_virtual_init=dict(return_rva=hex(ret), bytes='ff506c', table_rva=hex(skill_table),
                                        slot=0x6c, callee_rva=hex(skill_init)))


def write_bindings(link, ref):
    functions = []
    symbols = own_symbols(link)
    verified = {row['rva'] for row in ref['references'][0]['functions']}
    groups = [
        ('CGUIUnitTuningWindow', 'client455_unit_tuning.inc', {
            'Init': 0x72bb90, 'SetSprite': 0x72d950, 'Select_Parts': 0x72e3d0, 'Select_Bullet': 0x72e460,
            'SetPartsBuyingState': 0x72e750, 'SetBulletBuyingState': 0x72e9e0,
            'SetBackpackBulletBuyingState': 0x72ed70, 'Enable_Shouler_Bullet': 0x72e940,
            'Enable_BackPack_Bullet': 0x72ec30,
        }),
        ('CGUIUnitStoreWindow', 'client455_unit_storehouse.inc', {'Init': 0x72a700, 'SetSprite': 0x72a9f0}),
    ]
    for owner, filename, methods in groups:
        path = WS / 'scripts/native' / filename
        for method, target in methods.items():
            name = f'{owner}::{method}'
            require(hex(target - BASE) in verified and name in path.read_text(), 'Exact unit source binding ' + name)
            rvas = [hex(rva) for rva, symbol in symbols if symbol.startswith(f'?{method}@{owner}@@')]
            require(len(rvas) == (0 if method == 'Select_Parts' else 1), 'Expected standalone own unit symbols')
            functions.append(dict(rva=hex(target - BASE), symbol=name, source=record(path), ordinary_symbol_rvas=rvas,
                                  standalone_symbol_retained=bool(rvas), complete_equivalence=False))
    path = evidence('unit-windows-bindings')
    path.write_text(json.dumps(dict(schema_version=1, reference_sha256=ref['references'][0]['sha256'],
                                    architecture='x86', image_base='0x400000', normal_executable=link['executable'],
                                    scope='Partial unit view implementations; selected runtime coverage, complete unit gameplay open',
                                    functions=functions), indent=2) + '\n')
    return path


def main():
    link, ref, native, live = (load(name) for name in ('normal-link', 'unit-windows-reference',
                                                       'unit-windows-native', 'character-selection-live-taiwan-native'))
    require(validate_normal_link(link) == 'PASS', 'Exact successful normal client link')
    link_sha = sha(evidence('normal-link'))
    require(native['normal_link_sha256'] == live['normal_link_sha256'] == link_sha, 'Current client run evidence')
    require(sha(evidence('unit-windows-native')) == REVIEWED_NATIVE and native['status'] == 'PASS' and
            native['native']['observer_messages'] == 3 and native['natural_exit'] == 0 and len(native['frames']) == 3,
            'Three exact reviewed unit frames and native observations')
    for row in [ref['raw'], *ref['sources'], *ref['generated'], native['source'], native['script'],
                native['exe'], native['output'], native['console'], native['map'], *native['inputs']]:
        check(row)
    for frame in native['frames']:
        check(frame)
        check(frame['preview'])
    require(live['first_login_frame_captured'] and live['login_render_returned_after_capture'] and
            live['live_server']['private_handoff_removed'], 'Actual pre-Enter frame and private cleanup')
    for key in ('events', 'captured_frame', 'capture_metadata'):
        check(live[key])
    require(any(row.get('own_child_validated') and row.get('sent') for row in live['selection_input']),
            'Addressed live selection action')
    for step in ('RF455 Protocol:tx:1:14:1', 'RF455 Protocol:rx:1:15:22', 'RF455 Protocol:select-result:0:0:0'):
        require(step in live['protocol_observations'], 'Actual live selection ' + step)
    failure = inspect(link, live)
    require(failure['fault_rva_is_own'] and failure['exception']['code'] == '0xc0000005' and
            failure['own_fault']['symbol'].startswith('?GetSpriteXL@CSprite@@'), 'Actual next skin failure')
    for prefix in ('?SetSprite@CGUISFWindow@@', '?SetSprite@CGUISkillWindow@@', '?Init@CGUISkillWindow@@'):
        require(any(row['symbol'].startswith(prefix) and row['is_code'] for row in failure['candidates']),
                'Actual skill window failure candidate ' + prefix)
    failure.update(startup_calls(link, failure), kind='SKILL_SKIN_AFTER_UNIT_WINDOWS',
                   cause='Legacy CGUISkillWindow::Init/SetSprite uses CGUISFWindow::SetSprite and reaches an invalid sprite frame',
                   whole_client_run_succeeded=False)
    write_bindings(link, ref)
    names = ['unit-windows-reference', 'unit-windows-native', 'unit-windows-bindings', 'normal-preparation', 'normal-build',
             'normal-consumers', 'normal-link', 'own-entry', 'startup-audit', 'startup-taiwan-native',
             'live-launcher-native', 'character-selection-live-taiwan-native', 'live-server']
    report = dict(status='PARTIAL_KNOWN_FAILURE',
                  scope='UnitTuning and UnitStorehouse actual stock views, pack activation and three HWND messages tested. Live selection passes both initializers and reaches SkillWindow skin failure.',
                  script=record(Path(__file__)), normal_link_sha256=link_sha, normal_executable=link['executable'],
                  runtime_login_report=record(evidence('character-selection-live-taiwan-native')),
                  fresh_evidence={name: record(evidence(name)) for name in names},
                  prior_runtime=record(WS / 'artifacts/client455-progress/before167/manifest.json'),
                  component_frames_visually_inspected=True, live_unit_windows_returned_before_skill=True,
                  post_selection_failure=failure, boards_created=False, full_factory=False, world_entered=False,
                  full_client=False, private_handoff_removed=True, input_exe_executed=False, server_modified=False,
                  gaps=ref['gaps'], M6='OPEN', M6F='OPEN', M7='OPEN', M9='OPEN')
    path = evidence('unit-windows-checkpoint')
    path.write_text(json.dumps(report, indent=2) + '\n')
    registry_path = WS / 'inventory/client-features.json'
    registry = json.loads(registry_path.read_text())
    for feature in registry['features']:
        if feature.get('runtime_gate_current'):
            feature['runtime_gate_current'] = False
    feature = dict(id='CLIENT455-UNIT-WINDOWS-167', area='ui', status='partial', runtime_gate_current=True,
                   evidence=[path.relative_to(WS).as_posix(), 'inventory/client455-unit-windows-reference.json',
                             'inventory/client455-unit-windows-native.json'], description=report['scope'], gaps=report['gaps'])
    registry['features'] = [row for row in registry['features'] if row['id'] != feature['id']] + [feature]
    registry_path.write_text(json.dumps(registry, indent=2) + '\n', encoding='ascii')
    print('PARTIAL_KNOWN_FAILURE: UnitTuning and UnitStorehouse returned; next SkillWindow skin; world and M9 open')


if __name__ == '__main__':
    main()
