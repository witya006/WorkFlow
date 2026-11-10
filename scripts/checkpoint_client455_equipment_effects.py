"""Verify effect/loop ownership without accepting pending attachment/conditions."""
import json
from compare_client_binaries import WS
from checkpoint_client455_rvp_effects import load,sha,check,require

def record(name):
    path=WS/'inventory'/f'{name}.json';return dict(file=path.relative_to(WS).as_posix(),sha256=sha(path))
def main():
    ref=load('client455-equipment-effects-reference');native=load('client455-equipment-effects-native')
    for key in ['raw','script','regions_script']:check(ref[key])
    for source in ref['sources']:check(source)
    require(ref['full_functions']==22 and ref['full_instructions']==1489 and ref['positive_cfg_blocks']==222,'Complete selected equipment effect/loop code')
    require(ref['references'][0]['functions']==ref['references'][1]['functions'],'Both455pins match')
    require(native['reference_sha256']==sha(WS/'inventory/client455-equipment-effects-reference.json'),'Fresh effect reference')
    for key in ['source','script','builder','exe','map','console','output']:check(native[key])
    for row in native['inputs']:check(row)
    result=json.loads((WS/native['output']['file']).read_text());require(result==native['native'] and native['natural_exit']==0 and result['status']=='PASS','Actual equipment FX/Miles result')
    require(result['actual_magic_starts']==4 and result['actual_magic_expires']==4 and result['wave_requests']==4 and result['sample_stops']==3,'Real ownership actions')
    require(result['real_cloak_WAV_loop_and_stop'] and result['physical_row_retention'] and result['stop_all_preserves_counts'],'Actual sound/control behavior')
    require(result['creation_position_provider_pending'] and not result['ordinary_player_connected'] and not result['full_conditions'] and not result['full_appearance'],'Keep incomplete dependencies explicit')
    link=load('client455-normal-link');base=load('client455-equipment-checkpoint');check(link['executable'])
    require(native['normal_link_sha256']==base['normal_link_sha256']==sha(WS/'inventory/client455-normal-link.json'),'Ordinary145 unchanged')
    report=dict(status='PARTIAL_COMPONENT',scope=ref['scope'],evidence={name:record(name) for name in ['client455-equipment-effects-reference','client455-equipment-effects-native','client455-normal-link']},
        runtime_executable=link['executable'],ordinary_runtime_gate='inventory/client455-equipment-checkpoint.json',ordinary_runtime_changed=False,
        actual_magic_starts=4,actual_magic_expires=4,real_cloak_WAV_loop_and_stop=True,tracked_registry_source=True,
        full_attachment_positions=False,full_conditions=False,production_player_connected=False,full_player_appearance_or_draw=False,full_client=False,
        gaps=['Complete actual creation-position/bone/dummy provider7E0D10/7E22F0','Typed condition chain4411E0 andgameplay consumers','Ordinary CPlayerProc/Avatar/registered upgrades/frame/render/selection/bootstrap','Unbounded/OOM/unsafe sound-table overflow andallremainingM9 gaps'],
        input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-equipment-effects-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PARTIAL_COMPONENT:actual magic ownership/cloak looped WAV/cleanup/registry source verified;attachment positions/typed conditions/ordinary integration/M9 OPEN.')
if __name__=='__main__':main()
