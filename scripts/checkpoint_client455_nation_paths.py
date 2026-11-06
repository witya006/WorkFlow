"""Verify scoped country/root restoration and actual partial normal Create.

The final marker is BEFORE old character/item/data readers. No full-language,
UI,network or complete455Create claim follows from this checkpoint.
"""
import hashlib,json,re
from pathlib import Path
from compare_client_binaries import WS
from build_client455_x87_math import read_va
from client455_normal_link_evidence import validate_normal_link
from audit_client455_own_entry import validated_entry,symbol

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def load(name):return json.loads((WS/f'inventory/{name}.json').read_text())
def main():
    ref=load('client455-nation-paths-reference');cpu=load('client455-nation-paths-native');run=load('client455-create-startup-native');link=load('client455-normal-link');validate_normal_link(link);entry=validated_entry()
    if ref['script_sha256']!=sha(WS/'scripts/audit_client455_nation_paths.py') or cpu['reference_sha256']!=sha(WS/'inventory/client455-nation-paths-reference.json') or cpu['status']!='PASS' or cpu['countries']!=11:raise ValueError('Incomplete country/reference evidence')
    for folder,record in zip(['current','reference-backup'],ref['references']):
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';raw=path.read_bytes()
        if sha(path)!=record['sha256']:raise ValueError('Changed455pin')
        for row in record['ranges']:
            if hashlib.sha256(read_va(raw,0x400000+int(row['rva'],16),row['bytes'])).hexdigest()!=row['sha256']:raise ValueError('Changed455country contract')
    for name,digest in cpu['source_sha256'].items():
        if sha(WS/'scripts/native'/name)!=digest:raise ValueError('Changed country source')
    for name,key in [('exe','exe_sha256'),('output','output_sha256')]:
        if sha(WS/cpu[name])!=cpu[key]:raise ValueError('Changed CPU evidence')
    if sha(WS/ref['fixture'])!=ref['fixture_sha256']:raise ValueError('Changed reference fixture')
    if run['normal_link_sha256']!=sha(WS/'inventory/client455-normal-link.json') or run['own_entry_sha256']!=sha(WS/'inventory/client455-own-entry.json') or run['early_startup_sha256']!=sha(WS/'inventory/client455-startup-native.json') or not run['partial_client_create']:raise ValueError('Stale actual partial Create')
    helper=run['debugger']
    for path,digest in [(run['staged_executable'],link['executable']['sha256']),(run['events']['file'],run['events']['sha256']),(helper['file'],helper['sha256']),(helper['source'],helper['source_sha256'])]:
        if sha(WS/path)!=digest:raise ValueError('Changed actual execution evidence')
    for row in run['inputs']:
        if sha(WS/row['file'])!=row['sha256']:raise ValueError('Changed actual input')
    events=[json.loads(line) for line in (WS/run['events']['file']).read_text().splitlines()];markers=[e for e in events if e['kind']=='checkpoint'];summary=next(e for e in events if e['kind']=='summary')
    if run['debugger_exit'] or summary!=run['summary'] or not all(summary[k] for k in ['main_reached','after_d3d_reached','final_checkpoint_reached','exit_observed']):raise ValueError('Partial Create marker not reached')
    if markers!=run['markers'] or [m['name'] for m in markers]!=['WinMain','after_sound_before_d3d','after_d3d_before_create','before_character_data'] or markers[1]['eax']!=1 or markers[2]['eax']!=0 or int(markers[-1]['rva'],16)!=int(entry['points']['before_char_data']['rva'],16):raise ValueError('Wrong real startup sequence')
    device=next(e for e in events if e['kind']=='device_state');owner=next(e for e in events if e['kind']=='character_owner');config=next(e for e in events if e['kind']=='render_configuration')
    if device!=run['device_state'] or not device['read'] or device['ready']!=1 or device['windowed']!=1 or not int(device['window'],16) or not int(device['device'],16) or config['fullscreen'] or config['render_bits']!=32:raise ValueError('Invalid actual device')
    if owner!=run['character_owner'] or not owner['read'] or not int(owner['owner'],16) or owner['device']!=device['device']:raise ValueError('Character not bound to normal D3D device')
    if not any(e['kind']=='debug_string' and e['value']=='.\\DataTable\\ko-kr' for e in events):raise ValueError('Actual production country/path init not observed')
    if any(e['kind'].endswith('_error') or e['kind'] in ['timeout','termination_timeout'] or e['kind']=='exception' and not e['first_chance'] for e in events) or next(e['code'] for e in events if e['kind']=='exit')!='0xe0434200':raise ValueError('Unexpected runtime failure/termination')
    mapping=(WS/link['map']['file']).read_text()
    if not re.search(r'\?RF455_InitializeNationPaths@@[^\r\n]+RFClient455Facade:client455_nation_paths\.obj',mapping):raise ValueError('Own WinMain missing production nation provider')
    source=WS/'work/client455-port/normal/source/mainapp.cpp';raw=source.read_bytes()
    if not raw.index(b'RF455_InitializeNationPaths()')<raw.index(b'InitR3Engine();'):raise ValueError('Country configuration not before engine')
    names=['client455-nation-paths-reference','client455-nation-paths-native','client455-own-entry','client455-create-startup-native','client455-normal-link']
    gaps=[g for g in ref['gaps'] if not g.startswith('Actual CRT locale/codepage')]
    gaps.append('Full font/locale/UI acceptance remains open;selected CRT/NDLanguage kernels are verified separately by client455-language-checkpoint.json')
    report={'status':'PARTIAL','country_path_source':'PASS','binary_derived11_country_cases':'PASS','actual_own_winmain_country_root':'PASS','actual_partial_client_create':'PASS','character_bound_to_normal_device':'PASS','actual_create_stop':'Before _CreateCharDataMgr;after Character/bone/mesh/animation/bounds managers','executable':link['executable'],'evidence_sha256':{name:sha(WS/f'inventory/{name}.json') for name in names},'gaps':gaps+['Normal Create data readers/input/UI/LoadData/gameprogress/launcher/normal shutdown remain unexecuted','No reference input EXE execution or full455bootstrap behavior comparison','Renderer/pose/particle/oldCRT/remaining feature registry gaps remain open'],'input_exe_executed':False,'server_modified':False,'M6':'OPEN','M6F':'OPEN','M7':'OPEN','M9':'OPEN'}
    (WS/'inventory/client455-nation-paths-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n');print('PARTIAL:country/path source and actual Character initialization in normal Create PASS;full language/Create/M9 OPEN')
if __name__=='__main__':main()
