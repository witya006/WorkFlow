"""Accept bounded source BSP worlds and ownership,keeping fullclient acceptance open."""
import hashlib,json,re
from pathlib import Path
from build_client455_x87_math import read_va
from client455_normal_link_evidence import validate_normal_link
from compare_client_binaries import WS,pe
from prepare_client455_normal import section
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    def load(name):return json.loads((WS/f'inventory/{name}.json').read_text())
    def check(row):
        if sha(WS/row['file'])!=row['sha256']:raise ValueError('Changed world evidence:'+row['file'])
    link=load('client455-normal-link');validate_normal_link(link);digest=sha(WS/'inventory/client455-normal-link.json');ref=load('client455-world-reference');engine=load('client455-startup-engine-build');prep=load('client455-normal-preparation')
    if ref['script_sha256']!=sha(WS/'scripts/audit_client455_world.py') or prep['script_sha256']!=sha(WS/'scripts/prepare_client455_normal.py') or engine['script_sha256']!=sha(WS/'scripts/build_client455_engine_startup.py'):raise ValueError('Stale world source generator/audit')
    if prep['record_inputs']['client455_land_load.inc']!=sha(WS/'scripts/native/client455_land_load.inc'):raise ValueError('Changed land provider')
    if len(engine['derived_sources'])!=6 or sha(WS/engine['library'])!=engine['library_sha256']:raise ValueError('Wrong derived engine')
    for row in engine['derived_sources']+[engine['baseline_library']]:check(row)
    for row in engine['derived_sources']:
        if sha(WS/row['original'])!=row['original_sha256']:raise ValueError('Changed engine input:'+row['original'])
        if Path(row['file']).name=='level.cpp':
            raw=(WS/row['original']).read_bytes();first,last=section(raw,b'CLevel::~CLevel()',b'CLevel::~CLevel()')
            expected=raw[:first]+(WS/'scripts/native/client455_level_destroy.inc').read_bytes()+raw[last:]
            if (WS/row['file']).read_bytes()!=expected:raise ValueError('Derived level does not contain current destructor source')
    check(ref['raw_evidence'])
    for folder,pin in zip(['current','reference-backup'],ref['references']):
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';raw=path.read_bytes()
        if sha(path)!=pin['sha256']:raise ValueError('Changed455pin')
        for row in pin['ranges']+[pin['vtable_prefix']]:
            if hashlib.sha256(read_va(raw,0x400000+int(row['rva'],16),row['bytes'])).hexdigest()!=row['sha256']:raise ValueError('Changed world reference')
    visual=load('client455-world-visual')
    if not visual['manually_reviewed'] or visual['script_sha256']!=sha(WS/'scripts/review_client455_world.py') or len(visual['frames'])!=6:raise ValueError('Six initial/reload world frames must be reviewed')
    observations=[]
    for mapref in ref['maps']:
        race=mapref['race'];name=f'client455-world-{race}-native';native=load(name)
        if native['normal_link_sha256']!=digest or native['engine_report_sha256']!=sha(WS/'inventory/client455-startup-engine-build.json') or native['script_sha256']!=sha(WS/'scripts/probe_client455_world.py') or native['source_sha256']!=sha(WS/native['source']):raise ValueError('Stale world executable')
        for key in ['exe','map','console','output']:check(native[key])
        for row in native['inputs']+native['frames']:check(row)
        for row in mapref['files'].values():
            if sha(Path(row['file']))!=row['sha256']:raise ValueError('Changed map source')
        actual=json.loads((WS/native['output']['file']).read_text())
        if actual!=native['native'] or native['natural_exit'] or actual['status']!='PASS' or pe((WS/native['exe']['file']).read_bytes())['architecture']!='x86':raise ValueError('World native failed')
        for key,value in mapref['expected'].items():
            if actual[key]!=value:raise ValueError('Independent geometry count mismatch:'+race+'/'+key)
        if actual['warnings'] or actual['pixels']<=100 or not all(actual[key] for key in ['actual_land_owner','reload_and_global_clear','spawn_collision','INS_provider_refused']) or actual['full_ILevel'] or actual['full_Tutorial']:raise ValueError('World scope/observations mismatch')
        if actual['memory_loaded']!=actual['memory_reloaded'] or actual['memory_before']!=actual['memory_after']:raise ValueError('World Dmalloc balance failed')
        reviewed=[row for row in visual['frames'] if row['race']==race]
        if {Path(row['file']).name for row in reviewed}!={'world.bgra','world-reload.bgra'}:raise ValueError('Both initial/reload frames required')
        for frame in reviewed:
            if frame['native_sha256']!=sha(WS/f'inventory/{name}.json'):raise ValueError('World visual review stale')
            check(frame)
            if sha(WS/frame['preview'])!=frame['preview_sha256'] or (WS/frame['file']).stat().st_size!=640*480*4:raise ValueError('World image changed')
        mapping=(WS/native['map']['file']).read_text()
        for symbol,owner in [('LoadLevel@CLand','cland.obj'),('??1CLevel','R3Engine455Startup:level.obj')]:
            if not re.search(re.escape(symbol)+r'[^\r\n]*'+re.escape(owner),mapping,re.I):raise ValueError('World source provider missing:'+symbol)
        observations.append({'race':race,**mapref['expected'],'height':actual['spawn_height'],'Dmalloc_loaded':actual['memory_loaded']})
    ui=load('client455-ui-startup-native')
    if ui['normal_link_sha256']!=digest or not ui['completed_existing_client_create'] or ui['markers'][-1]['eax']!=1:raise ValueError('Current exact Create1 required')
    for name in ['client455-account-native','client455-briefing-window-native']:
        native=load(name)
        if native['normal_link_sha256']!=digest:raise ValueError('Current dependent consumer required:'+name)
        if 'runs' in native:
            if any(row['exit'] or row['native']['status']!='PASS' for row in native['runs']):raise ValueError('GUI regression failed')
        elif native['natural_exit'] or native['native']['status']!='PASS':raise ValueError('Account regression failed')
    names=['client455-world-reference','client455-world-visual','client455-startup-engine-build','client455-ui-startup-native','client455-account-native','client455-briefing-window-native']+[f'client455-world-{r}-native' for r in ['bellato','cora','accretia']]
    report={'status':'PARTIAL','actual_BSP_worlds':'PASS','load_reload_release_Dmalloc':'PASS','real_spawn_collision':'PASS_BOUNDED','source_opaque_GPU_frames_reviewed':6,'exactPE_Create1':'PASS','observations':observations,'sources':{name:sha(WS/'scripts/native'/name) for name in ['client455_land_load.inc','client455_level_destroy.inc']},'script_sha256':sha(Path(__file__)),'evidence_sha256':{name:sha(WS/f'inventory/{name}.json') for name in names},'gaps':ref['gaps'],'input_exe_executed':False,'server_modified':False,'M6':'OPEN','M6F':'OPEN','M7':'OPEN','M9':'OPEN'}
    (WS/'inventory/client455-world-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n');print('PARTIAL:3actualBSP worlds/CLand/reload/release/collision/GPU/Create1 PASS;fullILevel/INS/Tutorial/fourstage/M9 OPEN')
if __name__=='__main__':main()
