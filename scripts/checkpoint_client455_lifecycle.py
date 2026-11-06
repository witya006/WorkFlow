"""Keep early-uncreated exit evidence separate from full world/game shutdown."""
import hashlib,json,re
from pathlib import Path
from compare_client_binaries import WS
from build_client455_x87_math import read_va
from client455_normal_link_evidence import validate_normal_link

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(name):return json.loads((WS/f'inventory/{name}.json').read_text())

def main():
    ref=load('client455-lifecycle-reference');native=load('client455-lifecycle-native');font=load('client455-font-native');link=load('client455-normal-link');validate_normal_link(link)
    if ref['script_sha256']!=sha(WS/'scripts/audit_client455_lifecycle.py') or native['script_sha256']!=sha(WS/'scripts/probe_client455_lifecycle.py'):raise ValueError('Stale lifecycle source audit/probe')
    for folder,row in zip(['current','reference-backup'],ref['references']):
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';raw=path.read_bytes()
        if sha(path)!=row['sha256']:raise ValueError('Changed455pin')
        for body in row['ranges']:
            if hashlib.sha256(read_va(raw,0x400000+int(body['rva'],16),body['bytes'])).hexdigest()!=body['sha256']:raise ValueError('Changed455Land contract')
    if native['normal_link_sha256']!=sha(WS/'inventory/client455-normal-link.json') or native['reference_sha256']!=sha(WS/'inventory/client455-lifecycle-reference.json'):raise ValueError('Stale lifecycle binding')
    for path,digest in [(native['source'],native['source_sha256']),(native['normal_land_source']['file'],native['normal_land_source']['sha256']),(native['map'],native['map_sha256'])]:
        if sha(WS/path)!=digest:raise ValueError('Changed lifecycle source/provider')
    mapping=(WS/native['map']).read_text()
    for symbol,provider in [('UnloadLevel@CLand','cland.obj'),('Destroy@CLand','cland.obj'),('??1CLand','cland.obj'),('Destroy@CMainApp','mainapp.obj'),('?g_MainApp@@','mainapp.obj')]:
        if not re.search(re.escape(symbol)+r'[^\r\n]+'+re.escape(provider),mapping):raise ValueError('Actual normal lifecycle provider missing:'+symbol)
    if [r['mode'] for r in native['runs']]!=['uncreated','engine-only','created']:raise ValueError('Missing lifecycle scenarios')
    for run in native['runs']:
        if run['exit'] or run['native']['status_before_crt_exit']!='PASS' or not run['native']['normal_global_owner']:raise ValueError('Actual CRT global exit not observed')
        for path,digest in [(run['exe'],run['exe_sha256']),(run['output'],run['output_sha256'])]:
            if sha(WS/path)!=digest:raise ValueError('Changed lifecycle run')
    if native['debugger_used'] or native['termination_requested'] or native['full_winmain_executed'] or native['full_game_create_executed']:raise ValueError('Wrong lifecycle scope')
    if font['lab_land_initialized_before_exit'] or font['full_game_create_executed'] or font['normal_link_sha256']!=sha(WS/'inventory/client455-normal-link.json') or any(r['exit'] for r in font['runs']):raise ValueError('Font lab still depends on artificial Land initialization')
    report={'status':'PARTIAL','uncreated_land_false_return':'PASS','actual_global_crt_exit_before_engine':'PASS','actual_global_crt_exit_after_engine':'PASS','created_land_repeated_destroy_regression':'PASS','font_gui_exit_without_land_creation':'PASS','evidence_sha256':{name:sha(WS/f'inventory/{name}.json') for name in ['client455-lifecycle-reference','client455-lifecycle-native','client455-font-native','client455-normal-link']},'gaps':ref['gaps'],'input_exe_executed':False,'server_modified':False,'M6':'OPEN','M6F':'OPEN','M7':'OPEN','M9':'OPEN'}
    (WS/'inventory/client455-lifecycle-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n');print('PARTIAL:actual uncreated/engine-only/created normal CRT exit and GUI-without-Land PASS;full455lifecycle OPEN')
if __name__=='__main__':main()
