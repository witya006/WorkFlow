"""Corroborate ordinary client Linker application and the live follow-up replies."""
import json
from pathlib import Path

from checkpoint_client455_party_window import path, read, save
from checkpoint_client455_rvp_effects import check, require, sha
from client455_normal_link_evidence import validate_normal_link
from client455_ui_checkpoint import own_symbols, record
from compare_client_binaries import WS


def main():
    names = ('normal-link', 'linker-download-reference', 'initial-download-native', 'character-selection-live-taiwan-native')
    link, reference, native, live = (read(name) for name in names)
    link_sha = sha(path('normal-link'))
    require(validate_normal_link(link) == 'PASS' and link_sha == live['normal_link_sha256'] == native['normal_link_sha256']
            and live['executable']['sha256'] == link['executable']['sha256'], 'Exact ordinary client evidence')
    require(native['status'] == 'PASS' and native['native']['linker_bytes'] == 157 and native['native']['bad_sizes_rejected'],
            'Linker layout and length fixture')
    for item in [reference['raw'], reference['decompilation'], *reference['sources'], *(native[key] for key in
                 ('source', 'header', 'script', 'executable', 'console')), *(live[key] for key in
                 ('events', 'captured_frame', 'capture_metadata'))]:
        check(item)
    events = [json.loads(line) for line in (WS / live['events']['file']).read_text().splitlines()]
    prefix = 'RF455 Protocol:'
    messages = [event['value'].removeprefix(prefix) for event in events if event.get('kind') == 'debug_string' and
                event.get('value', '').startswith(prefix)]
    observed = read('mastery-quests-checkpoint')['observed_sequence'] + ['linker-applied:2:0:1', 'tx:3:49:1', 'tx:13:104:1',
                                                                       'rx:3:50:954', 'rx:13:105:650']
    require(all(event in messages for event in observed) and [messages.index(event) for event in observed] ==
            sorted(messages.index(event) for event in observed), 'Accepted selection through the two Linker follow-up replies')
    require(live['debugger_exit'] == 0 and live['live_server']['private_handoff_removed'] and
            any(row.get('own_child_validated') and row.get('sent') for row in live['selection_input']) and
            not any(event['kind'] == 'exception' and not event.get('first_chance') for event in events), 'Live terminal state')

    source = WS / 'scripts/native/client455_initial_download.inc'
    method = 'InitMsg_LinkerDownloadResult455'
    rvas = [hex(at) for at, name in own_symbols(link) if name.startswith(f'?{method}@CNetworkMgr@@')]
    require(rvas and ('CNetworkMgr::' + method + '(').encode() in source.read_bytes(), 'Actual Linker consumer symbol')
    save('linker-download-bindings', dict(schema_version=1, reference_sha256=reference['references'][0]['sha256'],
                                        architecture='x86', image_base='0x400000', normal_executable=link['executable'],
                                        functions=[dict(rva=reference['linker_handler_rva'], symbol='CNetworkMgr::' + method,
                                                        source=record(source), ordinary_symbol_rvas=rvas,
                                                        complete_equivalence=False)]))
    names += ('linker-download-bindings', 'normal-preparation', 'normal-build', 'normal-consumers', 'own-entry',
              'startup-audit', 'startup-taiwan-native', 'live-launcher-native', 'live-server')
    scope = ('The ordinary client applies Linker bank settings and receives the macro and patriarch shout replies. '
             'Two references were present and neither resolved to an available Linker owner.')
    report = dict(status='PARTIAL_WAITING_FOR_MACRO_AND_LINKER_OWNERS', scope=scope, script=record(Path(__file__)),
                  normal_link_sha256=link_sha, normal_executable=link['executable'],
                  runtime_login_report=record(path('character-selection-live-taiwan-native')),
                  fresh_evidence={name: record(path(name)) for name in names},
                  prior_runtime=record(WS / 'artifacts/client455-progress/before177/manifest.json'), observed_sequence=observed,
                  explicit_function_bindings=1, linker=dict(bytes=157, decoded=True, present=2, applied=0,
                                                            bank_settings_applied=True, additional_windows_restored=False),
                  macro=dict(bytes=954, received=True, decoded=False),
                  patriarch_shout=dict(bytes=650, received=True, decoded=False),
                  world_entered=False, full_client=False, private_handoff_removed=True,
                  input_exe_executed=False, server_modified=False, gaps=reference['gaps'],
                  M6='OPEN', M6F='OPEN', M7='OPEN', M9='OPEN')
    save('linker-download-checkpoint', report)

    registry_path = WS / 'inventory/client-features.json'
    registry = json.loads(registry_path.read_text())
    identity = 'CLIENT455-LINKER-DOWNLOAD-177'
    registry['features'] = [row for row in registry['features'] if row['id'] != identity]
    for feature in registry['features']:
        if feature.get('runtime_gate_current'):
            feature['runtime_gate_current'] = False
    registry['features'].append(dict(id=identity, area='network', status='partial', runtime_gate_current=True,
                                    evidence=[path(name).relative_to(WS).as_posix() for name in
                                              ('linker-download-checkpoint', 'linker-download-reference',
                                               'initial-download-native')], description=scope, gaps=report['gaps']))
    registry_path.write_text(json.dumps(registry, indent=2) + '\n', encoding='ascii')
    print('PARTIAL: applied Linker bank settings and reached macro and patriarch shout replies')


if __name__ == '__main__':
    main()
