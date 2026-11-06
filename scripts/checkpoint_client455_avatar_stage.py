"""Accept actual Avatar/MainApp/network wiring;keep real Tutorial integration open."""
import hashlib,json,re,subprocess
from pathlib import Path
from build_client455_x87_math import read_va
from client455_normal_link_evidence import validate_normal_link
from compare_client_binaries import WS
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    def load(name):return json.loads((WS/f'inventory/{name}.json').read_text())
    def check(row):
        if sha(WS/row['file'])!=row['sha256']:raise ValueError('Changed evidence:'+row['file'])
    link=load('client455-normal-link');validate_normal_link(link);digest=sha(WS/'inventory/client455-normal-link.json');ref=load('client455-avatar-stage-reference');prep=load('client455-normal-preparation')
    if ref['script_sha256']!=sha(WS/'scripts/audit_client455_avatar_stage.py') or prep['script_sha256']!=sha(WS/'scripts/prepare_client455_normal.py'):raise ValueError('Stale stage audit/generator')
    source_names=['client455_avatar_stage.h','client455_avatar_stage.cpp','client455_avatar_stage.inc','client455_tutorial_dispatch.inc','client455_account_bridge.inc']
    sources={name:sha(WS/'scripts/native'/name) for name in source_names}
    for name,value in sources.items():
        if prep['record_inputs'][name]!=value:raise ValueError('Stale stage source:'+name)
    for row in ref['raw_evidence']:check(row)
    for folder,pin in zip(['current','reference-backup'],ref['references']):
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';raw=path.read_bytes()
        if sha(path)!=pin['sha256']:raise ValueError('Changed455pin')
        for row in pin['ranges']+pin['vtables']:
            if hashlib.sha256(read_va(raw,0x400000+int(row['rva'],16),row['bytes'])).hexdigest()!=row['sha256']:raise ValueError('Changed stage reference')
    for row in ref['scene_inputs']:
        if sha(Path(row['file']))!=row['sha256']:raise ValueError('Changed Tutorial map/camera')
    account=load('client455-account-native')
    if account['normal_link_sha256']!=digest or account['source_sha256']!=sha(WS/account['source']) or account['script_sha256']!=sha(WS/'scripts/probe_client455_account.py'):raise ValueError('Stale actual stage/account probe')
    for row in [account['exe'],account['output'],account['map'],*account['inputs']]:check(row)
    actual=json.loads((WS/account['output']['file']).read_text())
    if actual!=account['native'] or actual['status']!='PASS' or account['natural_exit']:raise ValueError('Account native observation changed')
    for key in ['actual_Avatar_stage_skip','actual_MainApp_Create_gate','legacy_main2_maps_to455_main3','actual_login_Tutorial_transform']:
        if not actual[key]:raise ValueError('Missing real stage observation:'+key)
    if actual['full_fourstage_factory'] or actual['authentication_performed']:raise ValueError('Stage scope broadened')
    mapping=(WS/account['map']['file']).read_text()
    for symbol,owner in [('RF455_IsTutorialAvatarStage','cavatar.obj'),('GameMainLoop@CMainApp','mainapp.obj'),('SendNetMessage@CNetworkMgr','cnetworkmgr.obj')]:
        if not re.search(re.escape(symbol)+r'[^\r\n]*'+re.escape(owner),mapping,re.I):raise ValueError('Missing ordinary source provider:'+symbol)
    startup=load('client455-ui-startup-native')
    if startup['normal_link_sha256']!=digest or not startup['completed_existing_client_create'] or startup['markers'][-1]['eax']!=1:raise ValueError('Current own Create1 missing')
    window=load('client455-briefing-window-native');board=load('client455-tutorial-board-native')
    if window['normal_link_sha256']!=digest or board['normal_link_sha256']!=digest or board['natural_exit'] or not board['native']['source_briefing_window'] or board['native']['rich_view_is_test_fixture']:raise ValueError('Current source window/board regression missing')
    if window['source_sha256']!=sha(WS/window['source']):raise ValueError('Changed window singleton guard probe')
    for row in window['runs']:
        if row['exit'] or row['native']['status']!='PASS':raise ValueError('Window regression failed')
        for value in [row['exe'],row['output'],*row['frames']]:check(value)
    def prior(name):return json.loads(subprocess.check_output(['git','-c','safe.directory='+str(WS),'show','687b88c:inventory/'+name+'.json'],cwd=WS))
    old=prior('client455-briefing-window-native');visual=prior('client455-briefing-window-visual')
    if not visual['manually_reviewed']:raise ValueError('Missing prior visual review')
    if len(old['runs'])!=2 or len(window['runs'])!=2:raise ValueError('Both Ko/Ru window runs required')
    frames=0
    for before,after in zip(old['runs'],window['runs']):
        def hashes(run):return {Path(row['file']).name:row['sha256'] for row in run['frames']}
        if before['nation']!=after['nation'] or hashes(before)!=hashes(after):raise ValueError('Window image changed;fresh visual review required')
        frames+=len(after['frames'])
    names=['client455-avatar-stage-reference','client455-account-native','client455-briefing-window-native','client455-tutorial-board-native','client455-ui-startup-native','client455-normal-link']
    report={'status':'PARTIAL','actual_Avatar_stage_skip':'PASS','actual_MainApp_Create_gate':'PASS','stage2_login_and_local_route':'PASS_BOUNDED','missing_local_handlers':'EXPLICIT_FAILURE_OPEN','PostUI_Screen_singleton_guard':'PASS','existingCreate1':'PASS','window_GPU_frames_equal_reviewed072':frames,'visual_review_reused_from_commit':'687b88c','sources':sources,'script_sha256':sha(Path(__file__)),'evidence_sha256':{name:sha(WS/f'inventory/{name}.json') for name in names},'gaps':ref['gaps'],'input_exe_executed':False,'server_modified':False,'M6':'OPEN','M6F':'OPEN','M7':'OPEN','M9':'OPEN'}
    (WS/'inventory/client455-avatar-stage-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n');print('PARTIAL:actual Avatar/MainApp/login/local-route/Screen-post/22unchangedframes/Create1 PASS;local handlers/fullTutorial/fourstage/M9 OPEN')
if __name__=='__main__':main()
