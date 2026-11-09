"""Verify actual registered-character protocol/Avatar integration;keep M9 open."""
import json,re
from pathlib import Path
from checkpoint_client455_world_entry import main as check_world_entry
from checkpoint_client455_login import record
from checkpoint_client455_rvp_effects import check,load,require,sha
from compare_client_binaries import WS


def main():
    check_world_entry()
    link=load('client455-normal-link');link_hash=sha(WS/'inventory/client455-normal-link.json')
    ref=load('client455-registered-characters-reference');check(ref['raw']);check(ref['snapshot']);check(ref['script'])
    require(ref['full_functions']==9 and ref['full_instructions']==623 and ref['positive_cfg_blocks']==72,'Full selected record/actor reference')
    for pin in ref['references']:check(pin)
    require(ref['references'][0]['functions']==ref['references'][1]['functions'],'Both pins equal')
    probe=load('client455-account-native');require(probe['normal_link_sha256']==link_hash and probe['natural_exit']==0,'Fresh actual receiver/Avatar run')
    native=probe['registered_character_native'];require(native['status']=='PASS' and native['response_bytes']==506 and native['record_stride']==164 and native['actual_Avatar_records']==3,'Three real Avatar consumers')
    for key in ['actual_request1_8','actual_encrypted_receiver1_9','fragment_wrap','full64bit_money_time','level0_tutorial_writer','zero_count_retains_state']:require(native[key],key)
    require(not native['bootstrap_or_visual_selection_accepted'],'Do not widen acceptance')
    check(probe['registered_character_output'])
    prep=load('client455-normal-preparation')
    for name in ['client455_registered_characters.h','client455_registered_characters.inc']:
        require(prep['record_inputs'][name]==probe['registered_character_sources'][name]==sha(WS/'scripts/native'/name),'Normal/native source '+name)
    require(probe['registered_character_sources']['client455_registered_characters_probe.inc']==sha(WS/'scripts/native/client455_registered_characters_probe.inc'),'Current record scenarios')
    source=WS/'work/client455-port/normal/source/network/protocol/pt_zone_client.h';data=source.read_bytes()
    require(re.search(rb'#define\s+reged_char_request_zone\s+8\b',data) and re.search(rb'#define\s+reged_char_result_zone\s+9\b',data),'Source protocol numbers8/9')
    mapping=(WS/link['map']['file']).read_text();methods={}
    for name in ['SystemMsg_RegedCharRequest_zone','SystemMsg_RegedCharResult_zone','DispatchRegisteredCharacters455']:
        matches=re.findall(r'^\s+\S+\s+\?'+name+r'@CNetworkMgr@@\S+\s+([0-9a-fA-F]{8})\b',mapping,re.M)
        require(len(matches)==1,'Normal linked method '+name);methods[name]=hex(int(matches[0],16)-0x400000)
    inputs=['registered-characters-reference','account-native','world-entry-checkpoint','login-checkpoint','login-frame-native','login-visual','normal-preparation','normal-build','normal-link','startup-engine-build','startup-native','startup-audit','own-entry']
    out=dict(status='PARTIAL',scope=ref['scope'],script=record(Path(__file__)),normal_link_sha256=link_hash,normal_executable=link['executable'],
        response_payload_bytes=506,record_stride=164,actor_records_applied=3,ordinary_methods_rva=methods,component=native,
        fresh_evidence={name:record(WS/f'inventory/client455-{name}.json') for name in inputs},snapshot=ref['snapshot'],
        full_bootstrap=False,full_character_appearance=False,full_class_tier_names=False,ordinary_selection_UI_accepted=False,full_client=False,
        gaps=ref['gaps'],input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-registered-characters-checkpoint.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('PARTIAL:request1/8,reply1/9,506/164,real3Avatar/64bitmoney-time/tutorial writer;bootstrap/appearance/selection/full455/M9 OPEN')


if __name__=='__main__':main()
