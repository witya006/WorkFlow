"""Accept the selected creation-position component,not the whole455actor."""
import json,math
from compare_client_binaries import WS
from checkpoint_client455_rvp_effects import load,sha,check,require

def record(name):
    path=WS/'inventory'/f'{name}.json';return dict(file=path.relative_to(WS).as_posix(),sha256=sha(path))

def main():
    ref=load('client455-equipment-attachment-reference');native=load('client455-equipment-attachment-native')
    for key in ['script','raw','reused_raw','decoder_script','regions_script']:check(ref[key])
    for row in ref['sources']+ref['input_sets']:check(row)
    require(ref['full_functions']==23 and ref['full_instructions']==1953 and ref['positive_cfg_blocks']==223,'Full selected attachment code')
    require(ref['references'][0]['functions']==ref['references'][1]['functions'],'Both pinned455functions equal')
    require(len(ref['position_switch']['entries'])==17 and ref['position_switch']['entries'][9]=='0x7e1127','Type10default switch')
    require(native['reference_sha256']==sha(WS/'inventory/client455-equipment-attachment-reference.json'),'Current attachment reference')
    for key in ['source','script','builder','staging_script','exe','map','console','output']:check(native[key])
    for row in native['inputs']:check(row)
    result=json.loads((WS/native['output']['file']).read_text());require(native['natural_exit']==0 and result==native['native'] and result['status']=='PASS','Real attachment source execution')
    require(result['frozen_position_contracts']==28 and result['real_models']==25 and result['real_named_positions']==25 and result['real_attached_magic']==5 and result['races']==5,'Real selected attachment routes')
    require(len(result['positions'])==75 and all(math.isfinite(x) for x in result['positions']),'Recorded actual positions')
    require(result['archived_player_animation'] and result['missing_target_temporaries_indeterminate'],'Actual pose andexplicit failure limit')
    require(not result['ordinary_player_connected'] and not result['full_appearance'],'Keep ordinary integration open')
    link=load('client455-normal-link');base=load('client455-equipment-checkpoint');check(link['executable'])
    require(native['normal_link_sha256']==base['normal_link_sha256']==sha(WS/'inventory/client455-normal-link.json'),'Ordinary145 unchanged')
    report=dict(status='PARTIAL_COMPONENT',scope=ref['scope'],evidence={name:record(name) for name in ['client455-equipment-attachment-reference','client455-equipment-attachment-native','client455-normal-link']},
        runtime_executable=link['executable'],ordinary_runtime_gate='inventory/client455-equipment-checkpoint.json',ordinary_runtime_changed=False,
        full_functions=23,full_instructions=1953,positive_cfg_blocks=223,real_models=25,real_named_positions=25,real_attached_magic=5,races=5,actual_actor_pose_cache=True,actual_archived_ANI_pose=True,source_magic_translation=True,
        full_failure_fidelity=False,production_player_connected=False,full_player_appearance_or_draw=False,full_client=False,
        gaps=['Missing bone/weapon/bbox target temporaries areindeterminate;own wrapper rejects undefined translation,fullfailure fidelity open','Ordinary effect state/frame/dummy producers andactual CPlayerProc/Avatar/registered equipment integration','Typed4411E0 conditions andremaining bootstrap/appearance/selection/world/M9'],
        input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-equipment-attachment-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PARTIAL_COMPONENT:real five-race part positions/pose cache/attached magic verified;ordinary player/conditions/full failure fidelity/appearance/M9 OPEN.')
if __name__=='__main__':main()
