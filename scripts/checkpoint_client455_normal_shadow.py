"""Check real shadow target evidence and preserve remaining full-client gaps."""
import hashlib,json,re
from compare_client_binaries import WS,pe
from build_client455_x87_math import read_va

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def load(name):return json.loads((WS/f'inventory/{name}.json').read_text())
def main():
    ref=load('client455-normal-shadow-reference');run=load('client455-normal-renderer-gpu');link=load('client455-normal-link');prep=load('client455-normal-preparation');build=load('client455-normal-build')
    for folder,record in zip(['current','reference-backup'],ref['references']):
        raw=(WS/f'work/client-reference/{folder}/RF_Online.bin').read_bytes()
        if hashlib.sha256(raw).hexdigest()!=record['sha256']:raise ValueError('Changed reference')
        for row in record['functions']:
            if hashlib.sha256(read_va(raw,int(row['rva'],16)+0x400000,row['bytes'])).hexdigest()!=row['sha256']:raise ValueError('Changed shadow body/caller')
        for row in ref['constants']:
            if hashlib.sha256(read_va(raw,int(row['rva'],16)+0x400000,row['bytes'])).hexdigest()!=row['sha256']:raise ValueError('Changed shadow literal')
    if sha(WS/'scripts/audit_client455_normal_shadow.py')!=ref['script_sha256'] or run['shadow_reference_sha256']!=sha(WS/'inventory/client455-normal-shadow-reference.json'):raise ValueError('Stale shadow oracle')
    for name in ['client455_normal_shadow.cpp','client455_normal_shadow.h','client455_normal_shadow_constants.h']:
        if prep['record_inputs'][name]!=sha(WS/'scripts/native'/name):raise ValueError('Changed shadow implementation')
    if ref['constants_header_sha256']!=sha(WS/'scripts/native/client455_normal_shadow_constants.h'):raise ValueError('Changed quad')
    if run['normal_build_sha256']!=sha(WS/'inventory/client455-normal-build.json') or link['normal_build_sha256']!=run['normal_build_sha256'] or build['build_exit'] or build['objects']!=182:raise ValueError('Stale/incomplete normal build')
    if sha(WS/run['exe'])!=run['exe_sha256'] or pe((WS/run['exe']).read_bytes())['entry_rva']!=int(run['entry_rva'],16) or sha(WS/run['output'])!=run['output_sha256'] or sha(WS/run['map'])!=run['map_sha256'] or sha(WS/run['source'])!=run['source_sha256']:raise ValueError('Changed native evidence')
    expected='scripts/native/test_client455_normal_shadow.cpp'
    if run['extra_sources']!=[{'file':expected,'sha256':sha(WS/expected)}]:raise ValueError('Shadow native cases not compiled')
    for item in run['libraries']:
        if sha(WS/item['file'])!=item['sha256']:raise ValueError('Changed library')
    native=run['native'];frame=run['shadow_frame'];pixels=(WS/frame['file']).read_bytes()
    colored=sum(int.from_bytes(pixels[i:i+4],'little')&0xffffff!=0 for i in range(0,len(pixels),4))
    if len(pixels)!=512*512*4 or not 100<colored<512*512-100 or sha(WS/frame['file'])!=frame['sha256'] or sha(WS/frame['preview'])!=frame['preview_sha256']:raise ValueError('Invalid/blank shadow image')
    if native['status']!='PASS' or not native['shadow_capture'] or native['shadow_target_passes']!=3 or not native['real_model_shadow'] or native['shadow_begin_success_return']!=0 or native['device_refs'] or native['dmalloc_balance'] or native['game_dlls_loaded']:raise ValueError('Incomplete native shadow results')
    if not run['precanonical_frames_equal']:raise ValueError('Previous normal renderer behavior changed')
    mapping=(WS/run['map']).read_text(errors='replace')
    for name in ['BeginShadow','EndShadow']:
        if not re.search(r'\?'+name+r'@CRender[^\r\n]+RFClient455Facade:client455_normal_shadow\.obj',mapping):raise ValueError('Missing normal shadow provider')
        if any(name in row['symbol'] for row in link['unresolved']):raise ValueError('Still unresolved shadow method')
    if not link['link_exit'] or link['other_errors'] or not link['unresolved'] or link['legacy_character_linked'] or link['unresolved_forced']:raise ValueError('Inspect new full link state')
    names=['client455-normal-preparation','client455-normal-build','client455-normal-renderer-gpu','client455-normal-link','client455-normal-shadow-reference']
    report={'status':'PARTIAL','normal_shadow_targets':'PASS','capture_protocol_and_selected_failures':'PASS','real_model_shadow':'PASS','two_previous_color_frames_unchanged':True,
        'begin_success_hresult':0,'original_callers_use_bool':True,'shadow_colored_pixels':colored,'device_refs':0,'dmalloc_balance':0,'full_normal_link':'OPEN','remaining_unresolved':link['unique_unresolved'],
        'evidence_sha256':{name:sha(WS/f'inventory/{name}.json') for name in names},'gaps':ref['gaps']+['Effects/particle slots/accounting/Character clock unresolved;full client behavior acceptance open'],
        'input_exe_executed':False,'server_modified':False,'M6':'OPEN','M6F':'OPEN','M7':'OPEN','M9':'OPEN'}
    (WS/'inventory/client455-normal-shadow-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n');print('PARTIAL:normal shadow target/real silhouette PASS;full link'+str(link['unique_unresolved'])+'unresolved;M6/M9OPEN')
if __name__=='__main__':main()
