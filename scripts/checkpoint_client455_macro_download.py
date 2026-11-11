"""Check macro and announcement ingestion on the ordinary live login path."""
import json
from pathlib import Path

from checkpoint_client455_party_window import path, read, save
from checkpoint_client455_rvp_effects import check, require, sha
from client455_normal_link_evidence import validate_normal_link
from client455_ui_checkpoint import own_symbols, record
from compare_client_binaries import WS


def main():
    names = ('normal-link', 'macro-download-reference', 'initial-download-native', 'character-selection-live-taiwan-native')
    link, reference, native, live = (read(name) for name in names)
    link_sha = sha(path('normal-link'))
    require(validate_normal_link(link) == 'PASS' and link_sha == live['normal_link_sha256'] == native['normal_link_sha256']
            and live['executable']['sha256'] == link['executable']['sha256'], 'Exact ordinary client evidence')
    require(native['status'] == 'PASS' and native['native']['macro_bytes'] == 954 and native['native']['shout_bytes'] == 650
            and native['native']['bad_sizes_rejected'], 'Macro and shout fixtures')
    for item in [reference['raw'], reference['decompilation'], *reference['sources'], *(native[key] for key in
                 ('source', 'header', 'script', 'executable', 'console')), *(live[key] for key in
                 ('events', 'captured_frame', 'capture_metadata'))]:
        check(item)
    events = [json.loads(line) for line in (WS / live['events']['file']).read_text().splitlines()]
    prefix = 'RF455 Protocol:'
    messages = [event['value'].removeprefix(prefix) for event in events if event.get('kind') == 'debug_string' and
                event.get('value', '').startswith(prefix)]
    observed = read('linker-download-checkpoint')['observed_sequence'][:-1] + [
        'macro-decoded:0:0:0', 'tx:27:111:1', 'rx:13:105:650', 'patriarch-shout-decoded:10:0:0', 'rx:27:112:2']
    require(all(event in messages for event in observed) and [messages.index(event) for event in observed] ==
            sorted(messages.index(event) for event in observed), 'Accepted selection through live guild list response')
    require(live['debugger_exit'] == 0 and live['live_server']['private_handoff_removed'] and
            any(row.get('own_child_validated') and row.get('sent') for row in live['selection_input']) and
            not any(event['kind'] == 'exception' and not event.get('first_chance') for event in events), 'Live terminal state')

    source = WS / 'scripts/native/client455_initial_download.inc'
    bindings = []
    symbols = own_symbols(link)
    for method, kind in [('InitMsg_MacroDownloadResult455', 'macro'), ('InitMsg_PatriarchShoutResult455', 'shout')]:
        rvas = [hex(at) for at, name in symbols if name.startswith(f'?{method}@CNetworkMgr@@')]
        require(rvas and ('CNetworkMgr::' + method + '(').encode() in source.read_bytes(), 'Actual consumer ' + method)
        bindings.append(dict(rva=reference[kind]['handler_rva'], symbol='CNetworkMgr::' + method,
                             source=record(source), ordinary_symbol_rvas=rvas, complete_equivalence=False))
    save('macro-download-bindings', dict(schema_version=1, reference_sha256=reference['references'][0]['sha256'],
                                        architecture='x86', image_base='0x400000', normal_executable=link['executable'],
                                        functions=bindings))
    names += ('macro-download-bindings', 'normal-preparation', 'normal-build', 'normal-consumers', 'own-entry',
              'startup-audit', 'startup-taiwan-native', 'live-launcher-native', 'live-server')
    scope = ('The ordinary client decodes and retains character-scoped macro and patriarch shout data and '
             'receives guild reply 27/112. The live account had no populated macros or announcement text.')
    report = dict(status='PARTIAL_WAITING_FOR_GUILD_AND_WORLD_INITIALIZATION', scope=scope, script=record(Path(__file__)),
                  normal_link_sha256=link_sha, normal_executable=link['executable'],
                  runtime_login_report=record(path('character-selection-live-taiwan-native')),
                  fresh_evidence={name: record(path(name)) for name in names},
                  map_gate_analysis=record(WS / 'artifacts/client455-progress/macro178-map-gate.json'),
                  prior_runtime=record(WS / 'artifacts/client455-progress/before178/manifest.json'), observed_sequence=observed,
                  explicit_function_bindings=len(bindings), macro=dict(bytes=954, decoded=True, actions=0, texts=0),
                  patriarch_shout=dict(bytes=650, decoded=True, texts=0), guild=dict(bytes=2, received=True, decoded=False),
                  world_entered=False, full_client=False, private_handoff_removed=True,
                  input_exe_executed=False, server_modified=False, gaps=reference['gaps'],
                  M6='OPEN', M6F='OPEN', M7='OPEN', M9='OPEN')
    save('macro-download-checkpoint', report)

    registry_path = WS / 'inventory/client-features.json'
    registry = json.loads(registry_path.read_text())
    identity = 'CLIENT455-MACRO-DOWNLOAD-178'
    registry['features'] = [row for row in registry['features'] if row['id'] != identity]
    for feature in registry['features']:
        if feature.get('runtime_gate_current'):
            feature['runtime_gate_current'] = False
    registry['features'].append(dict(id=identity, area='network', status='partial', runtime_gate_current=True,
                                    evidence=[path(name).relative_to(WS).as_posix() for name in
                                              ('macro-download-checkpoint', 'macro-download-reference',
                                               'initial-download-native')], description=scope, gaps=report['gaps']))
    registry_path.write_text(json.dumps(registry, indent=2) + '\n', encoding='ascii')
    print('PARTIAL: decoded macros and announcements and received guild 27/112')


if __name__ == '__main__':
    main()
