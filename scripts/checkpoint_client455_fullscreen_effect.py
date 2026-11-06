"""Accept real fullscreen motion path and intro binding,not whole455 or fullstage."""
import hashlib,json,re
from pathlib import Path
from build_client455_x87_math import read_va
from client455_normal_link_evidence import validate_normal_link
from compare_client_binaries import WS,pe

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    def load(name):return json.loads((WS/f'inventory/{name}.json').read_text())
    def check(row):
        if not row or sha(WS/row['file'])!=row['sha256']:raise ValueError('Changed fullscreen evidence:'+str(row))
    link=load('client455-normal-link');validate_normal_link(link);digest=sha(WS/'inventory/client455-normal-link.json');engine=load('client455-startup-engine-build');reference=load('client455-fullscreen-effect-reference');native=load('client455-fullscreen-effect-native');visual=load('client455-fullscreen-effect-visual');introvisual=load('client455-tutorial-intro-visual');prep=load('client455-normal-preparation')
    for name,report in [('build_client455_engine_startup.py',engine),('audit_client455_fullscreen_effect.py',reference),('probe_client455_fullscreen_effect.py',native),('review_client455_fullscreen_effect.py',visual),('review_client455_tutorial_intro.py',introvisual),('prepare_client455_normal.py',prep)]:
        if report['script_sha256']!=sha(WS/'scripts'/name):raise ValueError('Stale fullscreen script:'+name)
    if len(engine['derived_sources'])!=7 or sha(WS/engine['library'])!=engine['library_sha256']:raise ValueError('Wrong derived engine')
    for row in engine['derived_sources']+[engine['baseline_library']]:check(row)
    for row in engine['base_sources']+[{'file':r['original'],'sha256':r['original_sha256']} for r in engine['derived_sources']]:check(row)
    for name,digestSource in engine['fullscreen_effect'].items():
        if sha(WS/'scripts/native'/name)!=digestSource:raise ValueError('Changed fullscreen source provider')
    for name in ['client455_tutorial_intro.h','client455_tutorial_intro.cpp','client455_tutorial_intro_camera.cpp']:
        if prep['record_inputs'][name]!=sha(WS/'scripts/native'/name):raise ValueError('Changed intro binding')
    check(reference['raw_evidence'])
    for folder,pin in zip(['current','reference-backup'],reference['references']):
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';raw=path.read_bytes()
        if sha(path)!=pin['sha256']:raise ValueError('Changed455pin')
        for row in pin['ranges']+[pin['default_density']]:
            if hashlib.sha256(read_va(raw,0x400000+int(row['rva'],16),row['bytes'])).hexdigest()!=row['sha256']:raise ValueError('Changed fullscreen reference')
    def verify_run(run,script):
        if run['normal_link_sha256']!=digest or run['engine_report_sha256']!=sha(WS/'inventory/client455-startup-engine-build.json') or run['source_sha256']!=sha(WS/run['source']) or run['script_sha256']!=sha(WS/'scripts'/script) or run['builder_sha256']!=sha(WS/'scripts/client455_own_probe.py'):raise ValueError('Stale fullscreen native build')
        for key in ['exe','map','console','output']:check(run[key])
        for row in run['inputs']+run['frames']:check(row)
        if run['natural_exit'] or run['native']['status']!='PASS' or run['native']!=json.loads((WS/run['output']['file']).read_text()) or pe((WS/run['exe']['file']).read_bytes())['architecture']!='x86':raise ValueError('Native fullscreen path failed')
    verify_run(native,'probe_client455_fullscreen_effect.py');actual=native['native']
    if native['reference_sha256']!=sha(WS/'inventory/client455-fullscreen-effect-reference.json') or actual['GPU_frames']!=18 or actual['saved_frames']!=5 or actual['warnings'] or actual['complete_water_bloom_lifecycle']:raise ValueError('Fullscreen result/scope mismatch')
    if not all(actual[key] for key in ['actual_R3Begin_FullScreenEffect_End','current_scene_opaque_final','framebuffer_depth_viewport_UI_restored','texture512_low_video_memory','failed_BeginScene_reported']):raise ValueError('Fullscreen contract failed')
    if not visual['manually_reviewed'] or visual['native_sha256']!=sha(WS/'inventory/client455-fullscreen-effect-native.json') or len(visual['frames'])!=5:raise ValueError('Current fullscreen frames must be reviewed')
    check(visual['sheet'])
    for row in visual['frames']:
        check(row)
        if sha(WS/row['preview'])!=row['preview_sha256']:raise ValueError('Changed fullscreen preview')
    if not introvisual['manually_reviewed'] or len(introvisual['frames'])!=29:raise ValueError('All current intro frames must be reviewed')
    for row in introvisual['sheets']:check(row)
    observations=[]
    for race,count in [('bellato',9),('cora',9),('accretia',8)]:
        path=WS/f'inventory/client455-tutorial-intro-{race}-native.json';run=json.loads(path.read_text());verify_run(run,'probe_client455_tutorial_intro.py');check(run['trace']);result=run['native']
        if not run['real_fullscreen_mode_density'] or result['selected']!=count or result['captures']!=count or result['fade_outs']!=count or result['warnings'] or result['memory_before']!=result['memory_after'] or result['full_stage_QBI_engine_controls']:raise ValueError('Intro fullscreen integration/scope failed')
        if not all(result[key] for key in ['real_camera_fade_screen_mouse_avatar_world','deferred_skip','reload_retains_counters']):raise ValueError('Intro regression failed')
        trace=[json.loads(line) for line in (WS/run['trace']['file']).read_text().splitlines()]
        if len(trace)!=result['frames'] or trace[-1]['active'] or trace[-1]['ordinal']!=count or {r['ordinal'] for r in trace if r['active']}!=set(range(count+1)):raise ValueError('Intro trace lost cuts/completion')
        reviewed=[row for row in introvisual['frames'] if row['race']==race]
        if {Path(row['file']).name for row in reviewed}!={f'cut-{i:02d}.bgra' for i in range(count)}|{'debug-first.bgra'}:raise ValueError('Missing real camera cut view')
        for row in reviewed:
            check(row)
            if row['native_sha256']!=sha(path) or sha(WS/row['preview'])!=row['preview_sha256']:raise ValueError('Stale intro visual review')
        mapping=(WS/run['map']['file']).read_text()
        for symbol,owner in [('FullScreenEffect@@','R3Engine455Startup:r3d3d8.obj'),('setEngineRenderFlag@RF455TutorialIntroCameraHost','RFClient455Facade:client455_tutorial_intro_camera.obj')]:
            if not re.search(re.escape(symbol)+r'[^\r\n]*'+re.escape(owner),mapping,re.I):raise ValueError('Real intro/fullscreen provider missing:'+symbol)
        observations.append({'race':race,'cameras':count,'frames':result['frames'],'Dmalloc_before_after':[result['memory_before'],result['memory_after']]})
    mapping=(WS/link['map']['file']).read_text()
    if not re.search(r'FullScreenEffect@@[^\r\n]*R3Engine455Startup:r3d3d8.obj',mapping,re.I):raise ValueError('Ordinary fullscreen source provider not retained')
    ui=load('client455-ui-startup-native');contracts=load('client455-startup-contracts-native')
    if ui['normal_link_sha256']!=digest or not ui['completed_existing_client_create'] or ui['markers'][-1]['eax']!=1 or contracts['build_sha256']!=sha(WS/'inventory/client455-startup-engine-build.json'):raise ValueError('Current exactPE/Create1 and engine contracts required')
    names=['client455-fullscreen-effect-reference','client455-fullscreen-effect-native','client455-fullscreen-effect-visual','client455-tutorial-intro-visual','client455-startup-engine-build','client455-ui-startup-native']+[f'client455-tutorial-intro-{r}-native' for r in ['bellato','cora','accretia']]
    report={'status':'PARTIAL','ordinary_fullscreen_motion_branch':'PASS_BOUNDED','GPU_pattern_frames':18,'reviewed_frames':34,'real_intro_fullscreen_bindings':'PASS','observations':observations,'exactPE_Create1':'PASS','script_sha256':sha(Path(__file__)),'evidence_sha256':{name:sha(WS/f'inventory/{name}.json') for name in names},'gaps':reference['gaps'],'input_exe_executed':False,'server_modified':False,'M6':'OPEN','M6F':'OPEN','M7':'OPEN','M9':'OPEN'}
    (WS/'inventory/client455-fullscreen-effect-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n');print('PARTIAL:ordinary fullscreen motion/GPU18/realintro26/34reviewedframes/Create1 PASS;camera controls/fullstage/QBI/water/bloom/M9 OPEN')
if __name__=='__main__':main()
