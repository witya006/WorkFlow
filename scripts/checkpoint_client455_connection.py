"""Bind actual source connection success/error evidence without claiming authentication."""
import hashlib,json,re
from pathlib import Path
from compare_client_binaries import WS
from build_client455_x87_math import read_va
from client455_normal_link_evidence import validate_normal_link
from audit_client455_own_entry import validated_entry
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(n):return json.loads((WS/f'inventory/{n}.json').read_text())
def check(row):
    if sha(WS/row['file'])!=row['sha256']:raise ValueError('Changed connection artifact:'+row['file'])
def main():
    ref=load('client455-connection-reference');native=load('client455-connection-native');prep=load('client455-normal-preparation');link=load('client455-normal-link');validate_normal_link(link);entry=validated_entry()
    for report,script in [(ref,'audit_client455_connection.py'),(native,'probe_client455_connection.py')]:
        if report['script_sha256']!=sha(WS/'scripts'/script):raise ValueError('Stale connection producer')
    for folder,row in zip(['current','reference-backup'],ref['references']):
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';raw=path.read_bytes()
        if sha(path)!=row['sha256']:raise ValueError('Changed455pin')
        for body in row['ranges']:
            if hashlib.sha256(read_va(raw,0x400000+int(body['rva'],16),body['bytes'])).hexdigest()!=body['sha256']:raise ValueError('Changed455connection range')
    check(ref['raw_evidence'])
    if native['source_sha256']!=sha(WS/native['source']) or native['normal_link_sha256']!=sha(WS/'inventory/client455-normal-link.json') or native['builder_sha256']!=sha(WS/'scripts/client455_own_probe.py') or native['tcp_fixture_sha256']!=sha(WS/'scripts/client455_tcp_fixture.py'):raise ValueError('Stale connection native build')
    for name,digest in native['sources'].items():
        if sha(WS/'scripts/native'/name)!=digest or prep['record_inputs'][name]!=digest:raise ValueError('Changed connection implementation')
    if [r['mode'] for r in native['runs']]!=['positive','timeout','russia']:raise ValueError('Missing connection cases')
    for run in native['runs']:
        for name in ['exe','output','language']:check(run[name])
        n=run['native'];tcp=run['tcp_fixture']
        if run['exit'] or n['status']!='PASS' or n['authentication_performed'] or not all(n[k] for k in ['strict_timeout_and_rollover','accept_delay_boundary','receipt_budget102','profile_dword_wrap']):raise ValueError('Invalid connection result')
        if not tcp['thread_stopped'] or tcp['rf_protocol_responses'] or tcp['bytes_sent'] or tcp['authentication_performed']:raise ValueError('Unexpected TCPfixture behavior')
        if run['mode']=='positive':
            if not n['connected'] or n['timeout'] or not n['raw_error_dialog'] or n['elapsed_ms']<1000 or tcp['accepted_connections']!=1 or n['peer_port']!=tcp['loopback_port']:raise ValueError('Positive result lacks genuine TCP peer')
        elif n['connected'] or not n['timeout'] or n['raw_result']!=0 or n['localized_dialogs']!=1 or tcp['accepted_connections']:raise ValueError('Negative result is not a genuine timeout/error dialog')
    for name in ['client455-startup-native','client455-ui-startup-native']:
        run=load(name);check(run['events']);tcp=run['tcp_fixture']
        if run['normal_link_sha256']!=native['normal_link_sha256'] or run['tcp_fixture_sha256']!=native['tcp_fixture_sha256'] or tcp['accepted_connections']!=1 or not tcp['thread_stopped'] or tcp['bytes_sent'] or tcp['rf_protocol_responses']:raise ValueError('Stale/missing ownWinMain TCPfixture')
        events=[json.loads(line) for line in (WS/run['events']['file']).read_text().splitlines()];debug=[e['value'] for e in events if e['kind']=='debug_string']
        connected=next(i for i,e in enumerate(events) if e.get('value')=='RF455 Connect:connected');sound=next(i for i,e in enumerate(events) if e.get('kind')=='checkpoint' and e.get('name')=='after_sound_before_d3d')
        if debug.index('RF455 Network:Create:1')>=debug.index('RF455 Connect:start:5000') or debug.index('RF455 Connect:start:5000')>=debug.index('RF455 Connect:connected') or connected>=sound:raise ValueError('Actual connect-before-engine sequence absent')
    russia=load('client455-startup-russia-native')
    if not russia['before_connect'] or russia['connection_attempted'] or russia['transport_connected'] or russia['markers'][-1]['rva']!=entry['points']['before_connect']['rva'] or not native['runs'][2]['native']['russia_endpoint_mismatch']:raise ValueError('Current Russianprofile limit not recorded')
    ui=load('client455-ui-startup-native')
    if not ui['completed_existing_client_create'] or ui['markers'][-1]['eax']!=1:raise ValueError('ExistingCreate regression')
    mapping=(WS/link['map']['file']).read_text()
    for symbol,provider in [('ConnectNetwork455@CMainApp','mainapp.obj'),('_Receipt@CNetProcess','netprocess.obj'),('RF455_WaitForConnection','RFClient455Facade:client455_connection.obj')]:
        if not re.search(re.escape(symbol)+r'[^\r\n]+'+re.escape(provider),mapping,re.I):raise ValueError('Missing production connection provider')
    report={'status':'PARTIAL','strict_wait_timeout_wrap':'PASS','delayed_accept_and_budget102':'PASS','genuine_TCP_success_and_localized_errors':'PASS','actual_winmain_connect_before_engine':'PASS','actual_existing_create_returned':'PASS','current_source_Russian_endpoint_gap_recorded':True,'authentication_performed':False,'evidence_sha256':{n:sha(WS/f'inventory/{n}.json') for n in ['client455-connection-reference','client455-connection-native','client455-normal-link','client455-startup-native','client455-startup-russia-native','client455-ui-startup-native']},'gaps':ref['gaps'],'input_exe_executed':False,'server_modified':False,'M6':'OPEN','M6F':'OPEN','M7':'OPEN','M9':'OPEN'}
    (WS/'inventory/client455-connection-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n');print('PARTIAL:realTCP/events/wait/errors and actualWinMain connect-before-engine PASS;authentication/full455/M9 OPEN')
if __name__=='__main__':main()
