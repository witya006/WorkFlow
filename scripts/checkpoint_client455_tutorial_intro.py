"""Accept bounded intro sequencing;keep actual Tutorial/game completeness open."""
import hashlib,json,re
from pathlib import Path
from audit_client455_tutorial_intro_production import layout,normalized
from build_client455_x87_math import read_va
from client455_d3d9_port import ENGINE_DEFINITIONS
from client455_normal_link_evidence import validate_normal_link
from compare_client_binaries import WS,pe

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    def load(name):return json.loads((WS/f'inventory/{name}.json').read_text())
    def check(row):
        if not row or sha(WS/row['file'])!=row['sha256']:raise ValueError('Changed intro evidence:'+str(row))
    reference=load('client455-tutorial-intro-reference');link=load('client455-normal-link');validate_normal_link(link);digest=sha(WS/'inventory/client455-normal-link.json');prep=load('client455-normal-preparation');production=load('client455-tutorial-intro-production');visual=load('client455-tutorial-intro-visual')
    for name,row in [('audit_client455_tutorial_intro.py',reference),('prepare_client455_normal.py',prep),('audit_client455_tutorial_intro_production.py',production),('review_client455_tutorial_intro.py',visual)]:
        if row['script_sha256']!=sha(WS/'scripts'/name):raise ValueError('Stale intro script:'+name)
    check(reference['raw_evidence']);check(reference['generated'])
    if prep['tutorial_intro_reference_sha256']!=sha(WS/'inventory/client455-tutorial-intro-reference.json'):raise ValueError('Stale intro preparation')
    for name in ['client455_tutorial_intro.h','client455_tutorial_intro.cpp','client455_tutorial_intro_camera.cpp']:
        if prep['record_inputs'][name]!=sha(WS/'scripts/native'/name):raise ValueError('Changed intro provider')
    for folder,pin in zip(['current','reference-backup'],reference['references']):
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';raw=path.read_bytes()
        if sha(path)!=pin['sha256']:raise ValueError('Changed455pin')
        for row in pin['ranges']+pin['tables']:
            if hashlib.sha256(read_va(raw,0x400000+int(row['rva'],16),row['bytes'])).hexdigest()!=row['sha256']:raise ValueError('Changed intro reference')
    source=WS/'work/client455-port/normal/generated/client455_tutorial_intro_camera.cpp';cmake=(WS/'work/client455-port/normal/CMakeLists.txt').read_text();definition='set_source_files_properties("'+source.as_posix()+'" PROPERTIES COMPILE_DEFINITIONS "'+';'.join(ENGINE_DEFINITIONS)+'")'
    if definition not in cmake:raise ValueError('Camera backend must share the real engine record definitions')
    if not visual['manually_reviewed'] or len(visual['frames'])!=29:raise ValueError('All intro frames must be reviewed')
    for row in visual['sheets']:check(row)
    observations=[]
    for table in reference['tables']:
        if sha(Path(table['camera']['file']))!=table['camera']['sha256']:raise ValueError('Changed real camera input')
        race=table['race'];manifest=WS/f'inventory/client455-tutorial-intro-{race}-native.json';native=json.loads(manifest.read_text());actual=native['native']
        if native['normal_link_sha256']!=digest or native['reference_sha256']!=sha(WS/'inventory/client455-tutorial-intro-reference.json') or native['source_sha256']!=sha(WS/native['source']) or native['script_sha256']!=sha(WS/'scripts/probe_client455_tutorial_intro.py') or native['builder_sha256']!=sha(WS/'scripts/client455_own_probe.py'):raise ValueError('Stale native intro')
        for key in ['exe','map','console','output','trace']:check(native[key])
        for row in native['inputs']+native['frames']:check(row)
        if native['natural_exit'] or actual['status']!='PASS' or actual!=json.loads((WS/native['output']['file']).read_text()) or pe((WS/native['exe']['file']).read_bytes())['architecture']!='x86':raise ValueError('Native intro failed')
        if actual['selected']!=table['count'] or actual['captures']!=table['count'] or actual['fade_outs']!=table['count'] or actual['warnings'] or actual['memory_before']!=actual['memory_after'] or actual['full_stage_QBI_engine_controls']:raise ValueError('Intro scope/results mismatch')
        if not all(actual[key] for key in ['real_camera_fade_screen_mouse_avatar_world','deferred_skip','reload_retains_counters']):raise ValueError('Intro behaviors failed')
        trace=[json.loads(line) for line in (WS/native['trace']['file']).read_text().splitlines()]
        if len(trace)!=actual['frames'] or {row['ordinal'] for row in trace if row['active']}!=set(range(table['count']+1)) or trace[-1]['active'] or trace[-1]['ordinal']!=table['count'] or not trace[-2]['active'] or trace[-2]['ordinal']!=table['count']:raise ValueError('Actual intro trace missing cuts/deferred completion')
        reviewed=[row for row in visual['frames'] if row['race']==race];expected={f'cut-{index:02d}.bgra' for index in range(table['count'])}|{'debug-first.bgra'}
        if {Path(row['file']).name for row in reviewed}!=expected:raise ValueError('Missing reviewed camera cut')
        for row in reviewed:
            if row['native_sha256']!=sha(manifest) or sha(WS/row['preview'])!=row['preview_sha256'] or (WS/row['file']).stat().st_size!=640*480*4:raise ValueError('Stale intro frame review')
            check(row)
        mapping=(WS/native['map']['file']).read_text()
        for symbol,owner in [('frame@RF455TutorialIntro','RFClient455Facade:client455_tutorial_intro.obj'),('applyCameraMatrix@RF455TutorialIntroCameraHost','RFClient455Facade:client455_tutorial_intro_camera.obj'),('LoadLevel@CLand','cland.obj')]:
            if not re.search(re.escape(symbol)+r'[^\r\n]*'+re.escape(owner),mapping,re.I):raise ValueError('Intro source provider missing:'+symbol)
        observations.append({'race':race,**actual})
    check(production['baseline']);old=(WS/production['baseline']['file']).read_bytes();new=(WS/link['executable']['file']).read_bytes()
    if production['normal_link_sha256']!=digest or not production['same_runtime_bytes_ignoring_link_timestamps'] or layout(old)!=layout(new) or normalized(old)!=normalized(new):raise ValueError('Runtime changed;must select affected regressions anew')
    ui=load('client455-ui-startup-native')
    if ui['normal_link_sha256']!=digest or not ui['completed_existing_client_create'] or ui['markers'][-1]['eax']!=1:raise ValueError('Current exactPE/Create1 required')
    names=['client455-tutorial-intro-reference','client455-tutorial-intro-production','client455-tutorial-intro-visual','client455-normal-preparation','client455-ui-startup-native']+[f'client455-tutorial-intro-{race}-native' for race in ['bellato','cora','accretia']]
    report={'status':'PARTIAL','intro_sequence':'PASS_BOUNDED','real_camera_count':26,'reviewed_frames':29,'observations':observations,'exactPE_Create1':'PASS','unchanged_runtime_against074':True,'evidence_sha256':{name:sha(WS/f'inventory/{name}.json') for name in names},'script_sha256':sha(Path(__file__)),'gaps':reference['gaps'],'input_exe_executed':False,'server_modified':False,'M6':'OPEN','M6F':'OPEN','M7':'OPEN','M9':'OPEN'}
    (WS/'inventory/client455-tutorial-intro-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n');print('PARTIAL:26real cameras/natural and skipped intro/realworld/fade/screen/Avatar/Dmalloc PASS;fullstage/QBI/newengine controls/fourstage/M9 OPEN')
if __name__=='__main__':main()
