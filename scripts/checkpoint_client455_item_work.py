"""Bind the 455 item windows to the component and ordinary selection evidence."""
import argparse
import json
import re
import struct
from pathlib import Path

from audit_client455_item_work import METHODS
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

    start = symbol('?Create_Board@CGP_MainGame@@')
    stops = [int(row['rva'], 16) for row in failure['candidates'] if row['is_code'] and
             row['symbol'].startswith('?Create_Board@CGP_MainGame@@')]
    require(len(stops) == 1 and stops[0] > start, 'One own board initialization return candidate')
    stop = stops[0]
    body = code(start, stop - start)
    get_board = symbol('?GetBoard@CBoardManager@@')
    calls = []
    for board, window, owner in ((14, 15, 'CItemWorkBoard'), (15, 16, 'CItemUpgradeBoard'),
                                 (16, 13, 'CExchangeBoard')):
        lookup = bytes((0x6a, board, 0xb9)) + b'.{4}\xe8.{4}'
        dispatch = bytes((0x6a, 0, 0x6a, 0, 0x6a, window)) + bytes.fromhex('8b108bc8ff5208')
        matches = [match for match in re.finditer(lookup + re.escape(dispatch), body, re.DOTALL)
                   if start + match.start() + 12 + struct.unpack_from('<i', match[0], 8)[0] == get_board]
        require(len(matches) == 1, 'Own board window dispatch ' + owner)
        match = matches[0]
        table = symbol(f'??_7{owner}@@6B@')
        target = symbol(f'?InitWindow@{owner}@@')
        require(code(table + 8, 4) == struct.pack('<I', BASE + target), 'Own board vtable ' + owner)
        calls.append(dict(board=board, window=window, lookup_rva=hex(start + match.start()),
                          return_rva=hex(start + match.end()), code=match[0].hex(), callee_rva=hex(target),
                          vtable_rva=hex(table), slot=8))
    returns = [int(call['return_rva'], 16) for call in calls]
    require(returns[0] < returns[1] < returns[2] == stop, 'Sequential craft, upgrade and exchange')
    return calls


def bindings(link, ref, symbols):
    root = WS / 'scripts/native'
    sources = {'CGUIItemMakeWindow': root / 'client455_item_make.inc',
               'CGUIItemListWindow': root / 'client455_item_make.inc',
               'CGUIItemUpgradeWindow': root / 'client455_item_upgrade.inc'}
    verified = {row['rva'] for row in ref['references'][0]['functions']}
    rows = []
    for owner, methods in METHODS.items():
        source = sources[owner]
        body = source.read_bytes()
        for method, va in methods.items():
            rva, name = hex(va - BASE), f'{owner}::{method}'
            require(rva in verified and (name + '(').encode() in body, 'Selected source binding ' + name)
            addresses = [hex(a) for a, symbol in symbols if symbol.startswith(f'?{method}@{owner}@@')]
            rows.append(dict(rva=rva, symbol=name, source=record(source), ordinary_symbol_rvas=addresses,
                             standalone_symbol_retained=bool(addresses), complete_equivalence=False))
    save('item-work-bindings', dict(schema_version=1, reference_sha256=ref['references'][0]['sha256'],
                                   architecture='x86', image_base='0x400000', normal_executable=link['executable'],
                                   scope='Partial crafting and upgrade views with controlled inputs.', functions=rows))
    return rows


