"""Record ordinary startup past the 455 service windows and the Linker attachment."""
import json
import re
import struct
from pathlib import Path

from audit_client455_service_windows import METHODS
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
    require(len(stops) == 1 and stops[0] > start, 'One own party return candidate')
    stop = stops[0]
    body = code(start, stop - start)
    get_board = symbol('?GetBoard@CBoardManager@@')

    def window_target(owner):
        table = symbol(f'??_7{owner}@@6B@')
        target = symbol(f'?InitWindow@{owner}@@')
        require(code(table + 8, 4) == struct.pack('<I', BASE + target), 'Own board vtable ' + owner)
        return dict(callee_rva=hex(target), vtable_rva=hex(table), slot=8)

    calls = []
    for board, window, coordinates, owner in ((16, 13, '6a006a00', 'CExchangeBoard'),
                                               (17, 11, '6a006a00', 'CMiningBoard'),
                                               (18, 36, '6a6468c8000000', 'CClassChangeBoard')):
        lookup = re.escape(bytes((0x6a, board, 0xb9))) + b'.{4}\xe8.{4}'
        dispatch = bytes.fromhex(coordinates) + bytes((0x6a, window)) + bytes.fromhex('8b108bc8ff5208')
        matches = [match for match in re.finditer(lookup + re.escape(dispatch), body, re.DOTALL)
                   if start + match.start() + 12 + struct.unpack_from('<i', match[0], 8)[0] == get_board]
        require(len(matches) == 1, 'Own service window dispatch ' + owner)
        match = matches[0]
        calls.append(dict(board=board, window=window, lookup_rva=hex(start + match.start()),
                          return_rva=hex(start + match.end()), code=match[0].hex(), **window_target(owner)))

    attach = symbol('?SetLinkWindow455@CGUIHotKeyBoard@@')
    after_class = int(calls[-1]['return_rva'], 16)
    attach_sites = [at for at in range(after_class, stop - 4) if body[at - start] == 0xe8 and
                    at + 5 + struct.unpack_from('<i', body, at - start + 1)[0] == attach]
    party_call = code(stop - 5, 5)
    require(len(attach_sites) == 1 and party_call == bytes.fromhex('6a13ff5008'),
            'Own Linker attachment and party window 19 call')
    require(int(calls[0]['return_rva'], 16) < int(calls[1]['return_rva'], 16) < after_class < attach_sites[0] < stop,
            'Sequential exchange, mining, promotion, Linker, then party')
    return calls, dict(callee_rva=hex(attach), call_rva=hex(attach_sites[0]),
                       code=code(attach_sites[0], 5).hex()), dict(window=19, return_rva=hex(stop),
                                                               code=party_call.hex(), **window_target('CPartyBoard'))


def bindings(link, ref, symbols):
    native = WS / 'scripts/native'
    gen = WS / 'work/client455-port/normal/source'
    ui = gen / 'userinterface/gamewindow'
    sources = {
        'CGUIExchangeWindow': (native / 'client455_exchange_window.inc', ui / 'npc/guiexchangewindow.cpp'),
        'CExchangeBoard': (native / 'client455_exchange_board.inc', gen / 'gameobject/board/general/cboard_etc.cpp'),
        'CGUIMiningWindow': (native / 'client455_mining_window.inc', ui / 'mining/guiminingwindow.cpp'),
        'CGUIClassChangeWindow': (native / 'client455_class_change_window.inc', ui / 'npc/guiclasschangewindow.cpp'),
        'CGUIHotKeyBoard': (ui / 'guihotkeyboard.cpp',),
        'CNetMsgProcessor_ItemTrade': (gen / 'network/netmsgprocessor/itemtrade/cnetmsgprocessor_itemtrade.cpp',),
    }
    verified = {row['rva'] for row in ref['references'][0]['functions']}
    rows = []
    for owner, methods in METHODS.items():
        for method, va in methods.items():
            rva, name = hex(va - BASE), f'{owner}::{method}'
            source = next((p for p in sources[owner] if (name + '(').encode() in p.read_bytes()), None)
            require(rva in verified and source is not None, 'Selected source binding ' + name)
            addresses = [hex(a) for a, symbol in symbols if symbol.startswith(f'?{method}@{owner}@@')]
            rows.append(dict(rva=rva, symbol=name, source=record(source), ordinary_symbol_rvas=addresses,
                             standalone_symbol_retained=bool(addresses), complete_equivalence=False))
    save('service-windows-bindings', dict(schema_version=1, reference_sha256=ref['references'][0]['sha256'],
                                         architecture='x86', image_base='0x400000', normal_executable=link['executable'],
                                         scope='Partial exchange, mining, promotion and Linker attachment.', functions=rows))
    return rows


