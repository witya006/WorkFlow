"""Bind initial-download fixtures and live exchange to the exact client build."""
import json
from pathlib import Path

from checkpoint_client455_party_window import path, read, save
from checkpoint_client455_rvp_effects import check, require, sha
from client455_normal_link_evidence import validate_normal_link
from client455_ui_checkpoint import own_symbols, record
from compare_client_binaries import WS


METHODS = {
    'InitMsg_BaseDownloadResult_zocl': 0x16bea0,
    'InitMsg_InvenDownloadRequest_clzo': 0x16cfe0,
    'InitMsg_InvenDownloadResult_zocl': 0x16d080,
    'InitMsg_ForceDownloadRequest_clzo': 0x16de90,
    'InitMsg_ForceDownloadResult_zocl': 0x16df30,
    'InitMsg_CumDownloadRequest_clzo': 0x16d8c0,
}


def bindings(link, reference):
    verified = {row['rva'] for row in reference['references'][0]['functions']}
    source = WS / 'work/client455-port/normal/source/network/cnetworkmgr_systemmsg.cpp'
    native = WS / 'scripts/native/client455_initial_download.inc'
    symbols = own_symbols(link)
    rows = []
    for name, rva in METHODS.items():
        method = 'CNetworkMgr::' + name
        file = native if name.endswith('Result_zocl') else source
        require(hex(rva) in verified and (method + '(').encode() in file.read_bytes(), 'Selected binding ' + method)
        addresses = [hex(at) for at, symbol in symbols if symbol.startswith(f'?{name}@CNetworkMgr@@')]
        if name.endswith('Result_zocl'):
            require(bool(addresses), 'Linked consumer ' + method)
        rows.append(dict(rva=hex(rva), symbol=method, source=record(file), ordinary_symbol_rvas=addresses,
                         standalone_symbol_retained=bool(addresses), complete_equivalence=False))
    save('initial-download-bindings', dict(schema_version=1, reference_sha256=reference['references'][0]['sha256'],
                                           architecture='x86', image_base='0x400000', normal_executable=link['executable'],
                                           scope='Initial download wire and partial data application.', functions=rows))
    return rows


def main():
    link, reference, native, live = (read(name) for name in ('normal-link', 'initial-download-reference',
                                                           'initial-download-native', 'character-selection-live-taiwan-native'))
    require(validate_normal_link(link) == 'PASS', 'Current complete own build and link')
    link_sha = sha(path('normal-link'))
    require(live['normal_link_sha256'] == native['normal_link_sha256'] == link_sha and
            live['executable']['sha256'] == link['executable']['sha256'], 'Exact binary for both runtime checks')
    require(native['status'] == 'PASS' and native['native']['bad_sizes_rejected'] and
            native['native']['empty_and_error_results'], 'Bounded native decoder fixtures')
    for item in [reference['raw'], *reference['sources'], *(native[key] for key in
                 ('source', 'header', 'script', 'executable', 'console')), *(live[key] for key in
                 ('events', 'captured_frame', 'capture_metadata'))]:
        check(item)
    events = [json.loads(line) for line in (WS / live['events']['file']).read_text().splitlines()]
    prefix = 'RF455 Protocol:'
    messages = [e['value'].removeprefix(prefix) for e in events if e.get('kind') == 'debug_string' and
                e.get('value', '').startswith(prefix)]
    expected = ['tx:1:14:1', 'rx:1:15:22', 'select-result:0:0:0', 'tx:3:3:0', 'rx:3:4:431',
                'base-applied:0:0:0', 'tx:3:5:0', 'rx:3:6:633', 'inventory-applied:3:21:0',
                'tx:3:9:0', 'rx:3:10:904', 'force-applied:82:0:0', 'tx:3:7:0', 'rx:3:8:322']
    require(all(e in messages for e in expected) and [messages.index(e) for e in expected] ==
            sorted(messages.index(e) for e in expected), 'Observed initial downloads in order')
    require(live['debugger_exit'] == 0 and live['live_server']['private_handoff_removed'] and
            any(row.get('own_child_validated') and row.get('sent') for row in live['selection_input']) and
            not any(e['kind'] == 'exception' and not e.get('first_chance') for e in events), 'Live selection terminal state')
    rows = bindings(link, reference)
    names = ['initial-download-reference', 'initial-download-native', 'initial-download-bindings', 'normal-preparation',
             'normal-build', 'normal-consumers', 'normal-link', 'own-entry', 'startup-audit', 'startup-taiwan-native',
             'live-launcher-native', 'character-selection-live-taiwan-native', 'live-server']
    scope = ('The ordinary client applies the supported base fields and reaches the 322-byte 3/8 mastery reply. '
             'The live inventory and Force records pass wire decoding, while the legacy item providers resolve none.')
    private = WS / 'artifacts/client455-progress'
    report = dict(status='PARTIAL_WAITING_FOR_MASTERY_AND_ITEM_OWNERS', scope=scope, script=record(Path(__file__)),
                  normal_link_sha256=link_sha, normal_executable=link['executable'],
                  runtime_login_report=record(path('character-selection-live-taiwan-native')),
                  fresh_evidence={name: record(path(name)) for name in names},
                  prior_runtime=record(private / 'before175/manifest.json'),
                  next_handlers_analysis=record(private / 'initial-download175-next-idalib.json'),
                  explicit_function_bindings=len(rows), observed_sequence=expected,
                  base=dict(bytes=431, decoded=True, map_index=0, equipment_resolved=0),
                  inventory=dict(bytes=633, bags=3, records=21, items_placed=0),
                  force=dict(bytes=904, records=82, items_applied=0), mastery=dict(bytes=322, received=True, decoded=False),
                  world_entered=False, full_client=False, private_handoff_removed=True,
                  input_exe_executed=False, server_modified=False, gaps=reference['gaps'],
                  M6='OPEN', M6F='OPEN', M7='OPEN', M9='OPEN')
    save('initial-download-checkpoint', report)

    registry_path = WS / 'inventory/client-features.json'
    registry = json.loads(registry_path.read_text())
    identity = 'CLIENT455-INITIAL-DOWNLOAD-175'
    registry['features'] = [row for row in registry['features'] if row['id'] != identity]
    for feature in registry['features']:
        if feature.get('runtime_gate_current'):
            feature['runtime_gate_current'] = False
    registry['features'].append(dict(id=identity, area='network', status='partial', runtime_gate_current=True,
                                    evidence=[path(n).relative_to(WS).as_posix() for n in
                                              ('initial-download-checkpoint', 'initial-download-reference', 'initial-download-native')],
                                    description=scope, gaps=report['gaps']))
    registry_path.write_text(json.dumps(registry, indent=2) + '\n', encoding='ascii')
    print('PARTIAL: base, inventory and Force wire decoded; live owners and 3/8 consumer open')


if __name__ == '__main__':
    main()
