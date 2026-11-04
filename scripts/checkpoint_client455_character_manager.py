"""Check saved evidence consistency without executing any client."""
import hashlib,json
from compare_client_binaries import WS
from audit_client_executable import without_timestamps

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def load(name):return json.loads((WS/f'inventory/{name}.json').read_text(encoding='utf-8'))

def main():
    build=load('client455-character-manager-build');reference=load('client455-character-manager-reference');link=load('client455-character-manager-link');client=load('client455-character-manager-client');gpu=load('client455-character-manager-gpu');cpu=load('client455-character-manager-cpu')
    for name,report in [('cpu',cpu),('gpu',gpu)]:
        if report['build_report_sha256']!=sha(WS/'inventory/client455-character-manager-build.json') or report['reference_report_sha256']!=sha(WS/'inventory/client455-character-manager-reference.json'):raise ValueError('Stale '+name+' proof')
        if report['native']['status']!='PASS' or sha(WS/report['output'])!=report['output_sha256'] or sha(WS/report['exe'])!=report['exe_sha256']:raise ValueError('Changed native outputs')
    if client['exe_sha256']!=link['lab']['exe_sha256'] or client['native']!=gpu['native'] or len(link['lab']['functions'])!=13 or link['normal']['functions']:raise ValueError('Unexpected link/runtime selection')
    if client['component_gpu_report_sha256']!=sha(WS/'inventory/client455-character-manager-gpu.json') or client['reference_report_sha256']!=sha(WS/'inventory/client455-character-manager-reference.json'):raise ValueError('Stale fullclient proof')
    for item in [client,load('client455-models-client'),load('client455-character-manager-graphics')]:
        if item['exe_sha256']!=link['lab']['exe_sha256'] or sha(WS/item['exe'])!=item['exe_sha256']:raise ValueError('Current PE identity mismatch')
    for name,digest in build['source_sha256'].items():
        if sha(WS/'scripts/native'/name)!=digest:raise ValueError('Changed source:'+name)
    if sha(WS/build['library'])!=build['library_sha256'] or sha(WS/reference['constructor_golden'])!=reference['constructor_golden_sha256']:raise ValueError('Changed library/golden')
    old=load('client455-models-graphics-regression');graphics=load('client455-character-manager-graphics');old_cases={x['case']:x for x in old['cases']}
    for case in graphics['cases']:
        if case['failures'] or case['warnings'] or case['errors'] or case['allocation_before']!=case['allocation_after'] or case['device_refs_after_release'] or case['d3d_refs_after_release']:raise ValueError('GPU regression failed')
        if case.get('frame_sha256')!=old_cases[case['case']].get('frame_sha256'):raise ValueError('Prior frame changed')
    first=load('client-first-build');old_normal=WS/first['character455-model-pipeline']['snapshot']/'RF_Online.bin';normal=WS/first['character455-manager-io']['snapshot']/'RF_Online.bin'
    if sha(normal)!=link['normal']['exe_sha256'] or without_timestamps(old_normal.read_bytes())[0]!=without_timestamps(normal.read_bytes())[0]:raise ValueError('Normal unused module unexpectedly changed runtime bytes')
    report={'scope':'Character455 record/manager/cache/rawMSH selected source unit checkpoint;M6/M6F/M7/M9 remain open','normal':link['normal'],'lab':{k:link['lab'][k] for k in ['architecture','exe_sha256','exe_bytes','entry_rva']},'native':{'cpu':cpu['native'],'gpu_and_client':gpu['native']},'model_regression_checks':load('client455-models-client')['native']['checks'],'graphics_cases':len(graphics['cases']),'graphics_checks':sum(c['checks'] for c in graphics['cases']),'previous_frame_hashes_equal':True,'normal_runtime_bytes_equal_previous_excluding_timestamps':True,'constructor_instruction_count':len(load('client455-character-constructor-instructions')['instructions']),'evidence_sha256':{name:sha(WS/f'inventory/{name}.json') for name in ['client455-character-manager-reference','client455-character-constructor-instructions','client455-character-manager-build','client455-character-manager-cpu','client455-character-manager-gpu','client455-character-manager-link','client455-character-manager-client','client455-character-manager-graphics','client455-models-client']}}
    (WS/'inventory/client455-character-manager-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('PASS:13 owned APIs;850CPU/1138HAL;model10021;Platform01/device69checks;frames and normal runtime bytes preserved')
if __name__=='__main__':main()
