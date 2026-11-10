"""Partial primary-player integration;preserve full455acceptance requirements."""
import collections,json
from pathlib import Path
from compare_client_binaries import WS
from audit_client455_own_entry import symbol
from audit_client455_equipment import record
from checkpoint_client455_rvp_effects import load,check,require,sha
from client455_normal_link_evidence import validate_normal_link


def main():
    ref=load('client455-player-owner-reference');native=load('client455-player-owner-native')
    draw=load('client455-player-owner-render-native');link=load('client455-normal-link')
    link_hash=sha(WS/'inventory/client455-normal-link.json')
    require(validate_normal_link(link)=='PASS','Exact current linked client')
    for key in ['script','decoder','verifier','preparer','owner_port','prior_runtime']:check(ref[key])
    for row in ref['sources']:check(row)
    for proof in ref['proof']+ref['reused_reference_proof']:check(proof['raw'])
    for body in [native,draw]:
        require(body['normal_link_sha256']==link_hash and body['natural_exit']==0,'Current affected run')
        for key in ['script','exe','map','console','output']:check(body[key])
        for row in body['inputs']+body['frames']:check(row)
        require(body['native']==json.loads((WS/body['output']['file']).read_text()),'Actual native output')
        require(body['native']['status']=='PASS','Native scenario completed')
    for row in native['sources']:check(row)
    for key in ['builder','owner_port','preparer']:check(native[key])
    n=native['native']
    for key in ['primary_typed_controller_connected','ordinary_numeric_puton_baseputoff','actual_Avatar_default_restore','actual_actor_part_cache',
                'replacement_restores_frame','independent_member_copy_raw_links_no_rand_or_retain','clone_cleanup_compensated_only_in_fixture',
                'real_equipment_Avatar_skillboard_payload_icon_route','production_cloak_magic_and_Miles','cloak_missing_specialskill_returnsfalse_after_detach']:
        require(n[key],key)
    require(n['real_controlled_draws']>0 and n['visible_pixels']>0 and n['removal_changes_pixels']>0,'Real geometry contributes pixels')
    require(not n['full_Character_clone_lifecycle'] and not n['full_player_appearance_or_selection'] and not n['full_client'],'Bounded integration only')
    frames={Path(row['file']).name:row for row in native['frames']}
    require(frames['player-owner-dressed.png']['sha256']==frames['player-owner-restored.png']['sha256']!=frames['player-owner-without-shirt.png']['sha256'],'Clothing removal/replacement images')
    for row in draw['source_includes']:check(row)
    check(draw['render_regression']['baseline']);require(draw['render_regression']['equal_frames']==6,'Preserved queue/base/overlay render frames')
    early=load('client455-startup-taiwan-native');create=load('client455-ui-startup-taiwan-native');login=load('client455-login-frame-taiwan-native');account=load('client455-account-native');live=load('client455-startup-live-taiwan-native')
    for body in [early,create,login,account,live]:require(body['normal_link_sha256']==link_hash,'Fresh ordinary/account/live execution')
    require(early['transport_connected'] and early['summary']['after_sound_reached'],'Ordinary Taiwan initial transport/Miles')
    require(create['completed_existing_client_create'] and create['summary']['final_checkpoint_reached'],'Actual Create returned1')
    require(login['first_login_frame_completed'] and login['first_login_frame_captured'] and login['capture_result']['result']==0,'Ordinary Taiwan Login frame')
    for key in ['captured_frame','capture_metadata']:check(login[key])
    profile=collections.Counter((e['code'],e['first_chance']) for e in login['exceptions'])
    require(profile==collections.Counter({('0x406d1388',1):1,('0xe06d7363',1):6}),'Observed Taiwan first-chance profile;no unhandled exceptions')
    require(account['natural_exit']==0 and account['registered_character_native']['actual_Avatar_records']==3 and not account['authentication_performed'],'Affected registered Avatar receiver')
    require(live['transport_connected'] and live['summary']['after_sound_reached'] and live['live_server']['port']==27830 and not live['live_server']['authentication_performed'],'Initial actual server connection;not authentication')
    for key in ['exe','map','output','registered_character_output']:check(account[key])
    build=load('client455-normal-build');engine=load('client455-startup-engine-build')
    require(build['build_exit']==0 and (build['objects'],engine['objects'],build['canonical_kernel_objects'])==(182,67,20),'Complete selected source build')
    check(dict(file=engine['library'],sha256=engine['library_sha256']))
    mapping=(WS/link['map']['file']).read_text();retained={}
    for name in ['?InitEquipment455@CPlayerProc@@QAEXXZ','?RenderEquipment455@CPlayerProc@@QAEXXZ','?AnimateEquipment455@CPlayerProc@@QAEXXZ','?PutOffEquipment455@CAvatar@@QAEHE@Z','?EquipmentSkillLevel455@CAvatar@@UAEXE@Z']:
        retained[name]=hex(symbol(mapping,name)-0x400000)
    names=['player-owner-reference','player-owner-native','player-owner-render-native','account-native','normal-preparation','normal-build','normal-consumers','normal-link','startup-engine-build','startup-contracts-native','startup-taiwan-native','startup-live-taiwan-native','ui-startup-taiwan-native','login-frame-taiwan-native','startup-audit','own-entry']
    report=dict(status='PARTIAL',scope=ref['scope'],script=record(Path(__file__)),normal_link_sha256=link_hash,normal_executable=link['executable'],
        fresh_evidence={name:record(WS/f'inventory/client455-{name}.json') for name in names},prior_runtime=ref['prior_runtime'],native=n,
        retained_methods_rva=retained,runtime_login_report=record(WS/'inventory/client455-login-frame-taiwan-native.json'),
        ordinary_nation='Taiwan',ordinary_Create=True,ordinary_Login_frame=login['captured_frame'],ordinary_Login_capture=login['capture_result'],Login_visually_inspected=True,
        known_first_chance_exceptions=len(login['exceptions']),unhandled_exceptions=0,equal_equipment_render_frames=6,
        primary_controller_connected=True,full_player_appearance_or_selection=False,full_client=False,gaps=ref['gaps'],input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-player-owner-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PARTIAL:primary controller/default restoration/actual skill callback andcloak effects pass;Taiwan Create/Login/account andinitial live server TCP pass;fullappearance/selection/auth/M9 OPEN')


if __name__=='__main__':main()
