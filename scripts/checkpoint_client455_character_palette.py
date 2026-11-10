"""Accept only the ordinary Character palette change, not full appearance."""
import collections,json
from pathlib import Path
from compare_client_binaries import WS
from audit_client455_equipment import record
from checkpoint_client455_rvp_effects import load,check,require,sha
from client455_normal_link_evidence import validate_normal_link

def main():
    ref=load('client455-character-palette-reference');native=load('client455-character-palette-native')
    link=load('client455-normal-link');link_hash=sha(WS/'inventory/client455-normal-link.json')
    require(validate_normal_link(link)=='PASS','Current complete link')
    require(ref['full_functions']==7 and ref['full_instructions']==611 and ref['positive_cfg_blocks']==80,'Pinned full reference scope')
    for key in ['raw','reused_raw','script','decoder_script','regions_script','port_script','preparer','original_source_snapshot','runtime_base']:check(ref[key])
    for row in ref['sources']:check(row)
    require(native['reference_sha256']==sha(WS/'inventory/client455-character-palette-reference.json'),'Fresh native reference')
    for key in ['source','script','builder','staging_script','exe','map','console','output']:check(native[key])
    for row in native['inputs']:check(row)
    result=load('client455-character-palette-native')['native']
    require(result==json.loads((WS/native['output']['file']).read_text()) and native['natural_exit']==0 and result['status']=='PASS','Actual ordinary Character execution')
    require(result['ordinary_character_groups']==20 and result['palette_roundtrips']==600 and result['dummy_slots']==13,'All ordinary cache dimensions')
    require(result['two_actor_independence'] and result['grow_shrink_partial_restore'] and result['actual_teardown'],'Cache ownership and lifetime')
    names=['character-palette-reference','character-palette-native','avatar-classes-native','account-native','ui-startup-native','login-frame-native','normal-preparation','normal-build','normal-consumers','normal-link','own-entry','startup-audit','startup-native']
    for name in ['character-palette-native','avatar-classes-native','account-native','ui-startup-native','login-frame-native']:
        require(load('client455-'+name)['normal_link_sha256']==link_hash,'Fresh affected evidence '+name)
    classes=load('client455-avatar-classes-native');require(len(classes['runs'])==3 and all(r['natural_exit']==0 and r['native']['status']=='PASS' for r in classes['runs']),'Three actual Avatar locales')
    for key in ['source','script','builder','map']:check(classes[key])
    for run in classes['runs']:
        for key in ['exe','console','output']:check(run[key])
        for row in run['inputs']:check(row)
    account=load('client455-account-native');require(account['natural_exit']==0 and account['registered_character_native']['actual_Avatar_records']==3,'Affected registered receiver')
    for key in ['exe','map','output','registered_character_output']:check(account[key])
    require(account['script_sha256']==sha(WS/'scripts/probe_client455_account.py'),'Current account probe with private map')
    create=load('client455-ui-startup-native');require(create['completed_existing_client_create'],'Actual own Create')
    login=load('client455-login-frame-native');require(login['first_login_frame_completed'] and login['first_login_frame_captured'] and login['capture_result']['result']==0,'Actual ordinary Login capture')
    old_login_file=WS/'artifacts/client455-progress/before146/inventory/client455-login-frame-native.json'
    old_login=json.loads(old_login_file.read_text())
    exception_profile=lambda body:collections.Counter((e['code'],e['first_chance']) for e in body['exceptions'])
    require(exception_profile(login)==exception_profile(old_login) and all(e['first_chance']==1 for e in login['exceptions']),'No new exception profile or unhandled exception relative to145')
    for key in ['captured_frame','capture_metadata']:check(login[key])
    report=dict(status='PARTIAL',scope=ref['scope'],script=record(Path(__file__)),normal_link_sha256=link_hash,normal_executable=link['executable'],
        fresh_evidence={name:record(WS/f'inventory/client455-{name}.json') for name in names},
        part_groups=20,matrix_palettes=30,character_dummy_slots=13,actual_ordinary_character_code=True,
        actual_Create=True,ordinary_Login_frame=login['captured_frame'],ordinary_Login_capture=login['capture_result'],
        affected_registered_Avatars=3,affected_Avatar_locales=3,prior_exception_profile_evidence=record(old_login_file),
        known_first_chance_exceptions=len(login['exceptions']),unhandled_exceptions=0,
        full_constructor_or_lifecycle=False,full_player_equipment=False,full_appearance_or_selection=False,authentication_performed=False,full_client=False,
        gaps=['Ordinary typed CPlayerProc/Avatar equipment and its draw/animation/effect/condition providers','Remaining bootstrap and complete Title/Login/selection','World/gameplay/protocol/UI/lifecycle and every M9 acceptance domain'],
        input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-character-palette-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PARTIAL:ordinary20x30Character cache/13dummy,affected Avatar/registered receiver/Create/Login verified;full equipment/appearance/selection/M9 OPEN')
if __name__=='__main__':main()
