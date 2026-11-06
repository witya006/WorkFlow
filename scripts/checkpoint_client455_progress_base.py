"""Bind ordinary stage-base behavior without certifying the unported fourstage runtime."""
import hashlib,json,re
from pathlib import Path
from compare_client_binaries import WS
from build_client455_x87_math import read_va
from client455_normal_link_evidence import validate_normal_link

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def load(name):return json.loads((WS/f'inventory/{name}.json').read_text())
def check(row):
    if sha(WS/row['file'])!=row['sha256']:raise ValueError('Changed stagebase evidence:'+row['file'])
def main():
    ref=load('client455-progress-base-reference');native=load('client455-progress-native');prep=load('client455-normal-preparation');link=load('client455-normal-link');validate_normal_link(link)
    for report,script in [(ref,'audit_client455_progress_base.py'),(native,'probe_client455_progress.py')]:
        if report['script_sha256']!=sha(WS/'scripts'/script):raise ValueError('Stale stagebase producer')
    for folder,row in zip(['current','reference-backup'],ref['references']):
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';raw=path.read_bytes()
        if sha(path)!=row['sha256']:raise ValueError('Changed455pin')
        for body in row['ranges']:
            if hashlib.sha256(read_va(raw,0x400000+int(body['rva'],16),body['bytes'])).hexdigest()!=body['sha256']:raise ValueError('Changed455stagebase body')
    check(ref['raw_evidence'])
    if native['source_sha256']!=sha(WS/native['source']) or native['normal_link_sha256']!=sha(WS/'inventory/client455-normal-link.json') or native['builder_sha256']!=sha(WS/'scripts/client455_own_probe.py') or native['reference_sha256']!=sha(WS/'inventory/client455-progress-base-reference.json'):raise ValueError('Stale ordinary stagebase native build')
    for name,digest in native['sources'].items():
        if sha(WS/'scripts/native'/name)!=digest or prep['record_inputs'][name]!=digest:raise ValueError('Changed production stagebase source')
    for key in ['exe','map','output']:check(native[key])
    n=native['native']
    if native['natural_exit'] or n['status']!='PASS' or n['actual_base_size']!=24 or n['next_stage_roundtrips']!=5 or n['full_four_stage_factory'] or n['tutorial_runtime']:raise ValueError('Invalid stagebase scope')
    if not all(n[key] for key in ['init_retains_next','base_create_destroy_no_data_sideeffects','actual_virtual_order','inactive_still_renders','input_exit_shortcircuits','frame_exit_observed_next_iteration','actual_particle_counters_reset','title_constructor_next1']):raise ValueError('Missing ordinary stagebase behavior')
    mapping=(WS/link['map']['file']).read_text()
    if not re.search(r'MainLoop@CGameProgress[^\r\n]+cgameprogress\.obj',mapping,re.I):raise ValueError('Missing ordinary stage loop')
    ui=load('client455-ui-startup-native')
    if ui['normal_link_sha256']!=native['normal_link_sha256'] or not ui['completed_existing_client_create'] or ui['markers'][-1]['eax']!=1:raise ValueError('Current existingCreate regression required')
    report={'status':'PARTIAL','ordinary_stage_base_order_and_exit':'PASS','explicit_next_field_and_Init_retention':'PASS','existing_particle_count_reset':'PASS','title_constructor_next1':'PASS','full_four_stage_factory':'OPEN','Tutorial_runtime':'OPEN','actual_existing_Create':'PASS','evidence_sha256':{name:sha(WS/f'inventory/{name}.json') for name in ['client455-progress-base-reference','client455-progress-native','client455-normal-link','client455-ui-startup-native']},'gaps':ref['gaps'],'input_exe_executed':False,'server_modified':False,'M6':'OPEN','M6F':'OPEN','M7':'OPEN','M9':'OPEN'}
    (WS/'inventory/client455-progress-base-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('PARTIAL:ordinary stagebase/next/exit/particlecount PASS;fourstage/Tutorial/full455/M9 OPEN')
if __name__=='__main__':main()
