"""Validate selected secondary source evidence and related pose regression."""
import hashlib,json
from compare_client_binaries import WS
from audit_client_executable import without_timestamps
from probe_client455_pose import inputs

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(name):return json.loads((WS/f'inventory/{name}.json').read_text(encoding='utf-8'))
def main():
    inputs();ref=load('client455-secondary-reference');build=load('client455-secondary-build');cpu=load('client455-secondary-cpu');client=load('client455-secondary-client');pose=load('client455-pose-client');link=load('client455-pose-link');lab=load('client-helper-lab-build')
    for report in [cpu,client,pose]:
        if report['native']['status']!='PASS' or sha(WS/report['exe'])!=report['exe_sha256'] or sha(WS/report['output'])!=report['output_sha256']:raise ValueError('Changed runtime evidence')
    if sha(WS/build['source'])!=build['source_sha256'] or build['pose_build_sha256']!=sha(WS/'inventory/client455-pose-build.json') or cpu['build_report_sha256']!=sha(WS/'inventory/client455-secondary-build.json') or cpu['reference_report_sha256']!=sha(WS/'inventory/client455-secondary-reference.json'):raise ValueError('Stale secondary source/evidence')
    if sha(WS/ref['golden'])!=ref['golden_sha256'] or ref['script_sha256']!=sha(WS/'scripts/audit_client455_secondary.py'):raise ValueError('Changed secondary oracle')
    for sample in ref['human_models']:
        if sha(WS/sample['copy'])!=sample['sha256']:raise ValueError('Changed human input')
    if client['native']!=cpu['native'] or client['component_report_sha256']!=sha(WS/'inventory/client455-secondary-cpu.json') or client['dmalloc_balance'] or client['owned_heap_balance'] or client['game_dlls_loaded']:raise ValueError('Fullclient secondary mismatch')
    if client['exe_sha256']!=link['lab']['exe_sha256'] or pose['exe_sha256']!=link['lab']['exe_sha256'] or len(link['lab']['functions'])!=6 or link['normal']['functions'] or lab['generated_objects']!=189:raise ValueError('Source selection/PE mismatch')
    if pose['native']!=load('client455-pose-cpu')['native'] or pose['native']['real_pairs']!=11 or pose['native']['pose_updates']!=132:raise ValueError('Related pose regression failed')
    snapshots=load('client-first-build');normal=WS/snapshots['character455-secondary']['snapshot']/'RF_Online.bin';old=WS/snapshots['character455-pose-final']['snapshot']/'RF_Online.bin'
    if sha(normal)!=link['normal']['exe_sha256'] or without_timestamps(normal.read_bytes())[0]!=without_timestamps(old.read_bytes())[0]:raise ValueError('Unexpected normal runtime change')
    evidence=['client455-secondary-reference','client455-secondary-build','client455-secondary-cpu','client455-secondary-client','client455-pose-build','client455-pose-cpu','client455-pose-client','client455-pose-link']
    result={'scope':'Selected secondary state/effects/connected FrameMove,not original staticCRT sine parity/normal runtime/draw orM9','normal':link['normal'],'lab':{k:link['lab'][k] for k in ['architecture','exe_sha256','exe_bytes','entry_rva']},'native':cpu['native'],'related_pose_regression':pose['native'],'normal_runtime_bytes_equal_previous_excluding_timestamps':True,'lab_client_objects':189,'unchanged_bulk_suites_repeated':False,'remaining':['Reference static __CIsin/SSE versusmodern MT sine bit-parity','Original actor constructor/defaults/frameproducer andnormal typed consumers','Full manager/worker/D3D9skin-draw/shaders/acceptance'],'evidence_sha256':{name:sha(WS/f'inventory/{name}.json') for name in evidence}}
    (WS/'inventory/client455-secondary-checkpoint.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print('PASS:secondary36cases/2humanmodels/6updates/sourcecaller;relatedpose11pairs passed;CRTsin/normal/draw stillopen')
if __name__=='__main__':main()
