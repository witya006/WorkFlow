"""Partial authenticated selection frame;lighting andfullstage remain open."""
import json
from pathlib import Path
from compare_client_binaries import WS
from client455_normal_link_evidence import validate_normal_link
from checkpoint_client455_rvp_effects import check,load,require,sha


def record(path):return dict(file=Path(path).relative_to(WS).as_posix(),sha256=sha(path))


def main():
    link=load('client455-normal-link');require(validate_normal_link(link)=='PASS','Current own PE')
    link_hash=sha(WS/'inventory/client455-normal-link.json');ref=load('client455-combat-transition-reference')
    check(ref['script']);check(ref['raw']);check(ref['effects_diagnostics']);check(ref['prior_runtime'])
    for row in ref['sources']:check(row)
    native=load('client455-player-owner-native');n=native['native']
    require(native['normal_link_sha256']==link_hash and native['natural_exit']==0 and n['status']=='PASS','Fresh actual owner test')
    require(n['actual_mounted_weapon_shield_transition'] and n['combat_transition_lowBYTE_FPS'],'Actual transition/fade checks')
    for key in ['exe','map','output','console']:check(native[key])
    for row in native['inputs']+native['sources']+native['frames']:check(row)
    previous=json.loads((WS/'artifacts/client455-progress/before156/inventory/client455-player-owner-native.json').read_text())
    old={Path(row['file']).name:row['sha256'] for row in previous['frames']}
    require(all(old[Path(row['file']).name]==row['sha256'] for row in native['frames']),'Three prior assembled PNGs')
    normal=load('client455-login-frame-taiwan-native');live=load('client455-login-frame-live-taiwan-native');auth=load('client455-live-launcher-native')
    for body in [normal,live]:
        require(body['normal_link_sha256']==link_hash and body['login_frame_captured'] and body['login_render_returned_after_capture'],'Fresh normal/live frame')
        require(not any(not e.get('first_chance') for e in body['exceptions']),'No unhandled normal/live exception')
        for key in ['events','captured_frame','capture_metadata']:check(body[key])
        for row in body['inputs']:check(row)
    require(auth['accepted'] and auth['complete_login_key_received'],'Actual launcher authentication')
    require(live['live_server']['private_handoff_removed'],'Key handoff removed')
    require(not ((WS/live['staged_executable']).parent/'System/DefaultSet.tmp').exists(),'No retained live key file')
    for value in ['RF455 Protocol:tx:1:1:58','RF455 Protocol:rx:1:2:12','RF455 Protocol:world-result:0:0:0','RF455 Protocol:rx:1:9:178']:
        require(value in live['protocol_observations'],'Actual live event '+value)
    names=['combat-transition-reference','player-owner-native','normal-build','normal-consumers','normal-link','normal-preparation','own-entry','startup-audit','startup-taiwan-native','login-frame-taiwan-native','login-frame-live-taiwan-native','live-launcher-native','live-resource-inputs','live-server']
    report=dict(status='PARTIAL',scope='Typed equipped transition andLogin effects lifecycle reach a real authenticated character-selection frame;character lighting is incorrect',
        script=record(Path(__file__)),normal_link_sha256=link_hash,normal_executable=link['executable'],
        fresh_evidence={name:record(WS/f'inventory/client455-{name}.json') for name in names},
        runtime_login_report=record(WS/'inventory/client455-login-frame-live-taiwan-native.json'),
        live_selection_frame=live['captured_frame'],live_capture=live['capture_result'],live_frame_visually_inspected=True,
        live_game_entry_accepted=True,actual_character_visible=True,animation_observed_by_user=True,
        character_lighting_correct=False,live_selection_completed=False,world_entered=False,
        ordinary_Login=True,equal_assembled_render_frames=3,native=n,
        gaps=ref['gaps']+['Ordinary character is nearly black:map lighting/material producer must be restored','Selection input/enter-world andfull455UI remain unverified'],
        full_client=False,input_exe_executed=False,server_modified=False,private_handoff_removed=True,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-combat-transition-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PARTIAL:authenticated own selection frame reached;animation observed;lighting incorrect;M9 OPEN')


if __name__=='__main__':main()
