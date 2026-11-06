"""Verify spatial QBI rules without certifying the still missing world host."""
import hashlib
import json
from pathlib import Path
from compare_client_binaries import WS, pe
from build_client455_x87_math import read_va
from prepare_client455_normal import kernel_sources


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    def load(name): return json.loads((WS / f'inventory/{name}.json').read_text())
    def check(row):
        if sha(WS / row['file']) != row['sha256']:
            raise ValueError('Changed spatial evidence: ' + row['file'])
    ref = load('client455-tutorial-spatial-reference')
    native = load('client455-tutorial-spatial-native')
    if ref['script_sha256'] != sha(WS / 'scripts/audit_client455_tutorial_spatial.py') or \
       native['script_sha256'] != sha(WS / 'scripts/probe_client455_tutorial_spatial.py') or \
       native['reference_sha256'] != sha(WS / 'inventory/client455-tutorial-spatial-reference.json'):
        raise ValueError('Stale spatial evidence')
    for row in ref['raw_evidence'] + ref['assemblies']:
        check(row)
    for row in ref['assemblies']:
        asm = json.loads((WS / row['file']).read_text())
        if len(asm['asm']['lines']) != row['instructions'] or not asm['cursor']['done']:
            raise ValueError('Incomplete spatial instructions')
    for folder, pin in zip(['current','reference-backup'],ref['references']):
        path = WS / f'work/client-reference/{folder}/RF_Online.bin'
        if sha(path) != pin['sha256']: raise ValueError('Changed455pin')
        raw = path.read_bytes()
        for row in pin['ranges'] + pin['data']:
            body = read_va(raw,0x400000+int(row['rva'],16),row['bytes'])
            if hashlib.sha256(body).hexdigest() != row['sha256']:
                raise ValueError('Changed spatial contract')
    for row in ref['inputs']:
        if sha(Path(row['file'])) != row['sha256']: raise ValueError('Changed client SCP')
    for name,digest in native['sources'].items():
        if sha(WS / 'scripts/native' / name) != digest: raise ValueError('Changed spatial source')
    if sha(WS / native['library']) != native['library_sha256']: raise ValueError('Changed spatial library')
    for key in ['exe','map','build_log','output','category_map']: check(native[key])
    for row in native['objects'] + native['inputs']: check(row)
    if int(native['entry_rva'],16) != pe((WS/native['exe']['file']).read_bytes())['entry_rva']:
        raise ValueError('Wrong own spatial entry')
    expected = next(row['hex'] for row in ref['references'][0]['data'] if row['role'] == 'item_category_map')
    if (WS/native['category_map']['file']).read_bytes().hex() != expected:
        raise ValueError('Wrong47item category bytes')
    actual = json.loads((WS/native['output']['file']).read_text())
    if actual != native['native'] or actual['status'] != 'PASS' or native['natural_exit']:
        raise ValueError('Spatial native runtime failed')
    for key in ['position12to18','move6to8','creation9to11_rules','XZ_distance','wire17_known25','timeout_wrap','counter_wrap']:
        if not actual[key]: raise ValueError('Missing spatial rule: '+key)
    if (actual['real_records'],actual['supported'],actual['open']) != (1235,946,289):
        raise ValueError('Unexpected factory sample coverage')
    if actual['production_host'] or actual['item_tail25_resolved'] or actual['full_Tutorial'] or native['normal_client_relinked']:
        raise ValueError('Do not certify the unresolved world host/item tail')
    kernels,_ = kernel_sources(WS/'scripts/native')
    if len(kernels) != 20: raise ValueError('Source discovery changed')
    report = {'status':'PARTIAL','Move_Creation_Position_rules_recording_host':'PASS',
              'known17_and25bytes':'PASS','item_category_map47':'PASS','shared_context_regression':'see runtime checkpoint',
              'remaining28_selectors':'OPEN','production_host':'OPEN','item_tail25':'OPEN','full_Tutorial':'OPEN',
              'evidence_sha256':{name:sha(WS/f'inventory/{name}.json') for name in
                                 ['client455-tutorial-spatial-reference','client455-tutorial-spatial-native']},
              'gaps':ref['gaps'],'input_exe_executed':False,'server_modified':False,
              'M6':'OPEN','M6F':'OPEN','M7':'OPEN','M9':'OPEN'}
    (WS/'inventory/client455-tutorial-spatial-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PARTIAL:spatialQBI6to18/knownspawnbytes/category47 PASS;worldhost/itemtail/28selectors/Tutorial/M9 OPEN')


if __name__ == '__main__':
    main()
