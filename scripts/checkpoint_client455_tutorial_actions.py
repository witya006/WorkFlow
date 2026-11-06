"""Accept bounded QBI action rules; preparing all programs is not playing them."""
import hashlib
import json
from pathlib import Path
from compare_client_binaries import WS, pe
from build_client455_x87_math import read_va
from prepare_client455_normal import kernel_sources
from probe_client455_tutorial_scripts import fixture


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    def load(name):return json.loads((WS/f'inventory/{name}.json').read_text())
    def check(row):
        if sha(WS/row['file'])!=row['sha256']:raise ValueError('Changed QBI action evidence:'+row['file'])
    ref=load('client455-tutorial-actions-reference');native=load('client455-tutorial-actions-native')
    if ref['script_sha256']!=sha(WS/'scripts/audit_client455_tutorial_actions.py') or \
       native['script_sha256']!=sha(WS/'scripts/probe_client455_tutorial_actions.py') or \
       native['reference_sha256']!=sha(WS/'inventory/client455-tutorial-actions-reference.json'):
        raise ValueError('Stale QBI action evidence')
    if ref['script_reference_sha256']!=sha(WS/'inventory/client455-tutorial-scripts-reference.json'):
        raise ValueError('Changed SCP data audit')
    for row in ref['raw_evidence']+ref['assemblies']:check(row)
    for row in ref['assemblies']:
        body=json.loads((WS/row['file']).read_text())
        if len(body['asm']['lines'])!=row['instructions'] or not body['cursor']['done']:
            raise ValueError('Incomplete QBI action assembly')
    for folder,pin in zip(['current','reference-backup'],ref['references']):
        path=WS/f'work/client-reference/{folder}/RF_Online.bin'
        if sha(path)!=pin['sha256']:raise ValueError('Changed455pin')
        raw=path.read_bytes()
        for row in pin['ranges']+pin['data']:
            if hashlib.sha256(read_va(raw,0x400000+int(row['rva'],16),row['bytes'])).hexdigest()!=row['sha256']:
                raise ValueError('Changed QBI action contract')
    for row in ref['inputs']:
        if sha(Path(row['file']))!=row['sha256']:raise ValueError('Changed client SCP')
    for name,digest in native['sources'].items():
        if sha(WS/'scripts/native'/name)!=digest:raise ValueError('Changed QBI action source:'+name)
    if sha(WS/native['library'])!=native['library_sha256']:raise ValueError('Changed action library')
    for key in ['exe','map','build_log','output','equip_map']:check(native[key])
    for row in native['objects']+native['inputs']+native['fixtures']:check(row)
    if pe((WS/native['exe']['file']).read_bytes())['entry_rva']!=int(native['entry_rva'],16):
        raise ValueError('Wrong own action entry')
    expected=next(row['hex'] for row in ref['references'][0]['data'] if row['role']=='equip_slot_map')
    if (WS/native['equip_map']['file']).read_bytes().hex()!=expected:raise ValueError('Wrong16equip bytes')
    synthetic=next(WS/row['file'] for row in native['fixtures'] if row['file'].endswith('/all47.scp'))
    if synthetic.read_bytes()!=fixture():raise ValueError('Changed independent47selector fixture')
    actual=json.loads((WS/native['output']['file']).read_text())
    if actual!=native['native'] or actual['status']!='PASS' or native['natural_exit']:
        raise ValueError('QBI action native failed')
    for key in ['ui19to22','equip23to26','cursor27to34','combat35to39','item40to46',
                'lifecycle_and_branch_order','synthetic47_prepared']:
        if not actual[key]:raise ValueError('Missing action rule:'+key)
    if actual['files_prepared']!=99 or actual['records_prepared']!=39864:
        raise ValueError('Incomplete real-program processor preparation')
    if actual['production_host'] or actual['unsafe_cursor_failure_resolved'] or actual['full_Tutorial'] or native['normal_client_relinked']:
        raise ValueError('Do not turn factory coverage into full Tutorial acceptance')
    kernels,_=kernel_sources(WS/'scripts/native')
    if len(kernels)!=20:raise ValueError('Canonical source discovery changed')
    report={'status':'PARTIAL','UI_Equip_Cursor_Combat_Item_rules_recording_host':'PASS',
            'all47_processor_families_prepared':'PASS','real99_programs_prepared':'PASS',
            'equip_map16':'PASS','production_host':'OPEN','unsafe_cursor_failure':'OPEN','full_Tutorial':'OPEN',
            'evidence_sha256':{name:sha(WS/f'inventory/{name}.json') for name in
                               ['client455-tutorial-actions-reference','client455-tutorial-actions-native']},
            'gaps':ref['gaps'],'input_exe_executed':False,'server_modified':False,
            'M6':'OPEN','M6F':'OPEN','M7':'OPEN','M9':'OPEN'}
    (WS/'inventory/client455-tutorial-actions-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PARTIAL:QBI19to46/rules/47families/99programs prepared PASS;realhost/unsafe domains/Tutorial/M9 OPEN')


if __name__=='__main__':main()
