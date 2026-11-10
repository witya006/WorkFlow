"""Check the current partial client without promoting a component to acceptance."""
import collections,json
from pathlib import Path
from compare_client_binaries import WS
from audit_client455_equipment import record
from checkpoint_client455_rvp_effects import load,check,require,sha
from client455_normal_link_evidence import validate_normal_link
from checkpoint_client455_equipment_draw import production_calls

def main():
    ref=load('client455-player-visual-reference');native=load('client455-player-visual-native')
    draw=load('client455-equipment-draw-native');link=load('client455-normal-link')
    link_hash=sha(WS/'inventory/client455-normal-link.json')
    require(validate_normal_link(link)=='PASS','Current normal link')
    require((ref['full_functions'],ref['full_instructions'],ref['positive_cfg_blocks'])==(11,684,107),'Complete selected player functions')
    require((ref['rand_reference']['full_functions'],ref['rand_reference']['full_instructions'])==(1,9),'Complete target PRNG')
    for key in ['raw','rand_raw','script','decoder','verifier','preparer','runtime_base']:check(ref[key])
    for row in ref['sources']:check(row)
    require(ref['physical_equipment_slots']==12 and ref['array_offset']+12*ref['slot_bytes']==ref['first_field_after_array']==7744,'Correct physical array')
    require(not ref['target_index12_is_constructed'] and not ref['ordinary_controller_connected'],'Do not perpetuate previous13-slot claim')
    require(ref['target_rand_recurrence']['first_values']==[3660,150,7964] and ref['target_rand_recurrence']['thirteenth']==9923,'Frozen binary-derived PRNG oracle')
    for proof in [native,draw]:
        require(proof['normal_link_sha256']==link_hash,'Fresh affected native execution')
        for key in ['source','script','exe','map','console','output']:check(proof[key])
        for row in proof['inputs']+proof.get('source_includes',[])+proof.get('frames',[]):check(row)
        require(proof['natural_exit']==0 and proof['native']==json.loads((WS/proof['output']['file']).read_text()) and proof['native']['status']=='PASS','Actual native result')
    check(native['reference'])
    n=native['native'];d=draw['native']
    require(n['physical_equipment_slots']==12 and n['unsafe_index12_refusal_cases']==3 and not n['unsafe_target_index12_accepted'],'Explicit unsupported unsafe target domain')
    require(n['visibility_cases']==24 and n['constructor_rand_cases']==3,'Actual visibility and constructor/copy checks')
    require(n['real_models_loaded']==32 and n['gpu_texture_entries']==33 and n['player_controller_real_creations']==30 and n['payloads_after_teardown']==0,'Real resources and teardown')
    require(not n['player_controller_production_connected'] and n['condition_animation_callbacks_are_probe_recorders'] and not n['full_player_appearance_or_draw'],'Keep full player integration open')
    require((d['primary_draws'],d['overlay_draws'],d['matrix_draws'])==(7,14,7) and d['visible_model_pixels']==d['changed_overlay_pixels']==2659,'Affected model render regression')
    require(d['actual_alpha_restore'] and d['fade_render_gate'] and d['queue_four_matrix_aliasing'] and d['queue_shared_payload_teardown'] and d['queue_cap']==256,'Affected queue/alpha regression')
    require(not d['actual_nonzero_particle_effects'] and not d['full_player_appearance'],'Do not claim particles or actor')
    previous=WS/'artifacts/client455-progress/before150/inventory'
    old_draw=json.loads((previous/'client455-equipment-draw-native.json').read_text())
    frames=lambda p:{Path(f['file']).name:f['sha256'] for f in p['frames']}
    require(frames(draw)==frames(old_draw),'Six controlled frames preserved from149')
    for name in ['account-native','startup-native','ui-startup-native','login-frame-native']:
        require(load('client455-'+name)['normal_link_sha256']==link_hash,'Fresh ordinary evidence '+name)
    build=load('client455-normal-build');engine=load('client455-startup-engine-build')
    require((build['objects'],engine['objects'],build['canonical_kernel_objects'])==(182,67,20),'Selected complete build')
    require(load('client455-startup-contracts-native')['build_sha256']==sha(WS/'inventory/client455-startup-engine-build.json'),'Unchanged engine contract evidence')
    check(dict(file=engine['library'],sha256=engine['library_sha256']))
    create=load('client455-ui-startup-native');login=load('client455-login-frame-native');account=load('client455-account-native')
    require(create['completed_existing_client_create'] and login['first_login_frame_completed'] and login['first_login_frame_captured'] and login['capture_result']['result']==0,'Ordinary Create/Login preserved')
    for key in ['captured_frame','capture_metadata']:check(login[key])
    old_login=json.loads((previous/'client455-login-frame-native.json').read_text())
    profile=lambda r:collections.Counter((e['code'],e['first_chance']) for e in r['exceptions'])
    require(profile(login)==profile(old_login) and all(e['first_chance']==1 for e in login['exceptions']),'No new or unhandled exception profile')
    require(account['natural_exit']==0 and account['registered_character_native']['actual_Avatar_records']==3 and not account['authentication_performed'],'Affected records;not authentication')
    for key in ['exe','map','output','registered_character_output']:check(account[key])
    calls=production_calls(link)
    names=['player-visual-reference','player-visual-native','equipment-draw-native','account-native','normal-preparation','normal-build','normal-consumers','normal-link','startup-engine-build','startup-contracts-native','startup-native','startup-audit','own-entry','ui-startup-native','login-frame-native','character-draw-build','renderer-owner-build']
    report=dict(status='PARTIAL',scope=ref['scope'],script=record(Path(__file__)),normal_link_sha256=link_hash,normal_executable=link['executable'],
        fresh_evidence={name:record(WS/f'inventory/client455-{name}.json') for name in names},prior_runtime=ref['runtime_base'],
        physical_equipment_slots=12,previous13_slot_claim_superseded=True,unsafe_target_index12_accepted=False,
        visibility_cases=24,constructor_rand_cases=3,native=n,affected_draw_native=d,frames=draw['frames'],same_six_controlled_frames_as149=True,
        ordinary_calls=calls,ordinary_queue_entrypoints_connected=True,secondary_geometry_retained_in_normal_PE=True,
        ordinary_player_connected=False,complete_particle_registry=False,actual_nonzero_particle_effects=False,
        ordinary_Create=True,ordinary_Login_frame=login['captured_frame'],ordinary_Login_capture=login['capture_result'],
        known_first_chance_exceptions=len(login['exceptions']),unhandled_exceptions=0,Login_visually_inspected=True,
        full_appearance_or_selection=False,full_client=False,gaps=ref['gaps'],input_exe_executed=False,server_modified=False,
        M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-player-visual-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PARTIAL:12 constructed slots and visibility/PRNG verified;ordinary Create/Login preserved;full player/selection/M9 OPEN')

if __name__=='__main__':main()
