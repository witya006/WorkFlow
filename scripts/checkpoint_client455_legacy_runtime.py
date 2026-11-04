"""Validate the current converter milestone evidence without running clients."""
import hashlib,json
from compare_client_binaries import WS
from audit_client_executable import without_timestamps

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(name):return json.loads((WS/f'inventory/{name}.json').read_text(encoding='utf-8'))

def main():
    build=load('client455-legacy-runtime-build');ref=load('client455-legacy-runtime-reference');inputs=load('client455-legacy-runtime-inputs');link=load('client455-legacy-runtime-link');cpu=load('client455-legacy-runtime-cpu');gpu=load('client455-legacy-runtime-gpu');client=load('client455-legacy-runtime-client');graphics=load('client455-legacy-runtime-graphics')
    for name,digest in build['source_sha256'].items():
        if sha(WS/'scripts/native'/name)!=digest:raise ValueError('Source changed:'+name)
    for record in build['dependencies']:
        if sha(WS/record['file'])!=record['sha256']:raise ValueError('Changed source dependency')
    if sha(WS/build['library'])!=build['library_sha256'] or sha(WS/inputs['golden'])!=inputs['golden_sha256'] or sha(WS/ref['missing_bone_wide']['file'])!=ref['missing_bone_wide']['sha256']:raise ValueError('Changed owned library/goldens')
    for mode,report in [('cpu',cpu),('gpu',gpu)]:
        for name,key in [('client455-legacy-runtime-build','build_report_sha256'),('client455-legacy-runtime-reference','reference_report_sha256'),('client455-legacy-runtime-inputs','input_report_sha256')]:
            if report[key]!=sha(WS/f'inventory/{name}.json'):raise ValueError('Stale '+mode+' proof')
        if report['native']['status']!='PASS' or sha(WS/report['exe'])!=report['exe_sha256'] or sha(WS/report['output'])!=report['output_sha256']:raise ValueError('Changed native evidence')
    if client['component_gpu_report_sha256']!=sha(WS/'inventory/client455-legacy-runtime-gpu.json') or client['native']!=gpu['native'] or client['native']['checks']!=14896 or len(link['lab']['functions'])!=10 or link['normal']['functions']:raise ValueError('Source selection/runtime mismatch')
    for report in [client,load('client455-character-manager-client'),load('client455-models-client'),graphics]:
        if report['exe_sha256']!=link['lab']['exe_sha256'] or sha(WS/report['exe'])!=report['exe_sha256']:raise ValueError('Current PE evidence mismatch')
    previous={case['case']:case for case in load('client455-character-manager-graphics')['cases']}
    for case in graphics['cases']:
        if case['failures'] or case['warnings'] or case['errors'] or case['allocation_before']!=case['allocation_after'] or case['device_refs_after_release'] or case['d3d_refs_after_release']:raise ValueError('Current graphics check failed')
        if case.get('frame_sha256')!=previous[case['case']].get('frame_sha256'):raise ValueError('Previous frame changed')
    snapshots=load('client-first-build');normal=WS/snapshots['character455-legacy-models']['snapshot']/'RF_Online.bin';old=WS/snapshots['character455-manager-io']['snapshot']/'RF_Online.bin'
    if sha(normal)!=link['normal']['exe_sha256'] or without_timestamps(normal.read_bytes())[0]!=without_timestamps(old.read_bytes())[0]:raise ValueError('Unexpected normal runtime byte change')
    evidence=['client455-legacy-runtime-reference','client455-legacy-runtime-inputs','client455-legacy-runtime-build','client455-legacy-runtime-cpu','client455-legacy-runtime-gpu','client455-legacy-runtime-client','client455-legacy-runtime-link','client455-legacy-runtime-graphics','client455-character-manager-client','client455-models-client']
    result={'scope':'Selected full legacy MSH/BN converter/IO source milestone,not full Character/normal dispatcher/animation/shaders orM9','normal':link['normal'],'lab':{key:link['lab'][key] for key in ['architecture','exe_sha256','exe_bytes','entry_rva']},'native':{'cpu':cpu['native'],'gpu_and_client':gpu['native']},'regressions':{'manager_checks':load('client455-character-manager-client')['native']['checks'],'model_checks':load('client455-models-client')['native']['checks'],'graphics_checks':sum(c['checks'] for c in graphics['cases']),'previous_frame_hashes_equal':True,'normal_runtime_bytes_equal_previous_excluding_timestamps':True},'evidence_sha256':{name:sha(WS/f'inventory/{name}.json') for name in evidence}}
    (WS/'inventory/client455-legacy-runtime-checkpoint.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print('PASS:66627capture/14896HAL+fullclient;real BN-to-MESH08 pairs;manager1138/model10021/graphics69;frames/normal runtime preserved')
if __name__=='__main__':main()
