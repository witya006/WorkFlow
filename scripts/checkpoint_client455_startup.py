"""Verify exact own PE early startup without promoting it to full455acceptance."""
import hashlib,json,re,struct
from pathlib import Path
from compare_client_binaries import WS,pe
from build_client455_x87_math import read_va
from client455_normal_link_evidence import validate_normal_link
from audit_client455_startup import imports,exported
from audit_client455_own_entry import validated_entry

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def load(name):return json.loads((WS/f'inventory/{name}.json').read_text())
def main():
    audit=load('client455-startup-audit');run=load('client455-startup-native');link=load('client455-normal-link');validate_normal_link(link)
    validated_entry()
    if run['own_entry_sha256']!=sha(WS/'inventory/client455-own-entry.json'):raise ValueError('Stale decoded startup checkpoints')
    if audit['normal_link_sha256']!=sha(WS/'inventory/client455-normal-link.json') or run['normal_link_sha256']!=audit['normal_link_sha256'] or run['audit_sha256']!=sha(WS/'inventory/client455-startup-audit.json'):raise ValueError('Stale full-client startup evidence')
    if audit['script_sha256']!=sha(WS/'scripts/audit_client455_startup.py') or audit['unresolved_provider_modules']:raise ValueError('Incomplete provider audit')
    raw=(WS/link['executable']['file']).read_bytes();current=imports(raw)+imports(raw,True)
    if len(current)!=len(audit['modules']):raise ValueError('Changed PE imports')
    for actual,record in zip(current,audit['modules']):
        if any(actual[k]!=record[k] for k in ['dll','delayed','imports']):raise ValueError('Changed actual import names')
        provider=record['provider'];path=Path(provider['file'])
        if sha(path)!=provider['sha256'] or pe(path.read_bytes())['architecture']!='x86' or provider['missing_exports']:raise ValueError('Changed runtime provider')
        named,ordinals=exported(path.read_bytes())
        if any(not (named.get(s['name']) if 'name' in s else ordinals.get(s['ordinal'])) for s in actual['imports']):raise ValueError('Actual runtime export absent')
    for row in audit['source_inputs']:
        if sha(WS/row['file'])!=row['sha256']:raise ValueError('Changed startup source')
    helper=run['debugger']
    if sha(WS/helper['file'])!=helper['sha256'] or sha(WS/helper['source'])!=helper['source_sha256']:raise ValueError('Changed own debugger')
    if sha(WS/run['events']['file'])!=run['events']['sha256'] or sha(WS/run['staged_executable'])!=link['executable']['sha256']:raise ValueError('Changed exact own startup trace/input')
    for row in run['lab_inputs']:
        if sha(WS/row['file'])!=row['sha256']:raise ValueError('Changed lab input')
    wave=next(row for row in audit['startup_files'] if row['relative']=='Snd/WaveList.spt')
    if next(row['sha256'] for row in run['lab_inputs'] if row['file'].lower().endswith('/snd/wavelist.spt'))!=wave['sha256']:raise ValueError('WaveList differs from audited input')
    for point in run['own_checkpoints']:
        if hashlib.sha256(read_va(raw,pe(raw)['image_base']+int(point['rva'],16),point['bytes'])).hexdigest()!=point['sha256']:raise ValueError('Changed instruction checkpoint')
    events=[json.loads(line) for line in (WS/run['events']['file']).read_text().splitlines()];summary=next(e for e in events if e['kind']=='summary');markers=[e for e in events if e['kind']=='checkpoint']
    if run['debugger_exit'] or summary!=run['summary'] or not all(summary[k] for k in ['main_reached','after_sound_reached','exit_observed']):raise ValueError('Incomplete actual WinMain/sound run')
    if [m['name'] for m in markers]!=['WinMain','after_sound_before_d3d'] or markers!=run['markers'] or markers[-1]['eax']!=1 or run['sound_return']!=1:raise ValueError('Actual sound initialization did not succeed')
    stop=pe(raw)['image_base']+int(markers[-1]['rva'],16);call=read_va(raw,stop-5,5)
    sound_symbol=re.search(r'\?InitR3SoundSystem@@YAHPAD@Z\s+([0-9a-fA-F]{8})',(WS/link['map']['file']).read_text())
    if call[0]!=0xe8 or not sound_symbol or stop+struct.unpack('<i',call[1:])[0]!=int(sound_symbol[1],16):raise ValueError('Marker is not the real sound return')
    if next(e['code'] for e in events if e['kind']=='exit')!='0xe0434200' or any(e['kind'].endswith('_error') or e['kind'] in ['timeout','termination_timeout'] for e in events):raise ValueError('Unexpected startup termination')
    exceptions=[e for e in events if e['kind']=='exception']
    if exceptions!=run['exceptions'] or any(not e['first_chance'] for e in exceptions):raise ValueError('Unhandled startup exception')
    if not all(p['matches_audited_provider'] and sha(Path(p['file']))==p['sha256']==p['expected_sha256'] for p in run['loaded_provider_checks']):raise ValueError('Wrong actual runtime DLL')
    if not {m['dll'] for m in audit['modules'] if not m['delayed']}|{'mss32.dll'}<={p['dll'] for p in run['loaded_provider_checks']}:raise ValueError('Missing actual provider evidence')
    sound=next(p for p in run['loaded_provider_checks'] if p['dll']=='mss32.dll')
    if not Path(sound['file']).samefile((WS/run['staged_executable']).parent/'mss32.dll'):raise ValueError('Sound loaded outside private lab')
    report={'status':'PARTIAL','static_import_provider_names':'PASS','own_pe_crt_and_winmain':'PASS','engine_and_sound_bootstrap':'PASS','actual_miles_startup_return':1,'planned_stop_before_d3d':True,'process_exit_observed':True,'own_executable':link['executable'],'own_checkpoints':run['own_checkpoints'],'handled_first_chance_exception_codes':[e['code'] for e in exceptions],'evidence_sha256':{name:sha(WS/f'inventory/{name}.json') for name in ['client455-startup-audit','client455-startup-native','client455-normal-link']},'gaps':['Window/D3D/Create/launcher/config/data loading/UI/network/full shutdown not executed or accepted by this run','WaveList content and full Miles playback/decoders/3D audio not compared to455','ABuse/Adv/PDLL names exist but were not reached/loaded;filter root paths differ from localized candidates','Original455startup equivalence/full functionality not established;M6/M6F/M7/M9 remain open'],'normal_winmain_executed':True,'input_exe_executed':False,'server_modified':False,'M6':'OPEN','M6F':'OPEN','M7':'OPEN','M9':'OPEN'}
    tcp=run['tcp_fixture']
    if not run['transport_connected'] or not run['connection_attempted'] or run['before_connect'] or tcp['accepted_connections']!=1 or not tcp['thread_stopped'] or tcp['bytes_sent'] or tcp['rf_protocol_responses'] or run['tcp_fixture_sha256']!=sha(WS/'scripts/client455_tcp_fixture.py') or not any(e.get('value')=='RF455 Connect:connected' for e in events):raise ValueError('Initial TCP connection not proved')
    report['genuine_initial_TCP_before_engine']='PASS';report['gaps'][0]='Window/D3D/full455Create/UI/fullprotocol/authentication/gameplay/shutdown not accepted by this early run'
    (WS/'inventory/client455-startup-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n');print('PARTIAL:exact own PE CRT/WinMain/TCP/engine/sound PASS;stopped before D3D;M9 OPEN')
if __name__=='__main__':main()
