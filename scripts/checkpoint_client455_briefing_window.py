"""Bind source briefing evidence without promoting it to full Tutorial acceptance."""
import hashlib,json,re
from pathlib import Path
from build_client455_x87_math import read_va
from client455_normal_link_evidence import validate_normal_link
from compare_client_binaries import WS,pe
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    def load(name):return json.loads((WS/f'inventory/{name}.json').read_text())
    def check(row):
        if sha(WS/row['file'])!=row['sha256']:raise ValueError('Changed evidence:'+row['file'])
    link=load('client455-normal-link');validate_normal_link(link);digest=sha(WS/'inventory/client455-normal-link.json')
    ref=load('client455-briefing-window-reference');native=load('client455-briefing-window-native');visual=load('client455-briefing-window-visual');prep=load('client455-normal-preparation')
    if prep['script_sha256']!=sha(WS/'scripts/prepare_client455_normal.py'):raise ValueError('Stale generator')
    if ref['script_sha256']!=sha(WS/'scripts/audit_client455_briefing_window.py') or native['reference_sha256']!=sha(WS/'inventory/client455-briefing-window-reference.json') or native['script_sha256']!=sha(WS/'scripts/probe_client455_briefing_window.py'):raise ValueError('Stale reference or probe')
    if native['normal_link_sha256']!=digest or native['source_sha256']!=sha(WS/native['source']) or native['builder_sha256']!=sha(WS/'scripts/client455_own_probe.py'):raise ValueError('Stale source build')
    for name,value in native['sources'].items():
        if value!=sha(WS/'scripts/native'/name) or prep['record_inputs'][name]!=value:raise ValueError('Changed source:'+name)
    for row in ref['raw_evidence']:check(row)
    for folder,pin in zip(['current','reference-backup'],ref['references']):
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';raw=path.read_bytes()
        if sha(path)!=pin['sha256']:raise ValueError('Changed455pin')
        for row in pin['ranges']+[pin['vtable']]:
            if hashlib.sha256(read_va(raw,0x400000+int(row['rva'],16),row['bytes'])).hexdigest()!=row['sha256']:raise ValueError('Changed455range')
    check(native['map']);mapping=(WS/native['map']['file']).read_text()
    for symbol in ['Continue455@CGUIBriefingWindow','Update@CGUIBriefingWindow','showRichMessage@RF455TutorialBriefingWindow']:
        if not re.search(re.escape(symbol)+r'[^\r\n]*RFClient455Facade:client455_briefing_window.obj',mapping,re.I):raise ValueError('Window probe lost real source provider:'+symbol)
    frames=0
    for run in native['runs']:
        for key in ['exe','output']:check(run[key])
        actual=json.loads((WS/run['output']['file']).read_text())
        if run['exit'] or actual!=run['native'] or actual['status']!='PASS' or actual['actual_Tutorial_stage'] or pe((WS/run['exe']['file']).read_bytes())['architecture']!='x86':raise ValueError('Window native failed or scope broadened')
        if actual['pages']<2 or actual['frames']!=11:raise ValueError('Missing page/portrait observations')
        for key in ['actual_briefing_provider','capture_input_message','capture_removed_live_object','typing_and_continue','posted_close_event','three_real_portraits','portrait_random_timer']:
            if not actual[key]:raise ValueError('Missing observation:'+key)
        for row in run['inputs']+run['frames']:check(row)
        for row in run['frames']:
            if (WS/row['file']).stat().st_size!=640*480*4 or sha(WS/row['preview'])!=row['preview_sha256']:raise ValueError('Changed window GPU readback');
            frames+=1
    if visual['native_sha256']!=sha(WS/'inventory/client455-briefing-window-native.json') or visual['script_sha256']!=sha(WS/'scripts/review_client455_briefing_window.py') or not visual['manually_reviewed']:raise ValueError('Window frames not manually reviewed')
    for row in visual['sheets']:check(row)
    startup=load('client455-ui-startup-native')
    if startup['normal_link_sha256']!=digest or not startup['completed_existing_client_create'] or startup['markers'][-1]['eax']!=1:raise ValueError('Current exact PE Create failed')
    dependencies=['client455-gui-input-native','client455-modal-native','client455-minimap-opacity-native']
    for name in dependencies:
        row=load(name)
        if row['normal_link_sha256']!=digest or any(r['exit'] or r['native']['status']!='PASS' for r in row['runs']):raise ValueError('Changed affected GUI:'+name)
        for name,value in row['sources'].items():
            if sha(WS/'scripts/native'/name)!=value:raise ValueError('Changed GUI source:'+name)
    board=load('client455-tutorial-board-checkpoint')
    if board['source_CGUIBriefingWindow']!='PASS' or board['production_host']!='OPEN':raise ValueError('Actual board source bridge required')
    names=['client455-briefing-window-reference','client455-briefing-window-native','client455-briefing-window-visual','client455-tutorial-board-checkpoint','client455-ui-startup-native']+dependencies
    report={'status':'PARTIAL','source_window_provider':'PASS','outline_portrait_pages_buttons_keys':'PASS','real_screen_capture_input_message':'PASS','board_uses_source_view':'PASS','GPU_frames_reviewed':frames,'exact_PE_existingCreate1':'PASS','full_Tutorial':'OPEN','ordinary_stage_factory_Avatar_world':'OPEN','full_briefing_acceptance':'OPEN','gaps':ref['gaps'],'script_sha256':sha(Path(__file__)),'evidence_sha256':{name:sha(WS/f'inventory/{name}.json') for name in names},'input_exe_executed':False,'server_modified':False,'M6':'OPEN','M6F':'OPEN','M7':'OPEN','M9':'OPEN'}
    (WS/'inventory/client455-briefing-window-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n');print('PARTIAL:source briefing/provider/capture/board/22GPU/Create1 PASS;actual Tutorial/Avatar/world/M9 OPEN')
if __name__=='__main__':main()
