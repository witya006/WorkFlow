"""Verify the complete selected wire decoder while retaining runtime111 scope."""
import hashlib,json,struct
from pathlib import Path
from audit_client455_item_payloads import record
from build_client455_x87_math import read_va
from checkpoint_client455_rvp_effects import check,load,require,sha
from client455_normal_link_evidence import validate_normal_link
from compare_client_binaries import WS,pe


def main():
    ref=load('client455-nuclear-protocol-reference');require(ref['script_sha256']==sha(WS/'scripts/audit_client455_nuclear_protocol.py') and (ref['selected_functions'],ref['full_assembly_functions'],ref['instructions'])==(45,22,903),'Reference coverage/provenance');check(ref['raw']);check(ref['session'])
    state=json.loads((WS/ref['session']['file']).read_text());require(state['closed']['success'] and state['closed']['saved'] and state['after']['count']==0,'Owned IDA cleanup')
    pins=json.loads((WS/'config/client-target.json').read_text())
    for folder,key,pin in zip(['current','reference-backup'],['behavior_reference','secondary_reference'],ref['references']):
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';raw=path.read_bytes();require(sha(path)==pins[key]['sha256']==pin['sha256'] and pe(raw)['architecture']=='x86','Actual pinned x86 input')
        for row in pin['ranges']+[pin['internal_flags_zero_store']]:require(hashlib.sha256(read_va(raw,0x400000+int(row['rva'],16),row['bytes'])).hexdigest()==row['sha256'],'Reference bytes')
        for row in pin['decoded_calls']:
            at=0x400000+int(row['rva'],16);data=read_va(raw,at,5);require(data[0]==0xe8 and at+5+struct.unpack('<i',data[1:])[0]==0x400000+int(row['target_rva'],16),'Actual receiver chain')
    require(ref['references'][0]['ranges']==ref['references'][1]['ranges'] and len(ref['packets'])==9,'Two-pin/layout coverage')
    run=load('client455-nuclear-wire-native');require(run['script_sha256']==sha(WS/'scripts/probe_client455_nuclear_wire.py') and run['reference_sha256']==sha(WS/'inventory/client455-nuclear-protocol-reference.json') and not run['natural_exit'],'Native provenance')
    for row in run['sources']+[run['object'],run['library'],run['build_log'],run['exe'],run['output'],run['console']]:check(row)
    require((WS/run['object']['file']).read_bytes()[:2]==b'\x4c\x01' and pe((WS/run['exe']['file']).read_bytes())['architecture']=='x86','x86 artifacts')
    actual=json.loads((WS/run['output']['file']).read_text());require(actual==run['native'] and actual['status']=='PASS' and (actual['checks'],actual['opcodes'],actual['all_result_bytes'],actual['all_list_counts'],actual['list_max_rows'])==(2429,9,256,256,9),'Actual native result')
    for key in ['short_prefixes','null_and_unknown','float_bits_preserved','packed14','output_unchanged_on_failure']:require(actual[key],'Selected parser boundary '+key)
    require(not actual['normal_receiver_integrated'] and not actual['full_client'],'No unjustified runtime acceptance')
    link=load('client455-normal-link');runtime=load('client455-message-dispatch-checkpoint');require(validate_normal_link(link)=='PASS' and runtime['normal_link_sha256']==sha(WS/'inventory/client455-normal-link.json') and runtime['normal_executable']==link['executable'] and link['executable']['sha256']=='031df3676c9bed977f660d79fe535666af9cb52cfc4e5b1a61b3f04841df831c','Runtime111 unchanged')
    engine=load('client455-startup-engine-build');require(sha(WS/engine['library'])==runtime['derived_engine_unchanged'],'Engine unchanged')
    report=dict(status='PARTIAL_COMPONENT',scope=run['scope'],script_sha256=sha(Path(__file__)),reference=record(WS/'inventory/client455-nuclear-protocol-reference.json'),decoder=record(WS/'inventory/client455-nuclear-wire-native.json'),sources=run['sources'],library=run['library'],native_checks=2429,current_runtime_gate=dict(**record(WS/'inventory/client455-message-dispatch-checkpoint.json'),work=111),ordinary_executable_unchanged=link['executable'],derived_engine_unchanged=runtime['derived_engine_unchanged'],normal_receiver_integrated=False,next_work=113,next_action='Restore actual Nuclear processor/ordinary group60 routing with real Character action/internal flags and UI/selection/record owners; do not invent an input callback or ignore nonzero branches',gaps=ref['gaps'],unchanged_runtime_suites_rerun=False,input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-nuclear-wire-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n');print('PARTIAL_COMPONENT:9wire layouts/2429checks/45pinned bodies;actual start via group60 result,not UIcallback;runtime111 unchanged;normalreceiver/M9OPEN')


if __name__=='__main__':main()
