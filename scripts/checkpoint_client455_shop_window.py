"""Record the verified shop window and the next ordinary live startup fault."""
import json
import struct
from pathlib import Path

from build_client455_x87_math import read_va
from checkpoint_client455_rvp_effects import check, require, sha
from client455_normal_link_evidence import validate_normal_link
from client455_ui_checkpoint import own_symbols, record
from compare_client_binaries import WS
from inspect_client455_failure import inspect


BASE = 0x400000


def evidence(name):
    return WS / 'inventory' / f'client455-{name}.json'


def load(name):
    return json.loads(evidence(name).read_text())


def live_calls(link, failure, symbols):
    binary = (WS / link['executable']['file']).read_bytes()

    def symbol(prefix):
        found = [rva for rva, name in symbols if name.startswith(prefix)]
        require(len(found) == 1, 'Unique own symbol ' + prefix)
        return found[0]

    def code(rva, size):
        return read_va(binary, BASE + rva, size)

    start = symbol('?Create_Board@CGP_MainGame@@')
    site = [int(row['rva'], 16) for row in failure['candidates'] if row['is_code'] and
            row['symbol'].startswith('?Create_Board@CGP_MainGame@@')]
    require(len(site) == 1 and start < site[0], 'Own MainGame return site')
    stop = site[0]
    calls = []
    for lookup, init, board, window, owner in (
        (stop - 0x51, stop - 0x38, 9, 7, 'CShopTradeBoard'),
        (stop - 0x1c, stop - 3, 10, 24, 'CPlayerTradeBoard'),
    ):
        prefix = code(lookup, 12)
        require(prefix[:3] == bytes((0x6a, board, 0xb9)) and prefix[7] == 0xe8 and
                lookup + 12 + struct.unpack_from('<i', prefix, 8)[0] == symbol('?GetBoard@CBoardManager@@'),
                'Own MainGame board lookup ' + owner)
        args = bytes.fromhex('6a0068c80000006a') + bytes((window,))
        tail = code(lookup + 12, init + 3 - lookup - 12)
        require(tail.endswith(bytes.fromhex('ff5208')) and args in tail, 'Own MainGame window dispatch')
        table = symbol(f'??_7{owner}@@6B@')
        callee = symbol(f'?InitWindow@{owner}@@')
        require(code(table + 8, 4) == struct.pack('<I', BASE + callee), 'Own board vtable ' + owner)
        calls.append(dict(board=board, window=window, lookup_rva=hex(lookup), call_rva=hex(init),
                          return_rva=hex(init + 3), table_rva=hex(table), slot=8, callee_rva=hex(callee),
                          code=code(lookup, init + 3 - lookup).hex()))
    require(int(calls[-1]['return_rva'], 16) == stop, 'Live candidate belongs to player-trade dispatch')
    return calls


def write_bindings(link, ref, symbols):
    owner = 'CGUIShopWindow'
    path = WS / 'scripts/native/client455_shop_window.inc'
    source = path.read_text()
    verified = {row['rva'] for row in ref['references'][0]['functions']}
    methods = dict(Init=0x6987f0, SetSprite=0x6990a0, SetShopType=0x6991e0, SetTradeMode=0x699300,
                   UpdateShopBoard=0x699d50, SetCurrentShopBoard=0x699eb0, SetDalant=0x69a110,
                   SetGold=0x69a1b0, SetPvp455=0x69a250, SetPoints455=0x69a2f0,
                   TakeInBuyItem=0x699480, TakeInTradeItem=0x699930)
    rows = []
    for method, va in methods.items():
        rva, name = hex(va - BASE), f'{owner}::{method}'
        require(rva in verified and name + '(' in source, 'Selected source binding ' + name)
        addresses = [hex(rva) for rva, symbol in symbols if symbol.startswith(f'?{method}@{owner}@@')]
        rows.append(dict(rva=rva, symbol=name, source=record(path), ordinary_symbol_rvas=addresses,
                         standalone_symbol_retained=bool(addresses), complete_equivalence=False))
    report = dict(schema_version=1, reference_sha256=ref['references'][0]['sha256'], architecture='x86',
                  image_base='0x400000', normal_executable=link['executable'],
                  scope='Partial shop initialization, layout and controlled row paging. Actual merchant gameplay open.',
                  functions=rows)
    evidence('shop-window-bindings').write_text(json.dumps(report, indent=2) + '\n')
    return rows


