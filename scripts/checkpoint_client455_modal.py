"""Accept confirmed normal modal controls; full455GUI/game acceptance remains open."""
import hashlib,json,re
from pathlib import Path
from compare_client_binaries import WS,pe
from build_client455_x87_math import read_va
from client455_normal_link_evidence import validate_normal_link
from prepare_client455_normal import kernel_sources

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    def load(name):return json.loads((WS/f'inventory/{name}.json').read_text())
    def check(row):
        if sha(WS/row['file'])!=row['sha256']:raise ValueError('Changed modal evidence:'+row['file'])
    reference=load('client455-modal-reference');native=load('client455-modal-native');link=load('client455-normal-link');validate_normal_link(link)
    if reference['script_sha256']!=sha(WS/'scripts/audit_client455_modal.py')or native['script_sha256']!=sha(WS/'scripts/probe_client455_modal.py')or native['reference_sha256']!=sha(WS/'inventory/client455-modal-reference.json'):
        raise ValueError('Stale modal verification')
    if native['normal_link_sha256']!=sha(WS/'inventory/client455-normal-link.json')or native['builder_sha256']!=sha(WS/'scripts/client455_own_probe.py'):
        raise ValueError('Changed ordinary client input')
    if native['source_sha256']!=sha(WS/native['source']):raise ValueError('Changed modal probe')
    preparation=load('client455-normal-preparation')
    for name,digest in native['sources'].items():
        if sha(WS/'scripts/native'/name)!=digest or preparation['record_inputs'][name]!=digest:raise ValueError('Changed normal modal source:'+name)
    if preparation['script_sha256']!=sha(WS/'scripts/prepare_client455_normal.py'):raise ValueError('Stale GUI source generator')
    manifest=WS/preparation['manifest']
    if sha(manifest)!=preparation['manifest_sha256']:raise ValueError('Changed normal source manifest')
    records=json.loads(manifest.read_text())
    for row in records:
        if '/source/userinterface/guicontroller/'in row['file'].lower()or row['file'].endswith(('client455_font.cpp','client455_modal.cpp')):check(row)
    for row in reference['raw_evidence']+reference['assemblies']:check(row)
    for row in reference['assemblies']:
        body=json.loads((WS/row['file']).read_text())
        if not body['cursor']['done']or len(body['asm']['lines'])!=row['instructions']:raise ValueError('Incomplete modal asm')
    for folder,pin in zip(['current','reference-backup'],reference['references']):
        binary=WS/f'work/client-reference/{folder}/RF_Online.bin'
        if sha(binary)!=pin['sha256']:raise ValueError('Changed455pin')
        raw=binary.read_bytes()
        for row in pin['ranges']+pin['data']:
            if hashlib.sha256(read_va(raw,0x400000+int(row['rva'],16),row['bytes'])).hexdigest()!=row['sha256']:raise ValueError('Changed modal contract')
    for row in reference['inputs']:
        for name in ['sprite','language']:
            if sha(Path(row[name]['file']))!=row[name]['sha256']:raise ValueError('Changed GUI resource')
        frames=row['sprite']['frames']
        if len(frames)!=11 or any((item['width'],item['height'])!=(67,21)for item in frames if item['action']==1):raise ValueError('Unexpected target button dimensions')
    check(native['map']);mapping=(WS/link['map']['file']).read_text()
    for symbol,provider in [('RF455_ConfigureModalButton','RFClient455Facade:client455_modal.obj'),
                            ('RF455_ConfigureModalCaption','RFClient455Facade:client455_modal.obj'),
                            ('RF455_MeasureLegacyText','RFClient455Facade:client455_font.obj'),
                            ('MsgProc@CGUIDialogBox','guidialogbox.obj'),('Init@CGUIMessagebox','guimessagebox.obj')]:
        if not re.search(re.escape(symbol)+r'[^\r\n]*'+re.escape(provider),mapping,re.I):raise ValueError('Missing ordinary modal provider:'+symbol)
    if [row['nation']for row in native['runs']]!=['Korea','Russia']:raise ValueError('Missing country run')
    for row in native['runs']:
        for name in ['exe','output']:check(row[name])
        if pe((WS/row['exe']['file']).read_bytes())['entry_rva']!=int(native['entry_rva'],16):raise ValueError('Wrong own modal entry')
        for item in row['inputs']:check(item)
        for frame in row['frames']:
            check(frame)
            if sha(WS/frame['preview'])!=frame['preview_sha256']or (WS/frame['file']).stat().st_size!=640*480*4:raise ValueError('Changed modal viewport')
        actual=json.loads((WS/row['output']['file']).read_text())
        if actual!=row['native']or actual['status']!='PASS'or row['exit']:raise ValueError('Modal native failed')
        for name in ['real_modal_controls','caption106107','outline_and_margins','keyboard_and_nested','mouse_results123','focused_chat_gate','pool_close_permission','open_reset_and_enable']:
            if not actual[name]:raise ValueError('Missing modal behavior:'+name)
        if actual['button_states']!=5 or actual['viewport_pixels']<=100 or actual['full455_text_scrollbar']or actual['full_Tutorial']:raise ValueError('Wrong modal scope')
        if len(row['frames'])!=5 or actual['pixel_message_sizing_cases']!=12 or not all(actual[key]for key in ['ordinary_rich_wrapper','natural_extent_before_scroll_fallback','empty_extent_unsupported']):raise ValueError('Missing modal sizing/rich checks')
    font=load('client455-font-native')
    if font['normal_link_sha256']!=native['normal_link_sha256']:raise ValueError('Current affected-font regression required')
    if any(row['exit']or row['native']['status']!='PASS'or not row['native']['gdi_metrics_and_atlas_equal']for row in font['runs']):raise ValueError('GDI regression failed')
    ui=load('client455-ui-startup-native')
    if ui['normal_link_sha256']!=native['normal_link_sha256']or not ui['completed_existing_client_create']or ui['markers'][-1]['eax']!=1:raise ValueError('Current existingCreate regression required')
    kernels,_=kernel_sources(WS/'scripts/native')
    if len(kernels)!=20:raise ValueError('Canonical kernel source discovery changed')
    report={'status':'PARTIAL','ordinary_modal_button_bindings':'PASS','localized_captions_and_GDI_route':'PASS',
            'outline_colors_and_margins':'PASS','keyboard_mouse_nested_and_focus':'PASS','actual_existing_Create':'PASS',
            'full455_text_scrollbar':'OPEN','full_Tutorial':'OPEN',
            'evidence_sha256':{name:sha(WS/f'inventory/{name}.json')for name in ['client455-modal-reference','client455-modal-native','client455-normal-link','client455-font-native','client455-ui-startup-native']},
            'gaps':reference['gaps'],'input_exe_executed':False,'server_modified':False,'M6':'OPEN','M6F':'OPEN','M7':'OPEN','M9':'OPEN'}
    (WS/'inventory/client455-modal-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PARTIAL:ordinary modal controls/GDI/keyboard/mouse/nested/focus/Create PASS;full455text/scrollbar/Tutorial/M9 OPEN')
if __name__=='__main__':main()
