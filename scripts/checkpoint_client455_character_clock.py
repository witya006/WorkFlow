"""Verify source Character clock, its real caller/provider and remaining gaps."""
import hashlib,json,re
from compare_client_binaries import WS,pe
from build_client455_x87_math import read_va
from audit_client455_effect_tables import loaded

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def load(name):return json.loads((WS/f'inventory/{name}.json').read_text())
def main():
    ref=load('client455-character-clock-reference');run=load('client455-character-clock-native');link=load('client455-normal-link');prep=load('client455-normal-preparation');build=load('client455-normal-build')
    for folder,item in zip(['current','reference-backup'],ref['references']):
        raw=(WS/f'work/client-reference/{folder}/RF_Online.bin').read_bytes()
        if hashlib.sha256(raw).hexdigest()!=item['sha256']:raise ValueError('Changed455')
        for row in item['functions']+[item['unsigned_bias']]:
            if hashlib.sha256(read_va(raw,0x400000+int(row['rva'],16),row['bytes'])).hexdigest()!=row['sha256']:raise ValueError('Changed timer/caller code')
        for row in item['initial_globals']:
            value=loaded(raw,0x400000+int(row['rva'],16),row['bytes'])
            if any(value) or hashlib.sha256(value).hexdigest()!=row['sha256']:raise ValueError('Changed clock initial image')
    if sha(WS/'scripts/audit_client455_character_clock.py')!=ref['script_sha256'] or sha(WS/ref['golden'])!=ref['golden_sha256'] or run['reference_sha256']!=sha(WS/'inventory/client455-character-clock-reference.json'):raise ValueError('Stale oracle')
    for name in ['client455_character_clock.cpp','client455_character_clock.h','client455_normal_clock.cpp']:
        if sha(WS/'scripts/native'/name)!=prep['record_inputs'][name]:raise ValueError('Changed timer source')
    if build['build_exit'] or build['objects']!=182 or build['canonical_kernel_objects']!=20:raise ValueError('Incomplete normal build')
    for report in [run,link]:
        if report['normal_build_sha256']!=sha(WS/'inventory/client455-normal-build.json'):raise ValueError('Stale normal build')
        for row in report['libraries']:
            if sha(WS/row['file'])!=row['sha256']:raise ValueError('Changed actual dependency')
    if sha(WS/run['exe'])!=run['exe_sha256'] or pe((WS/run['exe']).read_bytes())['entry_rva']!=int(run['entry_rva'],16) or sha(WS/run['output'])!=run['output_sha256'] or sha(WS/run['map'])!=run['map_sha256'] or sha(WS/run['source'])!=run['source_sha256']:raise ValueError('Changed native evidence')
    native=run['native']
    if native['status']!='PASS' or native['failures'] or native['state_cases']!=ref['cases'] or native['fp_modes']!=12 or not all(native[key] for key in ['normal_bridge','engine_clock_independent','initialization_and_fallback']):raise ValueError('Incomplete timer verification')
    mapping=(WS/run['map']).read_text(errors='replace')
    for symbol,unit in [('?_R3CalculateTime@@YAXXZ','client455_normal_clock'),('_RF455_UpdateCharacterClock','client455_character_clock')]:
        if not re.search(re.escape(symbol)+r'[^\r\n]+RFClient455Facade:'+unit+r'\.obj',mapping):raise ValueError('Wrong clock provider')
    caller=WS/'work/client455-port/normal/build/RFClient455Consumers.dir/Release/mainapp.obj'
    if b'?_R3CalculateTime@@YAXXZ' not in caller.read_bytes():raise ValueError('Real client caller lost')
    from client455_normal_link_evidence import validate_normal_link
    link_state=validate_normal_link(link)
    if any('_R3CalculateTime' in row['symbol'] for row in link['unresolved']):raise ValueError('Character clock still unresolved')
    names=['client455-character-clock-reference','client455-character-clock-native','client455-normal-build','client455-normal-preparation','client455-normal-link']
    report={'status':'PARTIAL','source_character_clock':'PASS','actual_normal_bridge':'PASS','engine_clock_independent':'PASS','cases':native['state_cases'],'fp_modes':12,'full_normal_link':'OPEN','remaining_unresolved':1,'actual_caller':{'file':caller.relative_to(WS).as_posix(),'sha256':sha(caller)},'evidence_sha256':{name:sha(WS/f'inventory/{name}.json') for name in names},'gaps':ref['gaps']+['Character accounting still unresolved;normal WinMain/gameplay/UI/network acceptance open'],'input_exe_executed':False,'server_modified':False,'M6':'OPEN','M6F':'OPEN','M7':'OPEN','M9':'OPEN'}
    report['full_normal_link']=link_state;report['remaining_unresolved']=link['unique_unresolved'];report['gaps'][-1]='Normal WinMain/gameplay/UI/network acceptance remains open'
    (WS/'inventory/client455-character-clock-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n');print('PARTIAL:separate Character clock and normal caller PASS;full link '+link_state+';M9OPEN')
if __name__=='__main__':main()
