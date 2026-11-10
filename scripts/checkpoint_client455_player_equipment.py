"""Verify146 component without promoting it to an ordinary client runtime."""
import json
from pathlib import Path
from compare_client_binaries import WS
from checkpoint_client455_rvp_effects import load,sha,check,require

def record(name):
    path=WS/'inventory'/f'{name}.json';return dict(file=path.relative_to(WS).as_posix(),sha256=sha(path))

def main():
    ref=load('client455-player-equipment-reference');native=load('client455-player-equipment-native')
    check(ref['script']);check(ref['raw']);check(ref['snapshot']);check(ref['runtime_base'])
    for source in ref['sources']:check(source)
    require(ref['full_functions']==32 and ref['full_instructions']==1640 and ref['positive_cfg_blocks']==225,'Complete selected static controller/clone evidence')
    require(ref['references'][0]['functions']==ref['references'][1]['functions'],'Selected reference regions equal')
    require(ref['references'][0]['rtti']==ref['references'][1]['rtti'],'Controller/clone RTTI equal')
    require(ref['owner_pointer_call_confirmed'],'Equipment owner argument must not become Player.SetPrevAction')
    require(native['controller_reference_sha256']==sha(WS/'inventory/client455-player-equipment-reference.json'),'Fresh controller reference')
    for key in ['source','controller','script','builder','exe','map','console','output']:check(native[key])
    for row in native['inputs']:check(row)
    result=json.loads((WS/native['output']['file']).read_text())
    require(result==native['native'] and native['natural_exit']==0 and result['status']=='PASS','Native component result')
    require(result['player_controller_real_creations']==30 and result['real_models_loaded']==32 and result['gpu_texture_entries']==33,'Real selected inputs')
    require(result['payloads_after_teardown']==0,'Controller/default teardown')
    require(result['condition_animation_callbacks_are_probe_recorders'] and not result['player_controller_production_connected'] and not result['full_player_appearance_or_draw'],'Keep required production providers open')
    link=load('client455-normal-link');base=load('client455-equipment-checkpoint')
    require(native['normal_link_sha256']==base['normal_link_sha256']==sha(WS/'inventory/client455-normal-link.json'),'Unchanged145 ordinary build')
    check(link['executable']);require(link['executable']['sha256']==base['normal_executable']['sha256'],'Actual145 PE unchanged')
    report=dict(status='PARTIAL_COMPONENT',scope=ref['scope'],static_functions=32,static_instructions=1640,positive_cfg_blocks=225,
        evidence={name:record(name) for name in ['client455-player-equipment-reference','client455-player-equipment-native','client455-equipment-checkpoint','client455-normal-link']},
        runtime_executable=link['executable'],ordinary_runtime_gate='inventory/client455-equipment-checkpoint.json',ordinary_runtime_changed=False,
        real_controller_model_creations=30,source_clone_implemented=True,production_controller_connected=False,full_player_appearance_or_draw=False,ordinary_selection_accepted=False,full_client=False,
        gaps=['Production animation/condition/effect providers and actual CPlayerProc integration','Complete12-slot rendering/animation loop and other actor appearance consumers','Ordinary appearance/selection/bootstrap/world/gameplay and fullM9'],
        input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-player-equipment-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PARTIAL_COMPONENT:13-slot controller/normal clone and real-resource execution verified;production providers/appearance/selection/M9 OPEN. Ordinary145 runtime unchanged.')
if __name__=='__main__':main()
