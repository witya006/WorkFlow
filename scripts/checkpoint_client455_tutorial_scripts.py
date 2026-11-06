"""Check the bounded SCP reader evidence without claiming a working Tutorial."""
import hashlib
import json
from pathlib import Path

from compare_client_binaries import WS, pe
from build_client455_x87_math import read_va
from audit_client455_tutorial_scripts import inspect


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    def load(name):
        return json.loads((WS / f'inventory/{name}.json').read_text())

    def check(row):
        if sha(WS / row['file']) != row['sha256']:
            raise ValueError('Changed SCP evidence: ' + row['file'])

    ref = load('client455-tutorial-scripts-reference')
    native = load('client455-tutorial-scripts-native')
    if ref['script_sha256'] != sha(WS / 'scripts/audit_client455_tutorial_scripts.py'):
        raise ValueError('Stale SCP reference')
    for key in ['raw_evidence', 'reader_asm', 'selection_evidence']:
        check(ref[key])
    assembly = json.loads((WS / ref['reader_asm']['file']).read_text())
    if len(assembly['asm']['lines']) != 700 or not assembly['cursor']['done']:
        raise ValueError('Incomplete QBI reader instructions')
    for folder, pin in zip(['current', 'reference-backup'], ref['references']):
        path = WS / f'work/client-reference/{folder}/RF_Online.bin'
        if sha(path) != pin['sha256']:
            raise ValueError('Changed pinned client')
        data = path.read_bytes()
        for row in pin['ranges']:
            body = read_va(data, 0x400000 + int(row['rva'], 16), row['bytes'])
            if hashlib.sha256(body).hexdigest() != row['sha256']:
                raise ValueError('Changed 455 SCP function')
    for row in ref['inputs']:
        path = Path(row['file'])
        layout = json.loads(json.dumps(inspect(path.read_bytes())))
        if sha(path) != row['sha256'] or layout != row['layout']:
            raise ValueError('Changed source SCP: ' + row['relative'])
    for row in ref['other_inputs']:
        if sha(Path(row['file'])) != row['sha256']:
            raise ValueError('Changed unselected SCP')
    if native['script_sha256'] != sha(WS / 'scripts/probe_client455_tutorial_scripts.py') or \
            native['reference_sha256'] != sha(WS / 'inventory/client455-tutorial-scripts-reference.json'):
        raise ValueError('Stale native SCP probe')
    for name, digest in native['sources'].items():
        if sha(WS / 'scripts/native' / name) != digest:
            raise ValueError('Changed SCP implementation')
    if sha(WS / native['library']) != native['library_sha256']:
        raise ValueError('Changed SCP library')
    for key in ['object', 'exe', 'map', 'build_log', 'output']:
        check(native[key])
    for key in ['inputs', 'roundtrips', 'semantics', 'fixtures']:
        for row in native[key]:
            check(row)
    if int(native['entry_rva'], 16) != pe((WS / native['exe']['file']).read_bytes())['entry_rva']:
        raise ValueError('Wrong native SCP entry')
    result = json.loads((WS / native['output']['file']).read_text())
    if result != native['native'] or result['status'] != 'PASS' or native['natural_exit']:
        raise ValueError('SCP native runtime failed')
    if len(ref['inputs']) != 99 or result['files'] != 99 or result['quests'] != 812 or result['instructions'] != 39864:
        raise ValueError('Unexpected real input coverage')
    for key in ['synthetic_all47', 'invalid_encode_atomic', 'semantic_edits',
                'max_text_length', 'unselected_generic_rejected']:
        if not result[key]:
            raise ValueError('Missing SCP boundary behavior: ' + key)
    if result['prefixes_rejected_atomically'] != 1069 or not native['semantic_fields_match_independent_python']:
        raise ValueError('Missing SCP semantic/atomic evidence')
    if result['command_execution'] or result['full_Tutorial'] or native['normal_client_relinked']:
        raise ValueError('Wire-only evidence cannot certify Tutorial runtime')
    report = {'status': 'PARTIAL', 'SCP47_reader': 'PASS', 'real99_lossless_and_semantic_fields': 'PASS',
              'malformed_and_serialized_boundaries': 'PASS', 'command_execution': 'OPEN',
              'ordinary_Tutorial_integration': 'OPEN', 'full_Tutorial': 'OPEN',
              'evidence_sha256': {name: sha(WS / f'inventory/{name}.json') for name in
                                 ['client455-tutorial-scripts-reference', 'client455-tutorial-scripts-native']},
              'gaps': ref['gaps'], 'input_exe_executed': False, 'server_modified': False,
              'M6': 'OPEN', 'M6F': 'OPEN', 'M7': 'OPEN', 'M9': 'OPEN'}
    (WS / 'inventory/client455-tutorial-scripts-checkpoint.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print('PARTIAL:SCP47 wire reader/99 real files/semantic fields/boundaries PASS;execution/Tutorial/M9 OPEN')


if __name__ == '__main__':
    main()
