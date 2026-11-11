"""Record the two verified windows and the next ordinary client failure."""
import json
import struct
from pathlib import Path

from audit_client455_trade_ore import METHODS
from build_client455_x87_math import read_va
from checkpoint_client455_rvp_effects import check, require, sha
from client455_normal_link_evidence import validate_normal_link
from client455_ui_checkpoint import own_symbols, record
from compare_client_binaries import WS
from inspect_client455_failure import inspect


BASE = 0x400000


def path(name):
    return WS / 'inventory' / f'client455-{name}.json'


def read(name):
    return json.loads(path(name).read_text())


def save(name, value):
    path(name).write_text(json.dumps(value, indent=2) + '\n')


def ordinary_calls(link, failure, symbols):
    binary = (WS / link['executable']['file']).read_bytes()

    def code(rva, size):
        return read_va(binary, BASE + rva, size)

    def symbol(prefix):
        matches = [rva for rva, name in symbols if name.startswith(prefix)]
        require(len(matches) == 1, 'Unique own symbol ' + prefix)
        return matches[0]

    site = [int(row['rva'], 16) for row in failure['candidates'] if row['is_code'] and
            row['symbol'].startswith('?Create_Board@CGP_MainGame@@')]
    require(len(site) == 1 and symbol('?Create_Board@CGP_MainGame@@') < site[0], 'Own MainGame return site')
    stop = site[0]
    calls = []
    for displacement, board, window, coordinates, name in (
        (0x95, 10, 23, bytes.fromhex('6a0068c8000000'), 'CPlayerTradeBoard'),
        (0x4b, 11, 12, bytes.fromhex('6a006a00'), 'COreProcBoard'),
        (0x19, 14, 15, bytes.fromhex('6a006a00'), 'CItemWorkBoard'),
    ):
        lookup = stop - displacement
        body = code(lookup, 12 + len(coordinates) + 9)
        require(body[:3] == bytes((0x6a, board, 0xb9)) and body[7] == 0xe8 and
                lookup + 12 + struct.unpack_from('<i', body, 8)[0] == symbol('?GetBoard@CBoardManager@@'),
                'Own board lookup ' + name)
        args = coordinates + bytes((0x6a, window)) + bytes.fromhex('8b108bc8ff5208')
        require(body[12:] == args, 'Own board window call ' + name)
        table = symbol(f'??_7{name}@@6B@')
        target = symbol(f'?InitWindow@{name}@@')
        require(code(table + 8, 4) == struct.pack('<I', BASE + target), 'Own board vtable ' + name)
        calls.append(dict(board=board, window=window, lookup_rva=hex(lookup), return_rva=hex(lookup + len(body)),
                          code=body.hex(), callee_rva=hex(target), vtable_rva=hex(table), slot=8))
    require(int(calls[-1]['return_rva'], 16) == stop, 'Item work return candidate')
    return calls


def bindings(link, ref, symbols):
    root = WS / 'scripts/native'
    generated = WS / 'work/client455-port/normal/source/userinterface/gamewindow'
    paths = {
        'CGUITradeWindow': (root / 'client455_player_trade_window.inc', generated / 'player/guitradewindow.cpp'),
        'CGUIOreProcWindow': (root / 'client455_ore_window.inc', generated / 'npc/guioreprocwindow.cpp'),
    }
    verified = {row['rva'] for row in ref['references'][0]['functions']}
    rows = []
    for owner, methods in METHODS.items():
        for method, va in methods.items():
            rva, name = hex(va - BASE), f'{owner}::{method}'
            source = next((p for p in paths[owner] if (name + '(').encode() in p.read_bytes()), None)
            require(rva in verified and source is not None, 'Selected source binding ' + name)
            addresses = [hex(a) for a, symbol in symbols if symbol.startswith(f'?{method}@{owner}@@')]
            rows.append(dict(rva=rva, symbol=name, source=record(source), ordinary_symbol_rvas=addresses,
                             standalone_symbol_retained=bool(addresses), complete_equivalence=False))
    save('trade-ore-bindings', dict(schema_version=1, reference_sha256=ref['references'][0]['sha256'],
                                   architecture='x86', image_base='0x400000', normal_executable=link['executable'],
                                   scope='Partial player trade and ore view. Live transactions remain open.', functions=rows))
    return rows