def main():
    link, ref, native, live = (load(name) for name in ('normal-link', 'shop-window-reference',
                                                        'shop-window-native', 'character-selection-live-taiwan-native'))
    require(validate_normal_link(link) == 'PASS', 'Current complete client compilation and link')
    link_sha = sha(evidence('normal-link'))
    require(native['normal_link_sha256'] == live['normal_link_sha256'] == link_sha, 'Current runtime evidence')
    result = native['native']
    require(native['status'] == 'PASS' and native['natural_exit'] == 0 and len(native['frames']) == 3 and
            result['grid_slots'] == 20 and result['buy_rows'] == result['trade_rows'] == 21, 'Reviewed native result')
    for row in [ref['raw'], *ref['sources'], native['source'], native['script'], native['exe'], native['output'],
                native['console'], native['config'], *native['inputs']]:
        check(row)
    for frame in native['frames']:
        check(frame)
        check(frame['preview'])
    for key in ('events', 'captured_frame', 'capture_metadata'):
        check(live[key])
    require(live['live_server']['private_handoff_removed'] and
            any(row.get('own_child_validated') and row.get('sent') for row in live['selection_input']),
            'Actual own selection input and private handoff cleanup')
    for step in ('RF455 Protocol:tx:1:14:1', 'RF455 Protocol:rx:1:15:22', 'RF455 Protocol:select-result:0:0:0'):
        require(step in live['protocol_observations'], 'Actual live selection ' + step)
    failure = inspect(link, live)
    require(failure['fault_rva_is_own'] and failure['exception']['code'] == '0xc0000005' and
            failure['own_fault']['symbol'].startswith('?GetSpriteXL@CSprite@@'), 'Actual next sprite failure')
    for prefix in ('?SetSprite@CGUITradeWindow@@', '?Init@CGUITradeWindow@@', '?InitWindow@CPlayerTradeBoard@@'):
        require(any(row['symbol'].startswith(prefix) and row['is_code'] for row in failure['candidates']),
                'Actual next failure candidate ' + prefix)
    symbols = own_symbols(link)
    failure.update(ordinary_calls=live_calls(link, failure, symbols),
                   kind='PLAYER_TRADE_SKIN_AFTER_MERCHANT_WINDOW')
    bindings = write_bindings(link, ref, symbols)
    names = ['shop-window-reference', 'shop-window-native', 'shop-window-bindings',
             'normal-preparation', 'normal-build', 'normal-consumers',
             'normal-link', 'own-entry', 'startup-audit', 'startup-taiwan-native', 'live-launcher-native',
             'character-selection-live-taiwan-native', 'live-server']
    scope = ('Ordinary merchant window initialization returns after accepted character selection. '
             'Stock Taiwan layout, four money fields and paging over controlled items pass. '
             'Next live failure is the legacy player-to-player trade window.')
    report = dict(status='PARTIAL_KNOWN_FAILURE', scope=scope, script=record(Path(__file__)),
                  normal_link_sha256=link_sha, normal_executable=link['executable'],
                  runtime_login_report=record(evidence('character-selection-live-taiwan-native')),
                  fresh_evidence={name: record(evidence(name)) for name in names},
                  prior_runtime=record(WS / 'artifacts/client455-progress/before169/manifest.json'),
                  component_frames_visually_inspected=True, live_merchant_initializer_returned=True,
                  explicit_function_bindings=len(bindings),
                  standalone_symbols=sum(row['standalone_symbol_retained'] for row in bindings),
                  post_selection_failure=failure, full_factory=False, world_entered=False, full_client=False,
                  private_handoff_removed=True, input_exe_executed=False, server_modified=False,
                  gaps=ref['gaps'], M6='OPEN', M6F='OPEN', M7='OPEN', M9='OPEN')
    checkpoint = evidence('shop-window-checkpoint')
    checkpoint.write_text(json.dumps(report, indent=2) + '\n')
    registry_path = WS / 'inventory/client-features.json'
    registry = json.loads(registry_path.read_text())
    identity = 'CLIENT455-SHOP-WINDOW-169'
    registry['features'] = [row for row in registry['features'] if row['id'] != identity]
    for feature in registry['features']:
        if feature.get('runtime_gate_current'):
            feature['runtime_gate_current'] = False
    registry['features'].append(dict(id=identity, area='ui', status='partial', runtime_gate_current=True,
                                    evidence=[p.relative_to(WS).as_posix() for p in
                                              (checkpoint, evidence('shop-window-reference'), evidence('shop-window-native'))],
                                    description=scope, gaps=ref['gaps']))
    registry_path.write_text(json.dumps(registry, indent=2) + '\n', encoding='ascii')
    print('PARTIAL_KNOWN_FAILURE: merchant initializer returned; legacy player-trade skin; world and M9 open')


if __name__ == '__main__':
    main()
