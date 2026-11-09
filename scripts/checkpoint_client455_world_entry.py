"""Verify139world-entry protocol integration;keep bootstrap/selection/M9 open."""
import json
import re
from pathlib import Path
from checkpoint_client455_login import main as check_login,record
from checkpoint_client455_rvp_effects import check,load,require,sha
from client455_normal_link_evidence import validate_normal_link
from compare_client_binaries import WS


def main():
    check_login()
    link=load('client455-normal-link');link_hash=sha(WS/'inventory/client455-normal-link.json')
    require(validate_normal_link(link)=='PASS','Exact current own binary')
    ref=load('client455-world-entry-reference');check(ref['raw']);check(ref['snapshot']);check(ref['script'])
    require(ref['full_functions']==8 and ref['full_instructions']==1372 and ref['positive_cfg_blocks']==225,'Full selected reference')
    require(ref['references'][0]['functions']==ref['references'][1]['functions'],'Both pins equal for selected bodies')
    for pin in ref['references']:check(pin)
    native=load('client455-account-native')
    require(native['normal_link_sha256']==link_hash and native['natural_exit']==0 and native['native']['status']=='PASS','Actual current account/world component')
    require(native['source_sha256']==sha(WS/native['source']) and native['script_sha256']==sha(WS/'scripts/probe_client455_account.py') and native['builder_sha256']==sha(WS/'scripts/client455_own_probe.py'),'Current native probe')
    for key in ['exe','map','output','world_entry_output']:check(native[key])
    for row in native['inputs']:check(row)
    prep=load('client455-normal-preparation')
    for name in ['client455_world_entry.h','client455_world_entry.inc']:
        require(prep['record_inputs'][name]==native['world_entry_sources'][name]==sha(WS/'scripts/native'/name),'Current normal and native source '+name)
    require(native['world_entry_sources']['client455_world_entry_probe.inc']==sha(WS/'scripts/native/client455_world_entry_probe.inc'),'Current protocol integration cases')
    require(native['world_entry_reference_sha256']==sha(WS/'inventory/client455-world-entry-reference.json'),'Bound to current reference')
    facts=native['world_entry_native'];require(facts['status']=='PASS' and facts['ordinary_request_bytes']==58 and facts['ordinary_response_bytes']==12,'58/12 actual protocol')
    for key in ['request_golden_frame','fullscreen_flag','null_rejected','fragmented_wrapped_encrypted_receiver','request_dialog_closed','failure_response_selectors_retained']:require(facts[key],key)
    require(facts['short_lengths_checked']==12 and facts['result_flag_combinations']==24 and not facts['authentication_performed'] and not facts['bootstrap_or_selection_accepted'],'Boundary scope and explicit acceptance limit')
    login=load('client455-login-checkpoint');require(login['normal_link_sha256']==link_hash,'Fresh ordinary Login gate')
    run=load('client455-login-frame-native');tcp=run['tcp_fixture']
    require(tcp['accepted_connections']==1 and tcp['bytes_received']==67 and tcp['bytes_sent']==0 and tcp['thread_stopped'] and not tcp['rf_protocol_responses'],'Ordinary encrypted entry request reached loopback fixture;no auth peer')
    old_file=WS/'artifacts/client455-progress/before139/inventory/client455-login-frame-native.json'
    old=json.loads(old_file.read_text());require(old['tcp_fixture']['bytes_received']==35,'Preserved older request evidence')
    require(native['asset_staging_script_sha256']==sha(WS/'scripts/client455_asset_staging.py') and native['shared_asset_staging']['new_pool_bytes']==0,'Shared component inputs')
    mapping=(WS/link['map']['file']).read_text();symbols={}
    for method in ['SystemMsg_EnterWorldRequest_zone','SystemMsg_EnterWorldResult_zone','DispatchWorldEntry455']:
        matches=re.findall(r'\?'+method+r'@CNetworkMgr@@\S+\s+([0-9a-fA-F]{8})',mapping)
        require(len(matches)==1,'Ordinary linked method '+method);symbols[method]=hex(int(matches[0],16)-0x400000)
    names=['world-entry-reference','account-native','login-checkpoint','login-frame-native','login-visual','normal-preparation','normal-build','normal-consumers','normal-link','startup-engine-build','own-entry','startup-native','startup-audit']
    result=dict(status='PARTIAL',scope=ref['scope'],script=record(Path(__file__)),normal_link_sha256=link_hash,normal_executable=link['executable'],
        ordinary_methods_rva=symbols,request_payload_bytes=58,response_payload_bytes=12,component=facts,
        ordinary_TCP_request_wire_bytes=dict(before=35,current=67),ordinary_Login_observed=True,
        actual_authentication_performed=False,client_bootstrap_accepted=False,character_selection_accepted=False,full_client=False,
        shared_asset_staging=dict(component=native['shared_asset_staging'],ordinary=run['shared_asset_staging']),
        fresh_evidence={name:record(WS/f'inventory/client455-{name}.json') for name in names},snapshot=ref['snapshot'],
        gaps=ref['gaps']+['Full registered-character/selection acceptance requires its separate gate and real bootstrap/UI consumers',
                           'All historical stage/UI/world/gameplay/lifecycle gaps and docs/client-acceptance.md'],
        input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-world-entry-checkpoint.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('PARTIAL:actual request58/reply12/8fullfunc/real encrypted dispatcher/ordinary67-byte send;bootstrap/selection/full455/M9 OPEN')


if __name__=='__main__':main()
