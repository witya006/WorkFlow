"""Bind recovered wire contracts to ordinary client methods;M9 stays open."""
import hashlib,json,re
from pathlib import Path
from compare_client_binaries import WS
from build_client455_x87_math import read_va
from client455_normal_link_evidence import validate_normal_link

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(n):return json.loads((WS/f'inventory/{n}.json').read_text())
def check(row):
    if sha(WS/row['file'])!=row['sha256']:raise ValueError('Changed account evidence:'+row['file'])
def main():
    ref=load('client455-account-reference');native=load('client455-account-native');prep=load('client455-normal-preparation');link=load('client455-normal-link');validate_normal_link(link)
    for row,script in [(ref,'audit_client455_account.py'),(native,'probe_client455_account.py')]:
        if row['script_sha256']!=sha(WS/'scripts'/script):raise ValueError('Stale account producer')
    for folder,row in zip(['current','reference-backup'],ref['references']):
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';raw=path.read_bytes()
        if sha(path)!=row['sha256']:raise ValueError('Changed455pin')
        for body in row['ranges']:
            if hashlib.sha256(read_va(raw,0x400000+int(body['rva'],16),body['bytes'])).hexdigest()!=body['sha256']:raise ValueError('Changed455account body')
    check(ref['raw_evidence'])
    if [r['nation'] for r in ref['ticket_profiles'] if r['ticket_profile']]!=[8]:raise ValueError('Changed ticket profile')
    if native['source_sha256']!=sha(WS/native['source']) or native['builder_sha256']!=sha(WS/'scripts/client455_own_probe.py') or native['normal_link_sha256']!=sha(WS/'inventory/client455-normal-link.json') or native['reference_sha256']!=sha(WS/'inventory/client455-account-reference.json'):raise ValueError('Stale account native build')
    for name,digest in native['sources'].items():
        if sha(WS/'scripts/native'/name)!=digest or prep['record_inputs'][name]!=digest:raise ValueError('Changed production account source')
    for key in ['exe','map','output']:check(native[key])
    for row in native['inputs']:check(row)
    n=native['native']
    if native['natural_exit'] or n['status']!='PASS' or n['authentication_performed'] or n['login_bytes']!=342 or n['world_stride']!=72 or n['world_capacity']!=300 or n['maximum_valid_signed_count']!=127:raise ValueError('Incomplete account runtime')
    if not all(n[k] for k in ['actual_gate_accept_request','actual_fragment_wrap_seed_dispatch','actual_request_dialog_open_close','actual_account_send_receive','bounded_world_reload','ticket_profile_packet','mode2_packer_branch']):raise ValueError('Missing actual account consumer')
    mapping=(WS/link['map']['file']).read_text()
    # MSVC inlines the two small account methods into these production callers.
    # The full-object probe also calls DispatchAccount455 directly and retains it.
    for symbol,provider in [('AnalysisServerPacket@CNetworkMgr','cnetworkmgr.obj'),('AcceptClientCheck@CNetworkMgr','cnetworkmgr.obj'),('AccountMsg_LoginAccountRequest_cllo@CNetworkMgr','cnetworkmgr_masterservermsg.obj'),('RF455_PackLogin','RFClient455Facade:client455_account.obj'),('RF455_ReadWorldList','RFClient455Facade:client455_account.obj')]:
        if not re.search(re.escape(symbol)+r'[^\r\n]+'+re.escape(provider),mapping,re.I):raise ValueError('Missing production account provider:'+symbol)
    probe_map=(WS/native['map']['file']).read_text()
    if not re.search(r'DispatchAccount455@CNetworkMgr[^\r\n]+cnetworkmgr\.obj',probe_map,re.I):raise ValueError('Missing direct ordinary dispatcher in probe')
    ui=load('client455-ui-startup-native')
    if ui['normal_link_sha256']!=native['normal_link_sha256'] or not ui['completed_existing_client_create'] or ui['markers'][-1]['eax']!=1:raise ValueError('ExistingCreate regression required')
    report={'status':'PARTIAL','gate_seed_and_login_packet':'PASS','normal_send_receive_dispatch':'PASS','request_dialog_and_zone_predicates':'PASS','bounded_world_list':'PASS','account_and_world_fields':'PASS','existing_Create_regression':'PASS','authentication_performed':False,'evidence_sha256':{name:sha(WS/f'inventory/{name}.json') for name in ['client455-account-reference','client455-account-native','client455-normal-link','client455-ui-startup-native']},'gaps':ref['gaps'],'input_exe_executed':False,'server_modified':False,'M6':'OPEN','M6F':'OPEN','M7':'OPEN','M9':'OPEN'}
    (WS/'inventory/client455-account-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('PARTIAL:gate/account packets,actual dispatch/dialog/worldfields PASS;authentication/full455/M9 OPEN')
if __name__=='__main__':main()