def main():
    link, ref, native, live = (read(name) for name in ('normal-link', 'service-windows-reference',
                                                      'service-windows-native', 'character-selection-live-taiwan-native'))
    require(validate_normal_link(link) == 'PASS', 'Current complete own build and link')
    link_sha = sha(path('normal-link'))
    require(native['normal_link_sha256'] == live['normal_link_sha256'] == link_sha, 'Current runtime evidence')
    result = native['native']
    require(native['status'] == 'PASS' and native['natural_exit'] == 0 and len(native['frames']) == 3 and
            result['window_messages'] == 8 and result['mining_ore_choices'] == 5 and
            result['promotion_class_choices'] == 10 and result['promotion_skill_icons'] == 6 and
            result['currency_request_bytes'] == 8 and result['currency_success_receipt_bytes'] == 17 and
            result['single_linker_attachment'] and not result['live_transactions'], 'Reviewed service windows fixture')
    for item in [ref['raw'], *ref['sources'], native['source'], native['script'], native['harness'],
                 native['exe'], native['config'], native['output'], native['console'], *native['inputs']]:
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
            failure['own_fault']['symbol'].startswith('?GetSpriteOrgYL@CSprite@@'), 'Actual next sprite failure')
    for prefix in ('?SetSprite@CGUIPartyMemberInfo@@', '?Init@CGUIPartyMemberInfo@@', '?Init@CGUIPartyWindow@@',
                   '?InitWindow@CPartyBoard@@'):
        require(any(row['is_code'] and row['symbol'].startswith(prefix) for row in failure['candidates']),
                'Observed party stack candidate ' + prefix)
    symbols = own_symbols(link)
    windows, attach, party = ordinary_calls(link, failure, symbols)
    failure.update(ordinary_calls=windows, linker_attach=attach, party_call=party, kind='PARTY_AFTER_SERVICE_WINDOWS')
    rows = bindings(link, ref, symbols)
    names = ['service-windows-reference', 'service-windows-native', 'service-windows-bindings', 'normal-preparation',
             'normal-build', 'normal-consumers', 'normal-link', 'own-entry', 'startup-audit', 'startup-taiwan-native',
             'live-launcher-native', 'character-selection-live-taiwan-native', 'live-server']
    scope = ('After accepted character selection, currency exchange, mining, promotion and the Linker attachment return. '
             'The next failure is the party member sprite. Live transactions and world entry remain open.')
    report = dict(status='PARTIAL_KNOWN_FAILURE', scope=scope, script=record(Path(__file__)),
                  normal_link_sha256=link_sha, normal_executable=link['executable'],
                  runtime_login_report=record(path('character-selection-live-taiwan-native')),
                  fresh_evidence={name: record(path(name)) for name in names},
                  prior_runtime=record(WS / 'artifacts/client455-progress/before172/manifest.json'),
                  intermediate_removed_belt_failure=record(WS / 'artifacts/client455-progress/service-windows172-failure.json'),
                  component_frames_visually_inspected=True, live_service_initializers_returned=True,
                  explicit_function_bindings=len(rows), standalone_symbols=sum(r['standalone_symbol_retained'] for r in rows),
                  post_selection_failure=failure, full_factory=False, world_entered=False, full_client=False,
                  private_handoff_removed=True, input_exe_executed=False, server_modified=False,
                  gaps=ref['gaps'], M6='OPEN', M6F='OPEN', M7='OPEN', M9='OPEN')
    save('service-windows-checkpoint', report)
    registry_path = WS / 'inventory/client-features.json'
    registry = json.loads(registry_path.read_text())
    identity = 'CLIENT455-SERVICE-WINDOWS-172'
    registry['features'] = [row for row in registry['features'] if row['id'] != identity]
    for feature in registry['features']:
        if feature.get('runtime_gate_current'):
            feature['runtime_gate_current'] = False
    registry['features'].append(dict(id=identity, area='ui', status='partial', runtime_gate_current=True,
                                    evidence=[path(n).relative_to(WS).as_posix() for n in
                                              ('service-windows-checkpoint', 'service-windows-reference', 'service-windows-native')],
                                    description=scope, gaps=report['gaps']))
    registry_path.write_text(json.dumps(registry, indent=2) + '\n', encoding='ascii')
    print('PARTIAL_KNOWN_FAILURE: service windows and Linker returned; party, world and M9 open')


if __name__ == '__main__':
    main()
