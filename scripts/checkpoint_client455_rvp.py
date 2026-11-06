"""Bind the078 RVP source/load-model evidence; never accept a complete player here."""
import hashlib
import json
from pathlib import Path

from audit_client455_rvp import decode
from audit_client455_scrollbar import assembly_rows
from build_client455_x87_math import read_va
from compare_client_binaries import WS, pe
from client455_normal_link_evidence import validate_normal_link


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    def load(name):
        return json.loads((WS / 'inventory' / (name + '.json')).read_text())
    def check(row):
        if sha(WS / row['file']) != row['sha256']:
            raise ValueError('Changed RVP evidence: ' + row['file'])
    reference, native = load('client455-rvp-reference'), load('client455-rvp-native')
    if reference['script_sha256'] != sha(WS / 'scripts/audit_client455_rvp.py') or \
       native['script_sha256'] != sha(WS / 'scripts/probe_client455_rvp.py') or \
       native['reference_sha256'] != sha(WS / 'inventory/client455-rvp-reference.json'):
        raise ValueError('Stale RVP audit/probe')
    check(reference['raw_evidence'])
    raw_evidence = json.loads((WS / reference['raw_evidence']['file']).read_text())
    if list(assembly_rows([raw_evidence['create_asm'], raw_evidence['curve_asm']])) != reference['assemblies']:
        raise ValueError('Incomplete RVP assembly')
    pages = raw_evidence['create_asm_pages']
    if [line for page in pages for line in page['asm']['lines']] != raw_evidence['create_asm']['asm']['lines']:
        raise ValueError('RVP assembly pages changed')
    for page in pages:
        if len(page['asm']['lines']) != page['instruction_count']:
            raise ValueError('Truncated RVP assembly page')
    head, tail = raw_evidence['create'], raw_evidence['create_tail']
    if head['cursor']['next'] != head['line_count'] or not tail['cursor']['done'] or \
       head['line_count'] + tail['line_count'] != head['total_lines']:
        raise ValueError('Incomplete RVP Create pseudocode')
    for folder, pin in zip(['current', 'reference-backup'], reference['references']):
        path = WS / 'work/client-reference' / folder / 'RF_Online.bin'
        raw = path.read_bytes()
        if sha(path) != pin['sha256'] or len(pin['ranges']) != 15:
            raise ValueError('Changed RVP455 pin/ranges')
        for row in pin['ranges']:
            digest = hashlib.sha256(read_va(raw, 0x400000 + int(row['rva'], 16), row['bytes'])).hexdigest()
            if digest != row['sha256']:
                raise ValueError('Changed RVP455 reference range')
    for key in ['source', 'header', 'probe', 'camera_header', 'executable', 'map', 'build_log', 'console', 'result']:
        check(native[key])
    check(dict(file=native['library'], sha256=native['library_sha256']))
    for row in native['inputs'] + native['outputs']:
        check(row)
    if native['natural_exit'] or native['native'] != json.loads((WS / native['result']['file']).read_text()) or \
       native['native']['status'] != 'PASS' or native['native']['full_RVP_player'] or native['native']['full_Tutorial'] or \
       not native['independent_named_fields_equal'] or not native['all_twelve_command_kinds'] or \
       native['normal_client_relinked'] or native['normal_client_functionality_changed']:
        raise ValueError('RVP result/scope mismatch')
    if pe((WS / native['executable']['file']).read_bytes())['architecture'] != 'x86':
        raise ValueError('RVP native probe must be x86')
    totals = reference['totals']
    if totals['files'] != 44 or totals['actors'] != 615 or totals['tracks'] != 1569 or \
       native['native']['files'] != 46 or len(native['inputs']) != 46 or len(native['outputs']) != 46:
        raise ValueError('RVP input coverage changed')
    for row, own, output in zip(reference['inputs'], native['inputs'], native['outputs']):
        if sha(Path(row['file'])) != row['sha256'] or own['sha256'] != row['sha256'] or \
           json.loads((WS / output['file']).read_text()) != decode((WS / own['file']).read_bytes()):
            raise ValueError('Stock RVP/source semantic evidence changed')
    link = load('client455-normal-link')
    if validate_normal_link(link) != 'PASS':
        raise ValueError('Existing production link changed')
    report = dict(status='PARTIAL', load_model='PASS_BOUNDED', original_files=44,
                  original_actor_records=615, original_tracks=1569, command_kinds=12,
                  source_only_executable=link['executable'], normal_client_relinked=False,
                  library=native['library'], library_sha256=native['library_sha256'],
                  reference_sha256=sha(WS / 'inventory/client455-rvp-reference.json'),
                  native_sha256=sha(WS / 'inventory/client455-rvp-native.json'),
                  script_sha256=sha(Path(__file__)), gaps=reference['gaps'],
                  full_RVP_player=False, input_exe_executed=False, server_modified=False,
                  M6='OPEN', M6F='OPEN', M7='OPEN', M9='OPEN')
    (WS / 'inventory/client455-rvp-checkpoint.json').write_text(json.dumps(report, indent=2) + '\n')
    print('PARTIAL: RVP load model44files/615actors/1569tracks,12command kinds/interpolation PASS; ordinary player/Tutorial/M9 OPEN')


if __name__ == '__main__':
    main()
