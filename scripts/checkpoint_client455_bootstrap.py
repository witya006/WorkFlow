"""Bind050implementation/native traces while preservingfull455network/UI gaps."""
import hashlib,json,re
from pathlib import Path
from compare_client_binaries import WS
from build_client455_x87_math import read_va
from client455_normal_link_evidence import validate_normal_link
from audit_client455_own_entry import validated_entry

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(n):return json.loads((WS/f'inventory/{n}.json').read_text())
def check_file(row):
    if sha(WS/row['file'])!=row['sha256']:raise ValueError('Changed bootstrap artifact:'+row['file'])

def main():
    ref=load('client455-bootstrap-reference');native=load('client455-bootstrap-native');link=load('client455-normal-link');prep=load('client455-normal-preparation');ui=load('client455-ui-startup-native');validate_normal_link(link);entry=validated_entry()
    for report,script in [(ref,'audit_client455_bootstrap.py'),(native,'probe_client455_bootstrap.py')]:
        if report['script_sha256']!=sha(WS/'scripts'/script):raise ValueError('Stale bootstrap producer')
    for folder,row in zip(['current','reference-backup'],ref['references']):
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';raw=path.read_bytes()
        if sha(path)!=row['sha256']:raise ValueError('Changed455pin')
        for body in row['ranges']:
            if hashlib.sha256(read_va(raw,0x400000+int(body['rva'],16),body['bytes'])).hexdigest()!=body['sha256']:raise ValueError('Changed bootstrap reference')
    for row in ref['raw_evidence']:check_file(row)
    if sha(Path(ref['fg_input']['file']))!=ref['fg_input']['sha256'] or native['original_fg_sha256']!=ref['fg_input']['sha256']:raise ValueError('Changed realFG fixture')
    if native['builder_sha256']!=sha(WS/'scripts/client455_own_probe.py') or native['source_sha256']!=sha(WS/native['source']):raise ValueError('Stale native source')
    for name,digest in native['sources'].items():
        if sha(WS/'scripts/native'/name)!=digest or prep['record_inputs'][name]!=digest:raise ValueError('Changed bootstrap source:'+name)
    if native['normal_link_sha256']!=sha(WS/'inventory/client455-normal-link.json') or native['reference_sha256']!=sha(WS/'inventory/client455-bootstrap-reference.json'):raise ValueError('Stale bootstrap build/reference')
    for name in ['exe','map','output']:check_file(native[name])
    n=native['native']
    if native['natural_exit'] or native['wrong_filename_exit'] or n['status']!='PASS' or n['country_policies']!=11 or n['core_process_capacity']!=6 or n['tcp_refusal_before_close']!=10061 or n['real_raw_tcp_return']!=n['tcp_error_after_close'] or n['real_invalid_process_error']!=10022 or n['authentication_performed']:raise ValueError('Invalid bootstrap probe result')
    if not all(n[k] for k in ['fg_profile_bounds','instance_name_process_mutex','real_network_created','real_logout_callback']):raise ValueError('Missing native bootstrap boundary')
    mapping=(WS/native['map']['file']).read_text()
    for symbol,provider in [('CreateNetworkMgr455@CMainApp','mainapp.obj'),('ConnectToServer455@CNetworkMgr','cnetworkmgr.obj'),('ConnectRaw455@CNetWorking','networking.obj'),('RF455_AttemptConnect','RFClient455Facade:client455_network_state.obj'),('RF455_CheckSingleInstance','RFClient455Facade:client455_bootstrap.obj')]:
        if not re.search(re.escape(symbol)+r'[^\r\n]+'+re.escape(provider),mapping,re.I):raise ValueError('Missing actual normalprovider:'+symbol)
    for report,expected in [('client455-startup-native','accepted'),('client455-startup-russia-native','country-skip'),('client455-ui-startup-native','accepted')]:
        run=load(report)
        if run['normal_link_sha256']!=native['normal_link_sha256']:raise ValueError('Stale actualbootstraptrace')
        check_file(run['events']);events=[json.loads(line) for line in (WS/run['events']['file']).read_text().splitlines()];debug=[e['value'] for e in events if e['kind']=='debug_string']
        language=next(i for i,s in enumerate(debug) if s.startswith('RF455 NDLanguage:'));fg=debug.index('RF455 FG:0');network=debug.index('RF455 Network:Create:1');instance=debug.index('RF455 Instance:'+expected)
        if not language<fg<network<instance or debug.count('RF455 Network:Create:1')!=1:raise ValueError('Wrong actualbootstraporder/duplicateCreate')
    if not ui['completed_existing_client_create'] or ui['markers'][-1]['name']!='after_client_create' or ui['markers'][-1]['rva']!=entry['points']['after_create']['rva'] or ui['markers'][-1]['eax']!=1:raise ValueError('ExistingCreate regression')
    report={'status':'PARTIAL','FG_profile_raw_int':'PASS','instance_country_name_process_mutex':'PASS','per_process_network_state':'PASS','raw_transport_error_contract':'PASS','target_after_close_error_loss_reproduced':n['tcp_error_after_close']==0,'actual_normal_startup_order_to_instance':'PASS','actual_existing_create_returned':'PASS','authentication_performed':False,'evidence_sha256':{name:sha(WS/f'inventory/{name}.json') for name in ['client455-bootstrap-reference','client455-bootstrap-native','client455-normal-link','client455-startup-native','client455-startup-russia-native','client455-ui-startup-native']},'gaps':ref['gaps'],'input_exe_executed':False,'server_modified':False,'M6':'OPEN','M6F':'OPEN','M7':'OPEN','M9':'OPEN'}
    (WS/'inventory/client455-bootstrap-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n');print('PARTIAL:FG/instance/per-process state/rawTCP/bootstrap order PASS;full455transport/framing/auth/UI/M9 OPEN')
if __name__=='__main__':main()
