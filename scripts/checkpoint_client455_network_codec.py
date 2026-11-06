"""Prove local051contracts without promoting them to complete455network/authentication."""
import hashlib,json,re
from pathlib import Path
from compare_client_binaries import WS
from build_client455_x87_math import read_va
from client455_normal_link_evidence import validate_normal_link

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(name):return json.loads((WS/f'inventory/{name}.json').read_text())
def check_file(row):
    if sha(WS/row['file'])!=row['sha256']:raise ValueError('Changed network codec evidence:'+row['file'])
def main():
    ref=load('client455-network-codec-reference');native=load('client455-network-codec-native');prep=load('client455-normal-preparation');link=load('client455-normal-link');validate_normal_link(link)
    for report,script in [(ref,'audit_client455_network_codec.py'),(native,'probe_client455_network_codec.py')]:
        if report['script_sha256']!=sha(WS/'scripts'/script):raise ValueError('Stale network codec producer')
    for folder,row in zip(['current','reference-backup'],ref['references']):
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';raw=path.read_bytes()
        if sha(path)!=row['sha256']:raise ValueError('Changed455pin')
        for body in row['ranges']:
            if hashlib.sha256(read_va(raw,0x400000+int(body['rva'],16),body['bytes'])).hexdigest()!=body['sha256']:raise ValueError('Changed455network body/data')
    for name in ['raw_evidence','generated_defaults']:check_file(ref[name])
    if prep['network_defaults']!=ref['generated_defaults'] or sha(WS/'work/client455-port/normal/include/client455_network_defaults.h')!=ref['generated_defaults']['sha256']:raise ValueError('Default keys are not the verified compiled input')
    if not ref['forward_and_inverse_schedules_verified'] or ref['rounds']!=12 or ref['direction_keys_equal']:raise ValueError('Unverified/different directional schedules')
    if native['builder_sha256']!=sha(WS/'scripts/client455_own_probe.py') or native['source_sha256']!=sha(WS/native['source']) or native['normal_link_sha256']!=sha(WS/'inventory/client455-normal-link.json') or native['reference_sha256']!=sha(WS/'inventory/client455-network-codec-reference.json'):raise ValueError('Stale native codec build')
    for name,digest in native['sources'].items():
        if sha(WS/'scripts/native'/name)!=digest or prep['record_inputs'][name]!=digest:raise ValueError('Changed codec production source')
    for name in ['exe','map','output']:check_file(native[name])
    n=native['native']
    if native['natural_exit'] or n['status']!='PASS' or n['authentication_performed'] or n['payload_boundaries']!=16 or n['real_network_processes']!=2 or n['process_capacity']!=6 or n['receive_buffer']!=20000 or n['send_buffer']!=1000000 or n['buffer_record_bytes']!=80:raise ValueError('Incomplete native network codec result')
    if not all(n[k] for k in ['independent_cng_aes128_192_256','directional_cbc_zero_padding','bounded_truncation_and_malformed','actual_send_ring_wrap','actual_receive_fragment_wrap_dispatch','normal_group21_cipher_toggle']):raise ValueError('Missing real codec consumer')
    mapping=(WS/native['map']['file']).read_text()
    for symbol,provider in [('LoadSendMsg@CNetProcess','netprocess.obj'),('_PopRecvMsg@CNetProcess','netprocess.obj'),('encode@RF455NetworkCodec','RFClient455Facade:client455_network_codec.obj'),('decode@RF455NetworkCodec','RFClient455Facade:client455_network_codec.obj')]:
        if not re.search(re.escape(symbol)+r'[^\r\n]+'+re.escape(provider),mapping,re.I):raise ValueError('Missing normal network provider:'+symbol)
    ui=load('client455-ui-startup-native')
    if ui['normal_link_sha256']!=native['normal_link_sha256'] or not ui['completed_existing_client_create'] or ui['markers'][-1]['eax']!=1:raise ValueError('Current existingCreate runtime required')
    report={'status':'PARTIAL','AES192_directional_schedules':'PASS','AES_CBC_zero_IV_and_padding_vs_CNG':'PASS','normal_send_receive_buffer_consumers':'PASS','two_configured_six_capacity':'PASS','actual_existing_create_returned':'PASS','authentication_performed':False,'evidence_sha256':{name:sha(WS/f'inventory/{name}.json') for name in ['client455-network-codec-reference','client455-network-codec-native','client455-normal-link','client455-ui-startup-native']},'gaps':ref['gaps']+['Full236byteconfiguration semantic mapping,send filters/throttle/backpressure and internal security messages remain open'],'input_exe_executed':False,'server_modified':False,'M6':'OPEN','M6F':'OPEN','M7':'OPEN','M9':'OPEN'}
    (WS/'inventory/client455-network-codec-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n');print('PARTIAL:source AES/framing/real rings/2process config PASS;full455transport/handlers/auth/UI/M9 OPEN')
if __name__=='__main__':main()
