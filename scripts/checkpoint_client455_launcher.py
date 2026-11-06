"""Keep launcher metadata reconstruction separate from realconnect/auth/455acceptance."""
import hashlib,json,re
from pathlib import Path
from compare_client_binaries import WS
from build_client455_x87_math import read_va
from client455_normal_link_evidence import validate_normal_link
from audit_client455_own_entry import validated_entry

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(name):return json.loads((WS/f'inventory/{name}.json').read_text())

def main():
    ref=load('client455-launcher-reference');native=load('client455-launcher-native');link=load('client455-normal-link');ui=load('client455-ui-startup-native');validate_normal_link(link);entry=validated_entry()
    if ref['script_sha256']!=sha(WS/'scripts/audit_client455_launcher.py') or native['script_sha256']!=sha(WS/'scripts/probe_client455_launcher.py') or native['builder_sha256']!=sha(WS/'scripts/client455_own_probe.py') or native['fixture_generator_sha256']!=sha(WS/'scripts/client455_launcher_fixture.py'):raise ValueError('Stale launcher producer')
    for folder,row in zip(['current','reference-backup'],ref['references']):
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';raw=path.read_bytes()
        if sha(path)!=row['sha256']:raise ValueError('Changed455pin')
        for body in row['ranges']:
            if hashlib.sha256(read_va(raw,0x400000+int(body['rva'],16),body['bytes'])).hexdigest()!=body['sha256']:raise ValueError('Changed targetlauncher body/vtable')
    for name,digest in native['sources'].items():
        if sha(WS/'scripts/native'/name)!=digest:raise ValueError('Changed launcher implementation')
    if native['normal_link_sha256']!=sha(WS/'inventory/client455-normal-link.json') or native['reference_sha256']!=sha(WS/'inventory/client455-launcher-reference.json') or sha(WS/native['source'])!=native['source_sha256'] or sha(WS/native['map'])!=native['map_sha256']:raise ValueError('Changed normal launcher evidence')
    mapping=(WS/native['map']).read_text()
    for symbol,provider in [('GetDataFromLauncher@CMainApp','mainapp.obj'),('SetID@CNetworkMgr','cnetworkmgr.obj'),('SetPassword@CNetworkMgr','cnetworkmgr.obj'),('RF455_InitializeLauncher','RFClient455Facade:client455_launcher.obj')]:
        if not re.search(re.escape(symbol)+r'[^\r\n]+'+re.escape(provider),mapping):raise ValueError('Actual normal launcher provider missing:'+symbol)
    if [r['nation'] for r in native['runs']]!=[0,7,3]:raise ValueError('Missing normal CCR/Russia/Europe cases')
    for run in native['runs']:
        n=run['native']
        if run['exit'] or n['status']!='PASS' or n['ccr_country_profiles']!=9 or n['truncation_cases']!=19 or n['network_created'] or n['connection_attempted'] or not all(n[k] for k in ['file_sharing_missing_extra','argument_count_numeric_bounds','normal_network_fields','identifier50_password32']):raise ValueError('Invalid offline launcher evidence')
        for path,digest in [(run['exe'],run['exe_sha256']),(run['output'],run['output_sha256'])]+[(r['file'],r['sha256']) for r in run['inputs']]:
            if sha(WS/path)!=digest:raise ValueError('Changed synthetic launcher artifact')
    for name,kind in [('client455-startup-native','ccr:1'),('client455-startup-russia-native','argv:0')]:
        run=load(name)
        if run['normal_link_sha256']!=native['normal_link_sha256']:raise ValueError('Stale actual WinMain')
        events=[json.loads(line) for line in (WS/run['events']['file']).read_text().splitlines()]
        debug=[e['value'] for e in events if e['kind']=='debug_string'];position=debug.index('RF455 Launcher:'+kind)
        if not any(s.startswith('.\\DataTable\\') for s in debug[:position]) or not any(s.startswith('RF455 NDLanguage:') for s in debug[position+1:]) or run['sound_return']!=1:raise ValueError('Actual nation/launcher/language/engine order not verified')
    if not ui['completed_existing_client_create'] or ui['normal_link_sha256']!=native['normal_link_sha256'] or ui['markers'][-1]['name']!='after_client_create' or ui['markers'][-1]['rva']!=entry['points']['after_create']['rva'] or ui['markers'][-1]['eax']!=1:raise ValueError('Own normal Create didnotreturn')
    report={'status':'PARTIAL','ccr93_and_country_check':'PASS','argument_profiles':'PASS','real_normal_field_consumers':'PASS','actual_winmain_launcher_before_language':'PASS','own_existing_create_returned':'PASS','authentication_performed':False,'evidence_sha256':{n:sha(WS/f'inventory/{n}.json') for n in ['client455-launcher-reference','client455-launcher-native','client455-startup-native','client455-startup-russia-native','client455-ui-startup-native','client455-normal-link']},'gaps':ref['gaps'],'input_exe_executed':False,'server_modified':False,'M6':'OPEN','M6F':'OPEN','M7':'OPEN','M9':'OPEN'}
    (WS/'inventory/client455-launcher-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n');print('PARTIAL:CCR93/argv/nativefields and actual WinMain launcher-before-language PASS;full455connect/auth/Create/M9 OPEN')
if __name__=='__main__':main()
