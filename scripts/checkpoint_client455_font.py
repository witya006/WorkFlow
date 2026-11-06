"""Verify real normal GUI/GDI output without claiming wholeUI/font acceptance."""
import hashlib,json,re
from pathlib import Path
from compare_client_binaries import WS
from build_client455_x87_math import read_va
from client455_normal_link_evidence import validate_normal_link
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(name):return json.loads((WS/f'inventory/{name}.json').read_text())
def main():
    ref=load('client455-font-reference');native=load('client455-font-native');link=load('client455-normal-link');engine=load('client455-startup-engine-build');create=load('client455-create-startup-native');validate_normal_link(link)
    if ref['script_sha256']!=sha(WS/'scripts/audit_client455_font.py') or native['reference_sha256']!=sha(WS/'inventory/client455-font-reference.json') or native['script_sha256']!=sha(WS/'scripts/probe_client455_font.py'):raise ValueError('Stale font oracle/probe')
    for folder,row in zip(['current','reference-backup'],ref['references']):
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';raw=path.read_bytes()
        if sha(path)!=row['sha256']:raise ValueError('Changed455pin')
        for body in row['functions']:
            if hashlib.sha256(read_va(raw,0x400000+int(body['rva'],16),body['bytes'])).hexdigest()!=body['sha256']:raise ValueError('Changed font body')
    for name,digest in native['font_sources'].items():
        if sha(WS/'scripts/native'/name)!=digest:raise ValueError('Changed font source')
    if sha(WS/native['source'])!=native['source_sha256'] or native['normal_link_sha256']!=sha(WS/'inventory/client455-normal-link.json') or sha(WS/native['map'])!=native['map_sha256']:raise ValueError('Changed client GUI evidence')
    for name,digest in engine['text_bridge'].items():
        if sha(WS/'scripts/native'/name)!=digest:raise ValueError('Changed derived text bridge')
    if native['lab_land_initialized_before_exit'] or native['full_game_create_executed']:raise ValueError('Unexpected lab lifecycle scope')
    for run,cp in zip(native['runs'],[949,1251]):
        n=run['native']
        if run['exit'] or n['status']!='PASS' or n['codepage']!=cp or n['colored_pixels']<=10 or not all(n[k] for k in ['real_ui_text_consumer','wide_bridge_equal_frame','gdi_metrics_and_atlas_equal','unicode_cache_reused']):raise ValueError('Incomplete actual UI text scenario')
        for path,digest in [(run['exe'],run['exe_sha256']),(run['output'],run['output_sha256']),(run['frame'],run['frame_sha256']),(run['preview'],run['preview_sha256'])]:
            if sha(WS/path)!=digest:raise ValueError('Changed owned GUI run')
        if len((WS/run['frame']).read_bytes())!=n['width']*n['height']*4:raise ValueError('Short actual frame')
        for row in run['inputs']:
            if sha(WS/row['file'])!=row['sha256']:raise ValueError('Changed actual font/language input')
    mapping=(WS/native['map']).read_text()
    for symbol,provider in [('Draw@CGUIText','guitext.obj'),('DrawR3Hangul','R3Engine455Startup:r3text.obj'),('RF455_DrawLegacyText','RFClient455Facade:client455_font.obj')]:
        if not re.search(re.escape(symbol)+r'[^\r\n]+'+re.escape(provider),mapping):raise ValueError('Missing real provider:'+symbol)
    events=[json.loads(line) for line in (WS/create['events']['file']).read_text(encoding='utf-8').splitlines()]
    if create['normal_link_sha256']!=sha(WS/'inventory/client455-normal-link.json') or not create['summary']['final_checkpoint_reached'] or not create['lab_font_registration_removed'] or not any(e['kind']=='debug_string' and e['value']=='RF455 Font:GDI:129:0' for e in events):raise ValueError('Actual fullPE font initialization/cleanup absent')
    report={'status':'PARTIAL','country_font_parameters':'PASS','gdi_metrics_and_atlas':'PASS','actual_normal_gui_korean_russian_text':'PASS','unicode_cache_hit_eviction':'PASS','actual_fullpe_gdi_font_startup':'PASS','actual_gui_probe_clean_exit':'PASS','full_game_create_executed':False,'evidence_sha256':{name:sha(WS/f'inventory/{name}.json') for name in ['client455-font-reference','client455-font-native','client455-create-startup-native','client455-normal-link','client455-startup-engine-build']},'gaps':ref['gaps']+['Before-Create null-level exit restored by lifecycle047;full ILevel/CMainApp shutdown remains open','Old GUI byteWidth6 layout/clipping is not accepted as455layout;only selected Draw consumer verified','Actual lab backbuffer640x500 vs viewport/configheight480;full window sizing acceptance open'],'input_exe_executed':False,'server_modified':False,'M6':'OPEN','M6F':'OPEN','M7':'OPEN','M9':'OPEN'}
    (WS/'inventory/client455-font-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n');print('PARTIAL:normalGUI Korean/Russian GDI/cache/frame/cleanexit and ownPE fontstartup PASS;fullUI/FT/lifecycle455 OPEN')
if __name__=='__main__':main()
