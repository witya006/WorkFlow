"""Bind the mastery through miner runtime sequence to the exact client build."""
import json
from pathlib import Path

from checkpoint_client455_party_window import path, read, save
from checkpoint_client455_rvp_effects import check, require, sha
from client455_normal_link_evidence import validate_normal_link
from client455_ui_checkpoint import own_symbols, record
from compare_client_binaries import WS


HANDLERS = (
    ('InitMsg_CumDownloadResult_zocl', '0x16d960'),
    ('InitMsg_QuestDownloadResult455', '0x16e0e0'),
    ('InitMsg_SpecialDownloadResult455', '0x16e470'),
    ('InitMsg_SpecialDownloadResult455', '0x16e880'),
    ('InitMsg_MinerDownloadResult455', '0x168e90'),
)


def bindings(link, reference):
    verified = {row['rva'] for row in reference['references'][0]['functions']}
    verified.update(row['handler_rva'] for row in reference['routes'])
    source = WS / 'scripts/native/client455_initial_download.inc'
    code = source.read_bytes()
    symbols = own_symbols(link)
    rows = []
    for name, rva in HANDLERS:
        method = 'CNetworkMgr::' + name
        addresses = [hex(at) for at, symbol in symbols if symbol.startswith(f'?{name}@CNetworkMgr@@')]
        require(rva in verified and (method + '(').encode() in code and addresses, 'Linked binding ' + method)
        rows.append(dict(rva=rva, symbol=method, source=record(source), ordinary_symbol_rvas=addresses,
                         complete_equivalence=False))
    save('mastery-quests-bindings', dict(schema_version=1, reference_sha256=reference['references'][0]['sha256'],
                                        architecture='x86', image_base='0x400000', normal_executable=link['executable'],
                                        scope='Selected mastery, quest, unit, Animus and miner initial download handlers.',
                                        functions=rows))
    return rows


def main():
    names = ('normal-link', 'mastery-quests-reference', 'initial-download-native', 'character-selection-live-taiwan-native')
    link, reference, native, live = (read(name) for name in names)
    require(validate_normal_link(link) == 'PASS', 'Complete own build and link')
    link_sha = sha(path('normal-link'))
    require(live['normal_link_sha256'] == native['normal_link_sha256'] == link_sha and
            live['executable']['sha256'] == link['executable']['sha256'], 'Exact binary for both runtime checks')
    dimensions = ('mastery_minimum', 'quest_stride', 'unit_stride', 'animus_stride', 'miner_stride')
    require(native['status'] == 'PASS' and tuple(native['native'][key] for key in dimensions) == (322, 14, 67, 18, 5)
            and native['native']['bad_sizes_rejected'], 'Native wire dimensions and malformed input fixtures')
    for item in [reference['raw'], *reference['sources'], *(native[key] for key in
                 ('source', 'header', 'script', 'executable', 'console')), *(live[key] for key in
                 ('events', 'captured_frame', 'capture_metadata'))]:
        check(item)
    events = [json.loads(line) for line in (WS / live['events']['file']).read_text().splitlines()]
    prefix = 'RF455 Protocol:'
    messages = [event['value'].removeprefix(prefix) for event in events if event.get('kind') == 'debug_string' and
                event.get('value', '').startswith(prefix)]
    end = next((event for event in messages if event.startswith('rx:3:45:')), '')
    require(bool(end), 'Linker response observed')
    expected = ['tx:1:14:1', 'rx:1:15:22', 'select-result:0:0:0', 'inventory-applied:3:21:0', 'force-applied:82:0:0',
                'rx:3:8:322', 'mastery-applied:0:0:0', 'tx:3:11:0', 'rx:3:12:100', 'quest-decoded:0:7:7',
                'tx:3:13:0', 'rx:3:14:1', 'special-decoded:14:0:0', 'tx:3:54:0', 'rx:3:55:2']
    miner = next((event for event in messages if event.startswith('miner-decoded:')), '')
    require(miner.split(':')[2:] == ['0', '0'], 'Empty miner list observed and decoded')
    expected += [miner, 'tx:3:46:0', end]
    require(all(event in messages for event in expected) and [messages.index(event) for event in expected] ==
            sorted(messages.index(event) for event in expected), 'Ordered character downloads through Linker')
    require(live['debugger_exit'] == 0 and live['live_server']['private_handoff_removed'] and
            any(row.get('own_child_validated') and row.get('sent') for row in live['selection_input']) and
            not any(event['kind'] == 'exception' and not event.get('first_chance') for event in events),
            'Live selection completed with no fatal exception and the private handoff removed')
    rows = bindings(link, reference)
    names += ('mastery-quests-bindings', 'normal-preparation', 'normal-build', 'normal-consumers', 'own-entry',
              'startup-audit', 'startup-taiwan-native', 'live-launcher-native', 'live-server')
    scope = ('The ordinary client applies supported mastery fields, resolves seven quest catalog records, '
             'handles empty unit and miner lists and receives the 3/45 Linker reply.')
    report = dict(status='PARTIAL_WAITING_FOR_LINKER_AND_ITEM_OWNERS', scope=scope, script=record(Path(__file__)),
                  normal_link_sha256=link_sha, normal_executable=link['executable'],
                  runtime_login_report=record(path('character-selection-live-taiwan-native')),
                  fresh_evidence={name: record(path(name)) for name in names},
                  prior_runtime=record(WS / 'artifacts/client455-progress/before176/manifest.json'),
                  explicit_function_bindings=len(rows), observed_sequence=expected,
                  inventory=dict(records=21, items_placed=0), force=dict(records=82, items_applied=0),
                  mastery=dict(bytes=322, decoded=True, skill_owners_applied=0, ores_applied=0),
                  quests=dict(decoded=7, catalog_resolved=7, journal_restored=False),
                  units=dict(records=0, applied=0), miner=dict(records=0, applied=0),
                  linker=dict(bytes=int(end.split(':')[-1]), received=True, decoded=False),
                  world_entered=False, full_client=False, private_handoff_removed=True,
                  input_exe_executed=False, server_modified=False, gaps=reference['gaps'],
                  M6='OPEN', M6F='OPEN', M7='OPEN', M9='OPEN')
    save('mastery-quests-checkpoint', report)

    registry_path = WS / 'inventory/client-features.json'
    registry = json.loads(registry_path.read_text())
    identity = 'CLIENT455-MASTERY-QUESTS-176'
    registry['features'] = [row for row in registry['features'] if row['id'] != identity]
    for feature in registry['features']:
        if feature.get('runtime_gate_current'):
            feature['runtime_gate_current'] = False
    registry['features'].append(dict(id=identity, area='network', status='partial', runtime_gate_current=True,
                                    evidence=[path(name).relative_to(WS).as_posix() for name in
                                              ('mastery-quests-checkpoint', 'mastery-quests-reference',
                                               'initial-download-native')], description=scope, gaps=report['gaps']))
    registry_path.write_text(json.dumps(registry, indent=2) + '\n', encoding='ascii')
    print('PARTIAL: reached Linker 3/45, world and item owners open')


if __name__ == '__main__':
    main()
