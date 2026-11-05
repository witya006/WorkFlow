"""Record source collection ownership and full-client caller evidence."""
import json
from compare_client_binaries import WS
from audit_client_executable import without_timestamps
from probe_client455_animation_manager import inputs,sha
def load(name):return json.loads((WS/f'inventory/{name}.json').read_text(encoding='utf-8'))
def main():
    ref,build=inputs();cpu=load('client455-animation-manager-cpu');client=load('client455-animation-manager-client');link=load('client455-animation-manager-link');lab=load('client-helper-lab-build');coff=load('client-mt-variant')
    if cpu['build_report_sha256']!=sha(WS/'inventory/client455-animation-manager-build.json') or cpu['reference_report_sha256']!=sha(WS/'inventory/client455-animation-manager-reference.json') or client['component_report_sha256']!=sha(WS/'inventory/client455-animation-manager-cpu.json'):raise ValueError('Stale manager evidence')
    for report in [cpu,client]:
        if sha(WS/report['exe'])!=report['exe_sha256'] or sha(WS/report['output'])!=report['output_sha256']:raise ValueError('Changed runtime result')
    if cpu['native']!=client['native'] or client['native']['status']!='PASS' or client['native']['owned_heap_balance'] or client['dmalloc_balance'] or client['game_dlls_loaded'] or client['exe_sha256']!=link['lab']['exe_sha256']:raise ValueError('Manager runtime mismatch')
    if len(link['lab']['functions'])!=11 or link['normal']['functions'] or lab['generated_objects']!=192:raise ValueError('Manager source selectors mismatch')
    snapshots=load('client-first-build');normal=WS/snapshots['character455-animation-manager']['snapshot']/'RF_Online.bin';previous=WS/snapshots['character455-loop-clock-final']['snapshot']/'RF_Online.bin'
    if sha(normal)!=link['normal']['exe_sha256'] or without_timestamps(normal.read_bytes())[0]!=without_timestamps(previous.read_bytes())[0]:raise ValueError('Unexpected normal runtime change')
    if sha(WS/coff['archive'])!=coff['archive_sha256'] or sum(item['objects_verified'] for item in coff['targets'])!=291:raise ValueError('Changed normal engine objects')
    evidence=['client455-animation-manager-reference','client455-animation-manager-build','client455-animation-manager-cpu','client455-animation-manager-client','client455-animation-manager-link','client-helper-lab-build']
    report={'scope':'Source AnimationManager4028 collection/cache/owners,not normal typed consumers/UI/async/fullCharacter455/M9','normal':link['normal'],'lab':{key:link['lab'][key] for key in ['architecture','exe_sha256','exe_bytes','entry_rva']},'native':cpu['native'],'normal_runtime_bytes_equal_previous_excluding_timestamps':True,'normal_modern_coff_objects':291,'lab_client_objects':192,'unchanged_bulk_suites_repeated':False,'unrelated_graphics_timer_suites_repeated':False,'remaining':ref['remaining'],'evidence_sha256':{name:sha(WS/f'inventory/{name}.json') for name in evidence}}
    (WS/'inventory/client455-animation-manager-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('PASS:manager4028/11actual sourceAPIs/87checks/oneANI/heap0;normal runtime unchanged;no unrelated bulk reruns')
if __name__=='__main__':main()
