"""Validate saved ANI/dispatcher milestone and current regressions, no execution."""
import hashlib,json
from compare_client_binaries import WS
from audit_client_executable import without_timestamps
from probe_client455_animation import inputs

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(name):return json.loads((WS/f'inventory/{name}.json').read_text(encoding='utf-8'))

def main():
    build,ref,_,_,_,_,_,_,_=inputs();link=load('client455-animation-link');cpu=load('client455-animation-cpu');gpu=load('client455-animation-gpu');client=load('client455-animation-client');graphics=load('client455-animation-graphics')
    for report in [cpu,gpu]:
        for name,key in [('client455-animation-build','build_report_sha256'),('client455-animation-reference','reference_report_sha256'),('character-mesh08-bone-pairs','pair_report_sha256'),('character-texture-inputs','texture_report_sha256')]:
            if report[key]!=sha(WS/f'inventory/{name}.json'):raise ValueError('Stale ANI proof')
        if report['native']['status']!='PASS' or sha(WS/report['exe'])!=report['exe_sha256'] or sha(WS/report['output'])!=report['output_sha256']:raise ValueError('Changed native evidence')
    if cpu['native']['checks']!=14513 or gpu['native']['checks']!=15181 or gpu['native']['physical_parts']!=660 or gpu['native']['rejected_msh_raw_buffers_released']!=1 or gpu['native']!=client['native'] or len(link['lab']['functions'])!=13 or link['normal']['functions']:raise ValueError('ANI scope/source selection mismatch')
    if client['component_gpu_report_sha256']!=sha(WS/'inventory/client455-animation-gpu.json') or client['dmalloc_balance'] or client['game_dlls_loaded'] or sha(WS/client['output'])!=client['output_sha256']:raise ValueError('Full-client ANI evidence mismatch')
    regressions=[client,load('client455-legacy-runtime-client'),load('client455-character-manager-client'),graphics]
    for report in regressions:
        if report['exe_sha256']!=link['lab']['exe_sha256'] or sha(WS/report['exe'])!=report['exe_sha256']:raise ValueError('Current PE evidence mismatch')
    previous={c['case']:c for c in load('client455-legacy-runtime-graphics')['cases']}
    for case in graphics['cases']:
        if case['failures'] or case['warnings'] or case['errors'] or case['allocation_before']!=case['allocation_after'] or case['device_refs_after_release'] or case['d3d_refs_after_release'] or case.get('frame_sha256')!=previous[case['case']].get('frame_sha256'):raise ValueError('Graphics regression')
    snapshots=load('client-first-build');normal=WS/snapshots['character455-animation']['snapshot']/'RF_Online.bin';old=WS/snapshots['character455-legacy-models']['snapshot']/'RF_Online.bin'
    if sha(normal)!=link['normal']['exe_sha256'] or without_timestamps(normal.read_bytes())[0]!=without_timestamps(old.read_bytes())[0]:raise ValueError('Unexpected normal runtime change')
    lab=load('client-helper-lab-build');normalBuild=load('client-character-diagnostic');coff=load('client-mt-variant')
    if lab['generated_objects']!=187 or normalBuild['generated_objects']!=180 or sum(t['objects_verified'] for t in coff['targets'])!=289:raise ValueError('Build manifest mismatch')
    evidence=['client455-animation-reference','client455-animation-build','client455-animation-cpu','client455-animation-gpu','client455-animation-link','client455-animation-client','client455-animation-graphics','client455-legacy-runtime-client','client455-character-manager-client','client-mt-variant']
    result={'scope':'Selected ANI/framing/rawIO/record/lifetime/attachment/character dispatcher,not full pose/normal runtime orM9','normal':link['normal'],'lab':{key:link['lab'][key] for key in ['architecture','exe_sha256','exe_bytes','entry_rva']},'native':{'cpu':cpu['native'],'gpu_and_client':gpu['native']},'regressions':{'legacy_runtime_checks':regressions[1]['native']['checks'],'manager_checks':regressions[2]['native']['checks'],'graphics_checks':sum(c['checks'] for c in graphics['cases']),'previous_frame_hashes_equal':True,'normal_runtime_bytes_equal_previous_excluding_timestamps':True},'normal_modern_coff_objects':289,'lab_client_objects':187,'evidence_sha256':{name:sha(WS/f'inventory/{name}.json') for name in evidence}}
    (WS/'inventory/client455-animation-checkpoint.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print('PASS:ANI14513CPU/15181HAL+fullclient;13sourceAPIs;legacy14896/manager1138/graphics69;frames/normal runtime preserved')
if __name__=='__main__':main()
