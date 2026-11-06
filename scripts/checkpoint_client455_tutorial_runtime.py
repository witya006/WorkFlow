"""Check common QBI execution evidence; real Tutorial/host are still required."""
import hashlib
import json
from pathlib import Path
from compare_client_binaries import WS, pe
from build_client455_x87_math import read_va
from prepare_client455_normal import kernel_sources


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    def load(name):
        return json.loads((WS / f'inventory/{name}.json').read_text())

    def check(row):
        if sha(WS / row['file']) != row['sha256']:
            raise ValueError('Changed QBI evidence: ' + row['file'])

    ref, native = load('client455-tutorial-runtime-reference'), load('client455-tutorial-runtime-native')
    if ref['script_sha256'] != sha(WS / 'scripts/audit_client455_tutorial_runtime.py') or \
       native['script_sha256'] != sha(WS / 'scripts/probe_client455_tutorial_runtime.py') or \
       native['reference_sha256'] != sha(WS / 'inventory/client455-tutorial-runtime-reference.json'):
        raise ValueError('Stale QBI runtime evidence')
    for key in ['raw_evidence', 'vtable_evidence']:
        check(ref[key])
    for row in ref['assemblies']:
        check(row)
        assembly = json.loads((WS / row['file']).read_text())
        if len(assembly['asm']['lines']) != row['instructions'] or not assembly['cursor']['done']:
            raise ValueError('Incomplete QBI assembly')
    for folder, pin in zip(['current', 'reference-backup'], ref['references']):
        binary = WS / f'work/client-reference/{folder}/RF_Online.bin'
        if sha(binary) != pin['sha256']:
            raise ValueError('Changed455pin')
        raw = binary.read_bytes()
        for row in pin['ranges']:
            if hashlib.sha256(read_va(raw, 0x400000 + int(row['rva'], 16), row['bytes'])).hexdigest() != row['sha256']:
                raise ValueError('Changed QBI function')
    for row in ref['inputs']:
        if sha(Path(row['file'])) != row['sha256']:
            raise ValueError('Changed client script')
    for name, digest in native['sources'].items():
        if sha(WS / 'scripts/native' / name) != digest:
            raise ValueError('Changed QBI source: ' + name)
    if sha(WS / native['library']) != native['library_sha256']:
        raise ValueError('Changed QBI library')
    for key in ['exe', 'map', 'build_log', 'output']:
        check(native[key])
    for row in native['objects'] + native['inputs']:
        check(row)
    if int(native['entry_rva'], 16) != pe((WS / native['exe']['file']).read_bytes())['entry_rva']:
        raise ValueError('Wrong QBI own entry')
    actual = json.loads((WS / native['output']['file']).read_text())
    if actual != native['native'] or native['natural_exit'] or actual['status'] != 'PASS':
        raise ValueError('QBI native runtime failed')
    for key in ['scheduler_order', 'flags_and_refresh', 'shared_timer_and_wrap', 'message0to4', 'wait5', 'callback_unload']:
        if not actual[key]:
            raise ValueError('Missing QBI rule: ' + key)
    if actual['real_records'] != 1235 or actual['basic_supported'] != 728 or actual['explicitly_unsupported'] != 507:
        raise ValueError('Wrong basic-factory coverage')
    if actual['full47_execution'] or actual['production_host'] or actual['full_Tutorial'] or native['normal_client_relinked']:
        raise ValueError('Do not certify unimplemented production Tutorial')
    # All client455 inventory files participate in source discovery. Preserve the
    # established library:string/library_sha256 schema for standalone libraries.
    kernels, _ = kernel_sources(WS / 'scripts/native')
    if len(kernels) != 20:
        raise ValueError('New reports broke canonical source discovery')
    report = {'status': 'PARTIAL', 'QBI_scheduler_and_common_state': 'PASS',
              'message_wait_rules_recording_host': 'PASS', 'canonical_discovery_compatible': 'PASS',
              'remaining41_selectors': 'OPEN', 'production_host': 'OPEN', 'full_Tutorial': 'OPEN',
              'evidence_sha256': {name: sha(WS / f'inventory/{name}.json') for name in
                                 ['client455-tutorial-runtime-reference', 'client455-tutorial-runtime-native']},
              'gaps': ref['gaps'], 'input_exe_executed': False, 'server_modified': False,
              'M6': 'OPEN', 'M6F': 'OPEN', 'M7': 'OPEN', 'M9': 'OPEN'}
    (WS / 'inventory/client455-tutorial-runtime-checkpoint.json').write_text(json.dumps(report, indent=2) + '\n')
    print('PARTIAL:QBI scheduler/common start/message+wait rules PASS;real host/41selectors/fullTutorial/M9 OPEN')


if __name__ == '__main__':
    main()
