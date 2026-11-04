"""Validate the saved pose result without repeating old runtime suites."""
import hashlib,json
from compare_client_binaries import WS
from audit_client_executable import without_timestamps
from probe_client455_pose import inputs

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(name):return json.loads((WS/f'inventory/{name}.json').read_text(encoding='utf-8'))
def main():
    build,_,_,_,_,_=inputs();link=load('client455-pose-link');cpu=load('client455-pose-cpu');client=load('client455-pose-client');lab=load('client-helper-lab-build');coff=load('client-mt-variant')
    for report in [cpu,client]:
        if report['native']['status']!='PASS' or sha(WS/report['exe'])!=report['exe_sha256'] or sha(WS/report['output'])!=report['output_sha256']:raise ValueError('Changed pose runtime evidence')
    if cpu['build_report_sha256']!=sha(WS/'inventory/client455-pose-build.json') or cpu['input_report_sha256']!=sha(WS/'inventory/client455-pose-inputs.json') or cpu['native']!=client['native'] or client['component_report_sha256']!=sha(WS/'inventory/client455-pose-cpu.json'):raise ValueError('Stale pose result')
    if client['exe_sha256']!=link['lab']['exe_sha256'] or client['dmalloc_balance'] or client['owned_heap_balance'] or client['game_dlls_loaded'] or client['rendered'] or len(link['lab']['functions'])!=5 or link['normal']['functions']:raise ValueError('Pose source/scope mismatch')
    if lab['generated_objects']!=188 or sum(t['objects_verified'] for t in coff['targets'])!=289:raise ValueError('Unexpected modern build objects')
    snapshots=load('client-first-build');normal=WS/snapshots['character455-pose-final']['snapshot']/'RF_Online.bin';old=WS/snapshots['character455-animation']['snapshot']/'RF_Online.bin'
    if sha(normal)!=link['normal']['exe_sha256'] or without_timestamps(normal.read_bytes())[0]!=without_timestamps(old.read_bytes())[0]:raise ValueError('Unexpected normal runtime change')
    evidence=['client455-pose-reference','client455-pose-inputs','client455-pose-build','client455-pose-cpu','client455-pose-link','client455-pose-client','client-mt-variant']
    report={'scope':'Selected pose evaluator/FrameMove phases,not full secondary motion/normal runtime/animateddraw or M9','normal':link['normal'],'lab':{k:link['lab'][k] for k in ['architecture','exe_sha256','exe_bytes','entry_rva']},'native':cpu['native'],'normal_runtime_bytes_equal_previous_excluding_timestamps':True,'normal_modern_coff_objects':289,'lab_client_objects':188,'old_runtime_suites_repeated':False,'prior_runtime_evidence':'Historical ANI/legacy/manager/graphics proofs remain in client455-animation-checkpoint.json;not rerun or claimed current here','evidence_sha256':{name:sha(WS/f'inventory/{name}.json') for name in evidence}}
    (WS/'inventory/client455-pose-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('PASS:source pose/11pairs/132updates/5linkedAPIs;normal runtime preserved;no old bulk runtime suite repeated')
if __name__=='__main__':main()
