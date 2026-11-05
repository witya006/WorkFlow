"""Freeze connected draw evidence without closing the full Character gap."""
import json
from compare_client_binaries import WS
from audit_client_executable import without_timestamps
from probe_client455_draw import sha
from verify_client455_draw import APIS
def load(name):return json.loads((WS/f'inventory/{name}.json').read_text(encoding='utf-8'))
def main():
    ref=load('client455-draw-reference');build=load('client455-draw-build');gpu=load('client455-draw-gpu');client=load('client455-draw-client');link=load('client455-draw-link');lab=load('client-helper-lab-build');coff=load('client-mt-variant')
    if sha(WS/'scripts/audit_client455_draw.py')!=ref['script_sha256']:raise ValueError('Changed draw reference script')
    for name,digest in build['source_sha256'].items():
        if sha(WS/'scripts/native'/name)!=digest:raise ValueError('Changed source draw:'+name)
    for name in ['object','library','exe']:
        if sha(WS/build[name])!=build[name+'_sha256']:raise ValueError('Changed source build artifact')
    for item in build['dependencies']:
        if sha(WS/item['file'])!=item['sha256']:raise ValueError('Changed source dependency')
    if gpu['build_report_sha256']!=sha(WS/'inventory/client455-draw-build.json') or gpu['reference_report_sha256']!=sha(WS/'inventory/client455-draw-reference.json') or client['component_report_sha256']!=sha(WS/'inventory/client455-draw-gpu.json'):raise ValueError('Draw evidence stale')
    for item in ref['files']:
        if sha(WS/item['path'])!=item['sha256']:raise ValueError('Changed real model input')
    for item in ref['textures']:
        if sha(WS/item['copy'])!=item['sha256']:raise ValueError('Changed real texture input')
    for result in [gpu,client]:
        if sha(WS/result['exe'])!=result['exe_sha256'] or sha(WS/result['output'])!=result['output_sha256']:raise ValueError('Changed runtime artifact')
        for frame in result['frames']:
            if sha(WS/frame['frame'])!=frame['sha256'] or sha(WS/frame['preview'])!=frame['preview_sha256']:raise ValueError('Changed GPU frame')
    if client['native']!=gpu['native'] or [f['sha256'] for f in client['frames']]!=[f['sha256'] for f in gpu['frames']]:raise ValueError('Fullclient/component render differs')
    native=client['native']
    if native['status']!='PASS' or native['real_drawn_parts']!=46 or native['animated_parts']!=44 or native['frame_values']!=[160,2160] or native['draws']!=96 or native['owned_heap_balance'] or native['device_and_api_release_counts'] or client['dmalloc_balance'] or client['game_dlls_loaded']:raise ValueError('Connected draw coverage incomplete')
    if {f['symbol'] for f in link['lab']['functions']}!=set(APIS) or link['normal']['functions'] or lab['generated_objects']!=194 or link['lab']['exe_sha256']!=client['exe_sha256']:raise ValueError('Actual source draw selectors mismatch')
    snapshots=load('client-first-build');normal=WS/snapshots['character455-draw']['snapshot']/'RF_Online.bin';previous=WS/snapshots['character455-shaders']['snapshot']/'RF_Online.bin'
    if sha(normal)!=link['normal']['exe_sha256'] or without_timestamps(normal.read_bytes())[0]!=without_timestamps(previous.read_bytes())[0]:raise ValueError('Unexpected normal runtime change')
    if sha(WS/coff['archive'])!=coff['archive_sha256'] or sum(item['objects_verified'] for item in coff['targets'])!=291:raise ValueError('Changed normal engine archive/objects')
    names=['client455-draw-reference','client455-draw-build','client455-draw-gpu','client455-draw-client','client455-draw-link','client-helper-lab-build']
    report={'scope':'Source draw state/program/material/palette/shared submission with real animated model;full draw/normal455/M9 unproven','normal':link['normal'],'lab':{key:link['lab'][key] for key in ['architecture','exe_sha256','exe_bytes','entry_rva']},'native':native,'same_frame_sha256':[f['sha256'] for f in client['frames']],'normal_runtime_bytes_equal_previous_excluding_timestamps':True,'normal_modern_coff_objects':291,'lab_client_objects':194,'bulk_suites_repeated':False,'original_exe_executed':False,'owned_ida_session':'96152de8 closed/save','remaining':['Full92E5F0 effect/material program dispatch and all its state transitions','Sorted transparent930A40 and batch queues92D9D0,CPU retained92DB60,shadow930120 and high-level wrapper/culling','Coupled typed normal model/animation/renderer integration;no old455 pointer casts','Original frame/lighting/camera/visibility/device-loss/reset/CRT/FPU/error-path acceptance','All remaining M6/M6F/M7/M9 domains'],'evidence_sha256':{name:sha(WS/f'inventory/{name}.json') for name in names}}
    (WS/'inventory/client455-draw-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('PASS:connected real animated/textured source draw in fullclient;two same frames;full455 draw still open')
if __name__=='__main__':main()
