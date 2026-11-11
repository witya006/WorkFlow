"""Check the live store-list gate, real BSP load and next avatar failure."""
import json
import struct
from pathlib import Path

from build_client455_x87_math import read_va
from checkpoint_client455_party_window import path, read, save
from checkpoint_client455_rvp_effects import check, require, sha
from client455_normal_link_evidence import validate_normal_link
from client455_ui_checkpoint import own_symbols, record
from compare_client_binaries import WS
from inspect_client455_failure import inspect


GAPS = [
    'Stock NPCs received in the store list need typed merchant data and character owners',
    'Avatar animation initialization still calls a legacy normal-item consumer for typed weapon equipment',
    'Start-position exchange, playable world, item owners, guild consumer and full acceptance',
    'The legacy repair request conflicted with the 455 store request and is disabled pending migration',
]


def verify_avatar_failure(link, live):
    failure = inspect(link, live)
    require(failure['exception']['code'] == '0xe06d7363' and not failure['fault_rva_is_own'], 'Observed MSVC exception')
    binary = (WS / link['executable']['file']).read_bytes()
    symbols = own_symbols(link)
    for caller, callee in [('GetNormalItem@CPlayerProc', 'CxxThrowException'),
                           ('SetCombatMode@CAvatar', 'GetNormalItem@CPlayer@@'),
                           ('Create_Avatar@CGP_MainGame', 'LoadAnimaitonData@CPlayer@@')]:
        candidate = next(row for row in failure['candidates'] if row['is_code'] and caller in row['symbol'])
        ret = int(candidate['rva'], 16)
        call = read_va(binary, 0x400000 + ret - 5, 5)
        require(call[0] == 0xe8, 'Direct own call from ' + caller)
        target = ret + struct.unpack('<i', call[1:])[0]
        matches = [name for rva, name in symbols if rva == target and callee in name]
        require(matches, 'Exact own call to ' + callee)
        candidate['verified_call'] = dict(rva=hex(ret - 5), target_rva=hex(target), target_symbol=matches[0])
    return failure


def main():
    names = ('normal-link', 'store-download-reference', 'initial-download-native', 'character-selection-live-taiwan-native')
    link, reference, native, live = (read(name) for name in names)
    link_sha = sha(path('normal-link'))
    require(validate_normal_link(link) == 'PASS' and link_sha == live['normal_link_sha256'] == native['normal_link_sha256']
            and live['executable']['sha256'] == link['executable']['sha256'], 'Exact ordinary client evidence')
    require(native['status'] == 'PASS' and native['native']['store_stride'] == 16 and native['native']['bad_sizes_rejected'],
            'Store fixture layout and size bounds')
    bsp = next(row for row in live['inputs'] if row['file'].lower().endswith('/map/neutralb/neutralb.bsp'))
    for item in [reference['raw'], reference['decompilation'], *reference['sources'], bsp, *(native[key] for key in
                 ('source', 'header', 'script', 'executable', 'console')), *(live[key] for key in
                 ('events', 'captured_frame', 'capture_metadata'))]:
        check(item)
    events = [json.loads(line) for line in (WS / live['events']['file']).read_text().splitlines()]
    messages = [e['value'].removeprefix('RF455 Protocol:') for e in events if e['kind'] == 'debug_string' and
                e.get('value', '').startswith('RF455 Protocol:')]
    expected = ['select-result:0:0:0', 'rx:3:45:157', 'linker-applied:2:0:1', 'tx:12:8:0',
                'rx:12:9:961', 'store-applied:60:0:1', 'map-bsp:0:1:0']
    require(all(e in messages for e in expected) and [messages.index(e) for e in expected] ==
            sorted(messages.index(e) for e in expected), 'Ordered NPC data and real BSP load')
    require(live['debugger_exit'] == 0 and live['live_server']['private_handoff_removed'] and
            any(row.get('own_child_validated') and row.get('sent') for row in live['selection_input']) and
            not any(e.startswith('tx:3:1:') for e in messages), 'Live terminal state before start-position request')
    failure = verify_avatar_failure(link, live)

    prepared = WS / 'work/client455-port/normal/source'
    source = prepared / 'network/netmsgprocessor/itemtrade/cnetmsgprocessor_itemtrade.cpp'
    methods = [('StoreListRequest_clzo', reference['store']['request_rva']),
               ('StoreListResult_clzo', reference['store']['handler_rva'])]
    bindings = []
    symbols = own_symbols(link)
    for name, address in methods:
        rvas = [hex(at) for at, symbol in symbols if symbol.startswith(f'?{name}@CNetMsgProcessor_ItemTrade@@')]
        require(rvas and ('CNetMsgProcessor_ItemTrade::' + name + '(').encode() in source.read_bytes(), 'Live method ' + name)
        bindings.append(dict(rva=address, symbol='CNetMsgProcessor_ItemTrade::' + name, source=record(source),
                             ordinary_symbol_rvas=rvas, complete_equivalence=False))
    save('store-download-bindings', dict(schema_version=1, reference_sha256=reference['references'][0]['sha256'],
                                        architecture='x86', image_base='0x400000', normal_executable=link['executable'],
                                        functions=bindings))
    names += ('store-download-bindings', 'normal-preparation', 'normal-build', 'normal-consumers', 'own-entry',
              'startup-audit', 'startup-taiwan-native', 'live-launcher-native', 'live-server')
    scope = ('The ordinary client accepts the 60-entry merchant list and loads the actual NeutralB BSP. '
             'Avatar creation then stops in a legacy weapon consumer before the start-position request.')
    report = dict(status='PARTIAL_MAP_LOADED_AVATAR_EQUIPMENT_FAILURE', scope=scope, script=record(Path(__file__)),
                  normal_link_sha256=link_sha, normal_executable=link['executable'],
                  runtime_login_report=record(path('character-selection-live-taiwan-native')),
                  fresh_evidence={name: record(path(name)) for name in names},
                  prior_runtime=record(WS / 'artifacts/client455-progress/before179/manifest.json'), observed_sequence=expected,
                  explicit_function_bindings=len(bindings), store=dict(bytes=961, records=60, applied=0, gate_set=True),
                  map=dict(index=0, bsp=bsp, loaded=True), avatar_failure=failure, position_request_sent=False,
                  world_entered=False, full_client=False, private_handoff_removed=True,
                  input_exe_executed=False, server_modified=False, gaps=GAPS, M6='OPEN', M6F='OPEN', M7='OPEN', M9='OPEN')
    save('store-download-checkpoint', report)

    registry_path = WS / 'inventory/client-features.json'
    registry = json.loads(registry_path.read_text())
    identity = 'CLIENT455-STORE-DOWNLOAD-179'
    registry['features'] = [row for row in registry['features'] if row['id'] != identity]
    for feature in registry['features']:
        if feature.get('runtime_gate_current'):
            feature['runtime_gate_current'] = False
    registry['features'].append(dict(id=identity, area='network', status='partial', runtime_gate_current=True,
                                    evidence=[path(name).relative_to(WS).as_posix() for name in
                                              ('store-download-checkpoint', 'store-download-reference', 'initial-download-native')],
                                    description=scope, gaps=GAPS))
    registry_path.write_text(json.dumps(registry, indent=2) + '\n', encoding='ascii')
    print('PARTIAL: actual NeutralB BSP loaded, verified legacy weapon fault during avatar creation')


if __name__ == '__main__':
    main()
