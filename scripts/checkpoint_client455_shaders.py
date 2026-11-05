"""Validate shader resource evidence and keep the full-renderer gap explicit."""
import json
from compare_client_binaries import WS
from audit_client_executable import without_timestamps
from probe_client455_shaders import inputs,sha
def load(name):return json.loads((WS/f'inventory/{name}.json').read_text(encoding='utf-8'))
def main():
    ref,build,dll=inputs();gpu=load('client455-shaders-gpu');client=load('client455-shaders-client');link=load('client455-shaders-link');lab=load('client-helper-lab-build');coff=load('client-mt-variant')
    if gpu['build_report_sha256']!=sha(WS/'inventory/client455-shaders-build.json') or gpu['reference_report_sha256']!=sha(WS/'inventory/client455-shaders-reference.json') or client['component_report_sha256']!=sha(WS/'inventory/client455-shaders-gpu.json'):raise ValueError('Shader evidence stale')
    for report in [gpu,client]:
        if sha(WS/report['exe'])!=report['exe_sha256'] or sha(WS/report['output'])!=report['output_sha256'] or sha(WS/report['frame'])!=report['frame_sha256']:raise ValueError('Changed shader runtime result')
    if gpu['native']!=client['native'] or gpu['frame_sha256']!=client['frame_sha256'] or client['native']['status']!='PASS' or client['native']['device_refs_after_release'] or client['native']['api_refs_after_release'] or client['dmalloc_balance'] or client['game_dlls_loaded'] or client['exe_sha256']!=link['lab']['exe_sha256']:raise ValueError('Fullclient shader differs')
    if len(link['lab']['functions'])!=7 or link['normal']['functions'] or lab['generated_objects']!=193:raise ValueError('Shader source selectors mismatch')
    snapshots=load('client-first-build');normal=WS/snapshots['character455-shaders']['snapshot']/'RF_Online.bin';previous=WS/snapshots['character455-animation-manager']['snapshot']/'RF_Online.bin'
    if sha(normal)!=link['normal']['exe_sha256'] or without_timestamps(normal.read_bytes())[0]!=without_timestamps(previous.read_bytes())[0]:raise ValueError('Unexpected normal runtime change')
    if sha(WS/coff['archive'])!=coff['archive_sha256'] or sum(item['objects_verified'] for item in coff['targets'])!=291:raise ValueError('Changed normal engine objects')
    evidence=['client455-shaders-reference','client455-shaders-build','client455-shaders-gpu','client455-shaders-client','client455-shaders-link','client-helper-lab-build']
    report={'scope':'Source Character shader bootstrap/real D3D9 resources;harness triangle not fullCharacter draw/normal455 integration/M9','normal':link['normal'],'lab':{key:link['lab'][key] for key in ['architecture','exe_sha256','exe_bytes','entry_rva']},'native':gpu['native'],'same_frame_sha256':gpu['frame_sha256'],'normal_runtime_bytes_equal_previous_excluding_timestamps':True,'normal_modern_coff_objects':291,'lab_client_objects':193,'unchanged_bulk_suites_repeated':False,'unrelated_platform01_suites_repeated':False,'remaining':['Full455DrawCharacter/draw-state/constants/palette/material/effects/device lifecycle','Coupled normal typedmodel/animation/renderer migration;old layout4-260 differsfrom4555-264','Modal shadererror UI/uncheckedfailure/OOM/originalCPU-FPU conditions notcertified','Fullclient acceptance M6F/M7/M9'],'evidence_sha256':{name:sha(WS/f'inventory/{name}.json') for name in evidence}}
    (WS/'inventory/client455-shaders-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('PASS:12SHO/15pinned compiler sources/7sourceAPIs/2declarations/HAL/119checks/fullclient sameframe;fullCharacter draw stillopen')
if __name__=='__main__':main()