def main():
    link, ref, native, live = (read(name) for name in ('normal-link', 'trade-ore-reference',
                                                      'trade-ore-native', 'character-selection-live-taiwan-native'))
    require(validate_normal_link(link) == 'PASS', 'Current complete own build and link')
    link_sha = sha(path('normal-link'))
    require(native['normal_link_sha256'] == live['normal_link_sha256'] == link_sha, 'Current runtime evidence')
    result = native['native']
    require(native['status'] == 'PASS' and native['natural_exit'] == 0 and len(native['frames']) == 3 and
            result['trade_slots_per_side'] == 15 and result['trade_messages'] == 3 and result['ore_rows'] == 21 and
            result['ore_capacity'] == 40, 'Reviewed component test')
    for item in [ref['raw'], *ref['sources'], native['source'], native['script'], native['exe'], native['config'],
                 native['output'], native['console'], *native['inputs']]:
        check(item)
    for frame in native['frames']:
        check(frame)
        check(frame['preview'])
    for key in ('events', 'captured_frame', 'capture_metadata'):
        check(live[key])
    require(live['live_server']['private_handoff_removed'] and
            any(row.get('own_child_validated') and row.get('sent') for row in live['selection_input']),
            'Actual own selection input and handoff cleanup')
    for event in ('RF455 Protocol:tx:1:14:1', 'RF455 Protocol:rx:1:15:22', 'RF455 Protocol:select-result:0:0:0'):
        require(event in live['protocol_observations'], 'Actual accepted selection ' + event)
    failure = inspect(link, live)
    require(failure['fault_rva_is_own'] and failure['exception']['code'] == '0xc0000005' and
            failure['own_fault']['symbol'].startswith('?GetSpriteXL@CSprite@@'), 'Actual next sprite failure')
    for prefix in ('?SetSprite@CGUIItemMakeWindow@@', '?Init@CGUIItemMakeWindow@@', '?InitWindow@CItemWorkBoard@@'):
        require(any(row['is_code'] and row['symbol'].startswith(prefix) for row in failure['candidates']),
                'Observed item work stack candidate ' + prefix)
    symbols = own_symbols(link)
    failure.update(ordinary_calls=ordinary_calls(link, failure, symbols), kind='ITEM_WORK_AFTER_TRADE_AND_ORE')
    rows = bindings(link, ref, symbols)
    names = ['trade-ore-reference', 'trade-ore-native', 'trade-ore-bindings', 'normal-preparation', 'normal-build',
             'normal-consumers', 'normal-link', 'own-entry', 'startup-audit', 'startup-taiwan-native',
             'live-launcher-native', 'character-selection-live-taiwan-native', 'live-server']
    scope = ('After accepted character selection, ordinary player trade and ore initializers return. '
             'The next live failure is the legacy item crafting skin. Transactions and world entry remain open.')
    report = dict(status='PARTIAL_KNOWN_FAILURE', scope=scope, script=record(Path(__file__)),
                  normal_link_sha256=link_sha, normal_executable=link['executable'],
                  runtime_login_report=record(path('character-selection-live-taiwan-native')),
                  fresh_evidence={name: record(path(name)) for name in names},
                  prior_runtime=record(WS / 'artifacts/client455-progress/before170/manifest.json'),
                  component_frames_visually_inspected=True, live_trade_ore_initializers_returned=True,
                  explicit_function_bindings=len(rows), standalone_symbols=sum(r['standalone_symbol_retained'] for r in rows),
                  post_selection_failure=failure, full_factory=False, world_entered=False, full_client=False,
                  private_handoff_removed=True, input_exe_executed=False, server_modified=False,
                  gaps=ref['gaps'], M6='OPEN', M6F='OPEN', M7='OPEN', M9='OPEN')
    save('trade-ore-checkpoint', report)
    registry_path = WS / 'inventory/client-features.json'
    registry = json.loads(registry_path.read_text())
    identity = 'CLIENT455-TRADE-ORE-170'
    registry['features'] = [row for row in registry['features'] if row['id'] != identity]
    for feature in registry['features']:
        if feature.get('runtime_gate_current'):
            feature['runtime_gate_current'] = False
    registry['features'].append(dict(id=identity, area='ui', status='partial', runtime_gate_current=True,
                                    evidence=[path(n).relative_to(WS).as_posix() for n in
                                              ('trade-ore-checkpoint', 'trade-ore-reference', 'trade-ore-native')],
                                    description=scope, gaps=report['gaps']))
    registry_path.write_text(json.dumps(registry, indent=2) + '\n', encoding='ascii')
    print('PARTIAL_KNOWN_FAILURE: trade and ore initializers returned; next ItemMakeWindow; world and M9 open')


if __name__ == '__main__':
    main()
