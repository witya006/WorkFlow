"""Freeze main draw evidence while retaining full normal/visibility/CRT gaps."""
import json
from compare_client_binaries import WS
from audit_client_executable import without_timestamps
from probe_client455_character_draw import inputs,sha
from verify_client455_character_draw import APIS
def load(name):return json.loads((WS/f'inventory/{name}.json').read_text(encoding='utf-8'))
def main():
    build,ref,dll=inputs();gpu=load('client455-character-draw-gpu');client=load('client455-character-draw-client');link=load('client455-character-draw-link');lab=load('client-helper-lab-build');coff=load('client-mt-variant')
    if gpu['build_report_sha256']!=sha(WS/'inventory/client455-character-draw-build.json') or gpu['reference_report_sha256']!=sha(WS/'inventory/client455-character-draw-reference.json') or client['component_report_sha256']!=sha(WS/'inventory/client455-character-draw-gpu.json'):raise ValueError('Draw route evidence stale')
    for artifact in build['objects']:
        if sha(WS/artifact['file'])!=artifact['sha256']:raise ValueError('Changed draw route object')
    if sha(WS/build['library'])!=build['library_sha256']:raise ValueError('Changed draw route archive')
    for report in [gpu,client]:
        if sha(WS/report['exe'])!=report['exe_sha256'] or sha(WS/report['output'])!=report['output_sha256']:raise ValueError('Changed runtime result')
        for frame in report['frames']:
            if sha(WS/frame['frame'])!=frame['sha256'] or sha(WS/frame['preview'])!=frame['preview_sha256']:raise ValueError('Changed readback frame')
    native=client['native']
    if native!=gpu['native'] or native['status']!='PASS' or native['route_cases']!=16 or native['real_draws']!=92 or native['frames']!=[160,2160] or native['heap_and_com_balance'] or client['dmalloc_balance'] or client['game_dlls_loaded']:raise ValueError('Connected route coverage incomplete')
    frameHashes=[f['sha256'] for f in client['frames']]
    if frameHashes!=[f['sha256'] for f in gpu['frames']] or len(set(frameHashes))!=2:raise ValueError('Fullclient/component draw differs')
    if set(f['symbol'] for f in link['lab']['functions'])!=set(APIS) or link['normal']['functions'] or link['lab']['exe_sha256']!=client['exe_sha256'] or lab['generated_objects']!=195:raise ValueError('Source route call/provider proof incomplete')
    snapshots=load('client-first-build');normal=WS/snapshots['character455-route-final']['snapshot']/'RF_Online.bin';previous=WS/snapshots['character455-draw']['snapshot']/'RF_Online.bin'
    if sha(normal)!=link['normal']['exe_sha256'] or without_timestamps(normal.read_bytes())[0]!=without_timestamps(previous.read_bytes())[0]:raise ValueError('Unexpected normal runtime change')
    if sha(WS/coff['archive'])!=coff['archive_sha256'] or sum(t['objects_verified'] for t in coff['targets'])!=291:raise ValueError('Changed normal engine/archive')
    primitive=load('client455-draw-gpu')
    if primitive['build_report_sha256']!=sha(WS/'inventory/client455-draw-build.json') or primitive['native']['status']!='PASS' or [f['sha256'] for f in primitive['frames']]!=frameHashes:raise ValueError('Related pool primitive regression failed')
    names=['client455-character-draw-reference','client455-character-draw-build','client455-character-draw-gpu','client455-character-draw-client','client455-character-draw-link','client455-draw-build','client455-draw-gpu','client-helper-lab-build']
    report={'scope':'Source main/effect/transparent/batch/dynamic/shadow routes with defined-input limits;not full normal455/M9 acceptance','normal':link['normal'],'lab':{key:link['lab'][key] for key in ['architecture','exe_sha256','exe_bytes','entry_rva']},'native':native,'same_frames':frameHashes,'same_as_related_primitive_frames':True,'normal_runtime_equal_previous_excluding_timestamps':True,'normal_modern_coff_objects':291,'lab_client_objects':195,'bulk_suites_repeated':False,'related_pool_primitive_regression':primitive['native'],'owned_ida_session':'96236a02 closed/save','remaining':['Typed normal model/animation/Character interface and D3D9 engine integration','Wrapper visibility/culling/simple92E140 and external scene-frustum publication8C2A90','StaticCRT sin/cos and original compiler/FPU parity;first-bump undefined scratch andzero-weight undefinedCPU temps notcertified','Device loss/reset/failure/OOM/unsafe input and full game lighting/camera/effects runtime acceptance','All remaining M6/M6F/M7/M9 domains'],'evidence_sha256':{name:sha(WS/f'inventory/{name}.json') for name in names}}
    (WS/'inventory/client455-character-draw-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('PASS:source main draw/16targetedcases/real animated frames equal in fullclient;normal455/M9 stillopen')
if __name__=='__main__':main()
