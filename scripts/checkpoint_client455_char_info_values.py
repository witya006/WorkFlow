"""Current stat-writer runtime gate,explicitly short offull455Avatar/UI behavior."""
import collections,json
from pathlib import Path
from compare_client_binaries import WS
from audit_client455_equipment import record
from checkpoint_client455_rvp_effects import load,check,require,sha
from client455_normal_link_evidence import validate_normal_link

def main():
    ref=load('client455-char-info-values-reference');native=load('client455-char-info-values-native');link=load('client455-normal-link')
    link_hash=sha(WS/'inventory/client455-normal-link.json')
    require(validate_normal_link(link)=='PASS','Current normal link')
    require((ref['full_functions'],ref['full_instructions'],ref['positive_cfg_blocks'])==(6,185,9),'Complete selected stat writer reference')
    for key in ['raw','script','verifier','decoder','preparer','prior_runtime']:check(ref[key])
    for row in ref['sources']:check(row)
    for key in ['reference','source','script','builder','exe','map','console','output']:check(native[key])
    for row in native['inputs']:check(row)
    require(native['normal_link_sha256']==link_hash and native['natural_exit']==0 and native['architecture']=='x86','Fresh source execution')
    n=native['native'];require(n==json.loads((WS/native['output']['file']).read_text()) and n['status']=='PASS','Actual native result')
    require(n['actual_window_value_owners']==5 and n['actual_basicrow_child_registration']==3,'Actual value owners andordinarywindow binding')
    require(n['full_DWORD_values_preserved'] and n['float_setters_not_empty'] and n['legacy_labels_preserved'] and n['actual_current_Avatar_caller'],'Ordinary widths/text/caller checks')
    require(not n['full455_Avatar_metric_producers'] and not n['full455_Avatar_refresh'] and not n['full455_window_layout'] and not n['full_client'],'Preserve unimplemented metric/layout/fullclient requirements')
    for name in ['account-native','startup-native','ui-startup-native','login-frame-native']:
        require(load('client455-'+name)['normal_link_sha256']==link_hash,'Fresh affected ordinary run '+name)
    build=load('client455-normal-build');engine=load('client455-startup-engine-build')
    require((build['objects'],engine['objects'],build['canonical_kernel_objects'])==(182,67,20),'Complete selected build')
    require(load('client455-startup-contracts-native')['build_sha256']==sha(WS/'inventory/client455-startup-engine-build.json'),'Unchanged engine contracts')
    check(dict(file=engine['library'],sha256=engine['library_sha256']))
    create=load('client455-ui-startup-native');login=load('client455-login-frame-native');account=load('client455-account-native')
    require(create['completed_existing_client_create'] and login['first_login_frame_completed'] and login['first_login_frame_captured'] and login['capture_result']['result']==0,'Ordinary Create/Login')
    for key in ['captured_frame','capture_metadata']:check(login[key])
    old=json.loads((WS/'artifacts/client455-progress/before152/inventory/client455-login-frame-native.json').read_text())
    profile=lambda p:collections.Counter((e['code'],e['first_chance']) for e in p['exceptions'])
    require(profile(login)==profile(old) and all(e['first_chance']==1 for e in login['exceptions']),'No new or unhandled exception profile')
    require(account['natural_exit']==0 and account['registered_character_native']['actual_Avatar_records']==3 and not account['authentication_performed'],'Affected realAvatar records;not authentication')
    for key in ['exe','map','output','registered_character_output']:check(account[key])
    names=['char-info-values-reference','char-info-values-native','account-native','normal-preparation','normal-build','normal-consumers','normal-link','startup-engine-build','startup-contracts-native','startup-native','startup-audit','own-entry','ui-startup-native','login-frame-native','character-draw-build','renderer-owner-build']
    report=dict(status='PARTIAL',scope=ref['scope'],script=record(Path(__file__)),normal_link_sha256=link_hash,normal_executable=link['executable'],
        fresh_evidence={name:record(WS/f'inventory/client455-{name}.json') for name in names},prior_runtime=ref['prior_runtime'],native=n,
        ordinary_stat_writers_connected=True,full455_Avatar_metric_producers=False,full455_Avatar_refresh=False,full455_window_layout=False,
        ordinary_Create=True,ordinary_Login_frame=login['captured_frame'],ordinary_Login_capture=login['capture_result'],Login_visually_inspected=True,
        known_first_chance_exceptions=len(login['exceptions']),unhandled_exceptions=0,ordinary_full_player_connected=False,
        full_appearance_or_selection=False,full_client=False,gaps=ref['gaps'],input_exe_executed=False,server_modified=False,
        M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-char-info-values-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PARTIAL:ordinary32bit/float stat writers andbasicrow owners verified;Create/Login preserved;fullAvatar455metrics/layout/player/M9 OPEN')

if __name__=='__main__':main()
