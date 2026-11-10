"""Corroborate the exact ordinary Skill/Force startup and next Shop failure."""
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
REVIEWED_NATIVE = 'efd26d18afaa52362a78f3c24abc09bfb24955de3b468d98bf135206b8491f05'


def evidence(name):
    return WS / 'inventory' / f'client455-{name}.json'


def load(name):
    return json.loads(evidence(name).read_text())


def startup_calls(link, failure, symbols):
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
    decoded = WS / 'artifacts/client455-progress/skill-force168-own-prefix.txt'
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
        _, board_arg, board_op = instructions[i - 8]
        require(board_op == 'push' and board_arg[0] in (0x6a, 0x68), 'Own board lookup argument')
        board = int.from_bytes(board_arg[1:], 'little', signed=True)
        args = [int.from_bytes(value[1:], 'little', signed=True)
                for _, value, argument_op in instructions[i - 5:i] if argument_op == 'push' and value[0] in (0x6a, 0x68)]
        require(len(args) == 3, 'Own window immediate arguments')
        y, x, window = args
        calls.append(dict(board=board, window=window, position=[x, y], call_rva=hex(at - BASE),
                          return_rva=hex(at + len(raw) - BASE), bytes=raw.hex()))
    last_calls = [row for row in calls if row['board'] in (7, 3, 4, 9)]
    expected = [(7, 5, [200, 60], 'CSkillBoard'), (3, 6, [300, 60], 'CForceBoard'),
                (4, 32, [400, 60], 'CAnimusBoard'), (9, 8, [200, 0], 'CShopTradeBoard')]
    require(len(last_calls) == len(expected), 'Four expected startup calls')
    for call, (board, window, position, name) in zip(last_calls, expected):
        require((call['board'], call['window'], call['position']) == (board, window, position), 'Own sequential board identity')
        table = symbol(f'??_7{name}@@6B@')
        init = symbol(f'?InitWindow@{name}@@')
        require(struct.unpack('<I', read_va(binary, BASE + table + 8, 4))[0] == BASE + init, 'Own board InitWindow vtable slot')
        call.update(table_rva=hex(table), slot=8, callee_rva=hex(init))
    require(int(last_calls[-1]['return_rva'], 16) == end, 'Observed MainGame return site belongs to ShopTradeBoard')
    ret = candidate('?InitWindow@CBaseBoard@@')
    require(read_va(binary, BASE + ret - 3, 3) == b'\xff\x50\x6c', 'Actual own CGUIWindow virtual Init call')
    table = symbol('??_7CGUIShopWindow@@6BCGUIContainer@@@')
    init = symbol('?Init@CGUIShopWindow@@')
    require(struct.unpack('<I', read_va(binary, BASE + table + 0x6c, 4))[0] == BASE + init, 'Own shop window Init vtable slot')
    return dict(main_game_prefix=record(decoded), calls=last_calls,
                shop_virtual_init=dict(return_rva=hex(ret), bytes='ff506c', table_rva=hex(table),
                                       slot=0x6c, callee_rva=hex(init)))


def write_bindings(link, ref, symbols):
    groups = [
        ('CGUISFWindow', 'client455_skill_force_window.inc', dict(CreateSFBoard=0x6c7cb0, Init=0x6c80b0,
            SetSprite=0x6c84e0, SetBound=0x6c8550, SetCurBoardTab=0x6c8a20)),
        ('CGUISkillForceBoard', 'client455_skill_force_window.inc', dict(SetSprite=0x6c7240)),
        ('CGUISkillWindow', 'client455_skill_force_window.inc', dict(Init=0x6c9570, SetSprite=0x6c9790)),
        ('CGUIForceWindow', 'client455_force_window.inc', dict(Init=0x6bff70, SetSprite=0x6c00c0, SetRaceType=0x6c0150)),
        ('CGUISkFcUnit', 'client455_skill_force_row.inc', dict(CGUISkFcUnit=0x6c6200, SetSprite=0x6c6960,
            SetSize=0x6c69e0, SetLevel=0x6c6b70, SetExp=0x6c6f60, SetUnitState=0x6c6a80, SetKind455=0x6c6570)),
    ]
    verified = {row['rva'] for row in ref['references'][0]['functions']}
    functions = []
    for owner, filename, methods in groups:
        path = WS / 'scripts/native' / filename
        for method, target in methods.items():
            name = f'{owner}::{method}'
            prefix = f'??0{owner}@@' if method == owner else f'?{method}@{owner}@@'
            require(hex(target - BASE) in verified and name in path.read_text(), 'Exact source binding ' + name)
            rvas = [hex(rva) for rva, symbol in symbols if symbol.startswith(prefix)]
            functions.append(dict(rva=hex(target - BASE), symbol=name, source=record(path), ordinary_symbol_rvas=rvas,
                                  standalone_symbol_retained=bool(rvas), complete_equivalence=False))
    path = evidence('skill-force-window-bindings')
    path.write_text(json.dumps(dict(schema_version=1, reference_sha256=ref['references'][0]['sha256'],
                                    architecture='x86', image_base='0x400000', normal_executable=link['executable'],
                                    scope='Partial Skill/Force windows and rows. Full production population and gameplay remain open.',
                                    functions=functions), indent=2) + '\n')
    return functions


