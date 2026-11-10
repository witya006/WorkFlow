"""Verify selected equipment-stat source without accepting ordinary consumers."""
import json
from compare_client_binaries import WS
from checkpoint_client455_rvp_effects import load,sha,check,require

def record(name):
    path=WS/'inventory'/f'{name}.json';return dict(file=path.relative_to(WS).as_posix(),sha256=sha(path))

def main():
    ref=load('client455-equipment-conditions-reference');native=load('client455-equipment-conditions-native')
    for key in ['raw','reused_raw','script','decoder_script','regions_script','expected','synthetic']:check(ref[key])
    for row in ref['sources']:check(row)
    require(ref['full_functions']==52 and ref['full_instructions']==2323 and ref['positive_cfg_blocks']==357,'Selected full condition/provider code')
    require(ref['references'][0]['functions']==ref['references'][1]['functions'],'Both455pinned functions equal')
    require(len(ref['data_regions'])==6 and len(ref['real_cases'])==22,'Pinned switches/weights/vtables andactual cases')
    require(native['reference_sha256']==sha(WS/'inventory/client455-equipment-conditions-reference.json'),'Current native reference')
    for key in ['source','script','builder','staging_script','exe','map','console','output']:check(native[key])
    for row in native['inputs']:check(row)
    result=json.loads((WS/native['output']['file']).read_text());require(result==native['native'] and native['natural_exit']==0 and result['status']=='PASS','Actual source execution')
    require(result['real_item_cases']==22 and result['accepted_items']==21 and result['frozen_contracts']==66,'Selected native conditions')
    require(result['modifier_bytes_match_independent_oracle'] and result['totals_match_independent_oracle'],'Independent real input results')
    require(result['set_predicate_is_runtime_byte113'] and result['detached_remove_after_payload_release'],'Runtime flag anddetached removal source')
    require(result['owner_callbacks_are_recorders'] and not result['ordinary_player_connected'] and not result['full_conditions_or_gameplay'],'Keep required ordinary owners/UI open')
    link=load('client455-normal-link');base=load('client455-equipment-checkpoint');check(link['executable'])
    require(native['normal_link_sha256']==base['normal_link_sha256']==sha(WS/'inventory/client455-normal-link.json'),'Ordinary145 unchanged')
    report=dict(status='PARTIAL_COMPONENT',scope=ref['scope'],evidence={name:record(name) for name in ['client455-equipment-conditions-reference','client455-equipment-conditions-native','client455-normal-link']},
        runtime_executable=link['executable'],ordinary_runtime_gate='inventory/client455-equipment-checkpoint.json',ordinary_runtime_changed=False,
        full_functions=52,full_instructions=2323,positive_cfg_blocks=357,real_item_cases=22,accepted_items=21,modifier_bytes_and_totals_verified=True,
        actual_detached_clone_removal=True,armour_set_predicate_byte113=True,base_player_proc_item_source=True,
        owner_callbacks_are_recorders=True,production_player_connected=False,full_conditions_or_gameplay=False,full_failure_fidelity=False,full_client=False,
        gaps=['Bind actual owner profiles/mount/global bonuses/skill virtual252 andglobal Avatar UI callbacks','Migrate live upgrade113/set-effect/SF/potion producers andallcondition consumers','Ordinary CPlayerProc/Avatar/registered/frame/render/appearance/selection/bootstrap/world/M9','Uninitialised target fields/OOM/out-of-owner reads/concurrent state/complete FPfailure fidelity'],
        input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-equipment-conditions-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PARTIAL_COMPONENT:typed equipment modifiers/upgrades/totals/weakpart andreal22item inputs verified;ordinary owners/UI/producer consumers/full455/M9 OPEN.')
if __name__=='__main__':main()