def check_component(report, frame_count, link_sha):
    require(report['status'] == 'PASS' and report['natural_exit'] == 0 and
            report['normal_link_sha256'] == link_sha and len(report['frames']) == frame_count,
            'Current reviewed component test')
    for key in ('source', 'script', 'exe', 'config', 'output', 'console'):
        check(report[key])
    for item in report['inputs']:
        check(item)
    for frame in report['frames']:
        check(frame)
        check(frame['preview'])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--shop-regression', required=True)
    args = parser.parse_args()
    shop_file = (WS / args.shop_regression).resolve()
    require(shop_file.is_relative_to(WS / 'work/m9'), 'Private merchant regression report')
    shop = json.loads(shop_file.read_text())
    link, ref, native, live = (read(name) for name in ('normal-link', 'item-work-reference', 'item-work-native',
                                                      'character-selection-live-taiwan-native'))
    require(validate_normal_link(link) == 'PASS', 'Current complete own build and link')
    link_sha = sha(path('normal-link'))
    require(live['normal_link_sha256'] == link_sha, 'Current ordinary runtime evidence')
    check_component(native, 4, link_sha)
    check_component(shop, 3, link_sha)
    result = native['native']
    require(result['recipe_groups'] == 3 and result['tabs'] == [9, 5, 2] and result['recipe_slot_capacity'] == 100 and
            result['upgrade_slots'] == 6 and result['window_messages'] == 14 and
            not result['ordinary_recipe_provider'] and not result['transactions_tested'], 'Reviewed controlled item test')
    require(shop['native']['buy_rows'] == shop['native']['trade_rows'] == 21, 'Reviewed merchant paging regression')
    for item in [ref['raw'], *ref['sources'], native['harness']]:
        check(item)
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
    for prefix in ('?SetSprite@CGUIExchangeWindow@@', '?Init@CGUIExchangeWindow@@', '?InitWindow@CExchangeBoard@@'):
        require(any(row['is_code'] and row['symbol'].startswith(prefix) for row in failure['candidates']),
                'Observed exchange stack candidate ' + prefix)
    symbols = own_symbols(link)
    failure.update(ordinary_calls=ordinary_calls(link, failure, symbols), kind='EXCHANGE_AFTER_ITEM_WORK_AND_UPGRADE')
    rows = bindings(link, ref, symbols)
    names = ['item-work-reference', 'item-work-native', 'item-work-bindings', 'normal-preparation', 'normal-build',
             'normal-consumers', 'normal-link', 'own-entry', 'startup-audit', 'startup-taiwan-native',
             'live-launcher-native', 'character-selection-live-taiwan-native', 'live-server']
    evidence = {name: record(path(name)) for name in names}
    evidence['shop-pager-regression'] = record(shop_file)
    scope = ('After accepted character selection, ordinary crafting and upgrade initializers return. '
             'The next failure is the item exchange window skin. Recipe data, transactions and world entry remain open.')
    report = dict(status='PARTIAL_KNOWN_FAILURE', scope=scope, script=record(Path(__file__)),
                  normal_link_sha256=link_sha, normal_executable=link['executable'],
                  runtime_login_report=record(path('character-selection-live-taiwan-native')), fresh_evidence=evidence,
                  prior_runtime=record(WS / 'artifacts/client455-progress/before171/manifest.json'),
                  component_frames_visually_inspected=True, live_item_work_initializers_returned=True,
                  explicit_function_bindings=len(rows), standalone_symbols=sum(r['standalone_symbol_retained'] for r in rows),
                  post_selection_failure=failure, full_factory=False, world_entered=False, full_client=False,
                  private_handoff_removed=True, input_exe_executed=False, server_modified=False,
                  gaps=ref['gaps'], M6='OPEN', M6F='OPEN', M7='OPEN', M9='OPEN')
    save('item-work-checkpoint', report)
    registry_path = WS / 'inventory/client-features.json'
    registry = json.loads(registry_path.read_text())
    identity = 'CLIENT455-ITEM-WORK-171'
    registry['features'] = [row for row in registry['features'] if row['id'] != identity]
    for feature in registry['features']:
        if feature.get('runtime_gate_current'):
            feature['runtime_gate_current'] = False
    registry['features'].append(dict(id=identity, area='ui', status='partial', runtime_gate_current=True,
                                    evidence=[path(n).relative_to(WS).as_posix() for n in
                                              ('item-work-checkpoint', 'item-work-reference', 'item-work-native')],
                                    description=scope, gaps=report['gaps']))
    registry_path.write_text(json.dumps(registry, indent=2) + '\n', encoding='ascii')
    print('PARTIAL_KNOWN_FAILURE: crafting and upgrade initializers returned; exchange, world and M9 open')


if __name__ == '__main__':
    main()