def main():
    link, ref, native, live = (load(name) for name in ('normal-link', 'skill-force-window-reference',
                                                        'skill-force-window-native', 'character-selection-live-taiwan-native'))
    require(validate_normal_link(link) == 'PASS', 'Exact successful client build and link')
    link_sha = sha(evidence('normal-link'))
    require(native['normal_link_sha256'] == live['normal_link_sha256'] == link_sha, 'Exact current runtime evidence')
    require(sha(evidence('skill-force-window-native')) == REVIEWED_NATIVE and native['status'] == 'PASS' and
            native['native']['real_edf_view_rows'] == 4 and native['native']['force_races'] == 3 and
            native['natural_exit'] == 0 and len(native['frames']) == 3, 'Reviewed frames and actual component checks')
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
            'Addressed live selection input')
    for step in ('RF455 Protocol:tx:1:14:1', 'RF455 Protocol:rx:1:15:22', 'RF455 Protocol:select-result:0:0:0'):
        require(step in live['protocol_observations'], 'Actual live selection ' + step)
    failure = inspect(link, live)
    require(failure['fault_rva_is_own'] and failure['exception']['code'] == '0xc0000005' and
            failure['own_fault']['symbol'].startswith('?GetSpriteXL@CSprite@@'), 'Actual next skin failure')
    for prefix in ('?SetSprite@CGUIShopWindow@@', '?Init@CGUIShopWindow@@', '?InitWindow@CShopTradeBoard@@'):
        require(any(row['symbol'].startswith(prefix) and row['is_code'] for row in failure['candidates']),
                'Actual shop window failure candidate ' + prefix)
    symbols = own_symbols(link)
    failure.update(startup_calls(link, failure, symbols), kind='SHOP_SKIN_AFTER_SKILL_FORCE_WINDOWS',
                   cause='Legacy CGUIShopWindow::Init/SetSprite reaches an invalid sprite frame',
                   whole_client_run_succeeded=False)
    bindings = write_bindings(link, ref, symbols)
    names = ['skill-force-window-reference', 'skill-force-window-native', 'skill-force-window-bindings',
             'normal-preparation', 'normal-build', 'normal-consumers', 'normal-link', 'own-entry',
             'startup-audit', 'startup-taiwan-native', 'live-launcher-native',
             'character-selection-live-taiwan-native', 'live-server']
    report = dict(status='PARTIAL_KNOWN_FAILURE',
                  scope='Skill/Force panel initializers return in ordinary MainGame. Actual localized rows and race presentation are verified through the view API. The next live failure is the legacy ShopWindow skin.',
                  script=record(Path(__file__)), normal_link_sha256=link_sha, normal_executable=link['executable'],
                  runtime_login_report=record(evidence('character-selection-live-taiwan-native')),
                  fresh_evidence={name: record(evidence(name)) for name in names},
                  prior_runtime=record(WS / 'artifacts/client455-progress/before168/manifest.json'),
                  component_frames_visually_inspected=True, live_skill_force_initializers_returned=True,
                  ordinary_sf_population_complete=False, explicit_function_bindings=len(bindings),
                  standalone_symbols=sum(row['standalone_symbol_retained'] for row in bindings),
                  post_selection_failure=failure, boards_created=False, full_factory=False, world_entered=False,
                  full_client=False, private_handoff_removed=True, input_exe_executed=False, server_modified=False,
                  gaps=ref['gaps'], M6='OPEN', M6F='OPEN', M7='OPEN', M9='OPEN')
    path = evidence('skill-force-window-checkpoint')
    path.write_text(json.dumps(report, indent=2) + '\n')
    registry_path = WS / 'inventory/client-features.json'
    registry = json.loads(registry_path.read_text())
    for feature in registry['features']:
        if feature.get('runtime_gate_current'):
            feature['runtime_gate_current'] = False
    feature = dict(id='CLIENT455-SKILL-FORCE-WINDOW-168', area='ui', status='partial', runtime_gate_current=True,
                   evidence=[path.relative_to(WS).as_posix(), 'inventory/client455-skill-force-window-reference.json',
                             'inventory/client455-skill-force-window-native.json'], description=report['scope'], gaps=report['gaps'])
    registry['features'] = [row for row in registry['features'] if row['id'] != feature['id']] + [feature]
    registry_path.write_text(json.dumps(registry, indent=2) + '\n', encoding='ascii')
    print('PARTIAL_KNOWN_FAILURE: Skill/Force startup passed; next ShopWindow skin; world and M9 open')


if __name__ == '__main__':
    main()
