"""Check real ANI/fade providers without promoting full player integration."""
import json
from compare_client_binaries import WS
from checkpoint_client455_rvp_effects import load,sha,check,require

def record(name):
    path=WS/'inventory'/f'{name}.json';return dict(file=path.relative_to(WS).as_posix(),sha256=sha(path))

def main():
    ref=load('client455-equipment-providers-reference');native=load('client455-equipment-providers-native')
    for key in ['raw','script','decoder_script','regions_script','resource_script','expected']:check(ref[key])
    for row in ref['sources']:check(row)
    require(ref['full_functions']==24 and ref['full_instructions']==2220 and ref['positive_cfg_blocks']==373,'Full selected provider code')
    require(ref['references'][0]['functions']==ref['references'][1]['functions'],'Both455pins match')
    require(len(ref['cases'])==65 and len(ref['selected_animations'])==48 and len(ref['selected_models'])==12 and not ref['missing'],'Selected real assets accounted')
    zero=[case for case in ref['cases'] if case['found'] and not case['ani_maximum']]
    require(zero,'Preserve actual zero-maximum ANI as a successful load')
    require(native['reference_sha256']==sha(WS/'inventory/client455-equipment-providers-reference.json'),'Current native reference')
    for key in ['source','script','builder','exe','map','console','output']:check(native[key])
    for row in native['inputs']:check(row)
    result=json.loads((WS/native['output']['file']).read_text())
    require(native['natural_exit']==0 and result==native['native'] and result['status']=='PASS','Real provider execution')
    require(result['cases']==65 and result['animation_successes']==64 and result['animation_failures']==1 and result['actual_pose_calls']==64 and result['owner_lifts']==20,'Real pose/fallback/failure/lift results')
    require(result['fade_actual_source'] and result['animation_selection_actual_source'],'Actual source providers')
    require(result['item_effect_callback_is_recorder'] and not result['ordinary_player_connected'] and not result['full_appearance'],'Keep item-effect and integration gaps explicit')
    link=load('client455-normal-link');base=load('client455-equipment-checkpoint')
    require(native['normal_link_sha256']==base['normal_link_sha256']==sha(WS/'inventory/client455-normal-link.json'),'Ordinary145 unchanged')
    check(link['executable']);require(link['executable']['sha256']==base['normal_executable']['sha256'],'Exact ordinary145 PE')
    report=dict(status='PARTIAL_COMPONENT',scope=ref['scope'],evidence={name:record(name) for name in ['client455-equipment-providers-reference','client455-equipment-providers-native','client455-player-equipment-checkpoint','client455-normal-link']},
        runtime_executable=link['executable'],ordinary_runtime_gate='inventory/client455-equipment-checkpoint.json',ordinary_runtime_changed=False,
        real_animations=48,real_models=12,successful_animation_selections=64,expected_animation_failures=1,actual_pose_calls=64,owner_lifts=20,
        actual_animation_fade_source=True,full_item_animation_effects=False,full_condition_effects=False,production_controller_connected=False,full_player_appearance_or_draw=False,full_client=False,
        gaps=['Actual item animation effect provider46D3D0/cleanup/sound/attachment','Typed condition ApplyItemEffect4411E0 and full consumers','Ordinary CPlayerProc/Avatar/registered upgrades/animation/render/appearance/selection/bootstrap','All remaining client acceptance/M9 gaps'],
        input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-equipment-providers-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PARTIAL_COMPONENT:real equipment ANI/pose/fallback/failure/fade/height source verified;item effects/conditions/ordinary integration/appearance/M9 OPEN.')
if __name__=='__main__':main()
