"""Verify a partial ordinary Login result;keep full455Login/M9 open."""
import json
import re
from pathlib import Path
from audit_client455_own_entry import validated_entry
from checkpoint_client455_rvp_effects import require, check, load, sha
from client455_normal_link_evidence import validate_normal_link
from compare_client_binaries import WS


def record(path):
    return dict(file=path.relative_to(WS).as_posix(),sha256=sha(path))


def main():
    link=load('client455-normal-link');link_hash=sha(WS/'inventory/client455-normal-link.json')
    require(validate_normal_link(link)=='PASS','Current normal link')
    prep=load('client455-normal-preparation')
    require(prep['script_sha256']==sha(WS/'scripts/prepare_client455_normal.py'),'Current source generator')
    check(dict(file=prep['manifest'],sha256=prep['manifest_sha256']))
    ref=load('client455-login-registration-reference')
    require(ref['script']['sha256']==sha(WS/'scripts/audit_client455_login_registration.py'),'Current static verifier')
    check(ref['evidence']);require(ref['full_functions']==5 and ref['full_instructions']==221 and ref['positive_cfg_blocks']==21,'Selected full reference scope')
    require(ref['references'][0]['functions']==ref['references'][1]['functions'],'Equal selected bodies in two pins')
    for pin in ref['references']:check(pin)
    run=load('client455-login-frame-native');early=load('client455-startup-native');audit=load('client455-startup-audit')
    require(run['normal_link_sha256']==early['normal_link_sha256']==audit['normal_link_sha256']==link_hash,'Fresh ordinary run')
    require(run['script_sha256']==sha(WS/'scripts/probe_client455_device_startup.py') and early['script_sha256']==sha(WS/'scripts/probe_client455_startup.py'),'Current runtime drivers')
    require(not run['debugger_exit'] and run['summary']['exit_observed'] and run['login_render_returned_after_capture'] and run['login_frame_captured'],'Actual Render returned after capture and own process exited')
    require(not [event for event in run['exceptions'] if not event.get('first_chance')],'No fatal native exception')
    require(run['device_state']['ready']==1 and run['device_state']['windowed']==1,'Actual own D3D device')
    require(run['stage_state']['created']==run['stage_state']['loaded']==1,'Ordinary Login created and loaded')
    require(run['capture_result']['result']==0 and run['capture_result']['frame_index']>1 and run['capture_result']['elapsed_ms']>=3200,'Settled real frame,not frame1')
    for key in ['events','captured_frame','capture_metadata']:check(run[key])
    for row in run['inputs']:check(row)
    require(run['executable']==link['executable'],'Exact current own executable')
    providers=early['loaded_provider_checks']
    require(run['early_startup_sha256']==sha(WS/'inventory/client455-startup-native.json') and early['sound_return']==1 and providers and all(row['matches_audited_provider'] for row in providers) and not audit['unresolved_provider_modules'],'Own WinMain/Miles/providers')
    require(run['debugger']['source_sha256']==sha(WS/'scripts/native/own_client_startup_debugger.cpp'),'Current debugger source')
    check(run['debugger']);check(early['events'])
    require(validated_entry()['normal_link_sha256']==link_hash,'Decoded own entry')
    require(run['lobby_inputs_staged'] and run['shared_asset_staging']['assets']==43 and run['shared_asset_staging']['new_pool_bytes']==0,'Actual lobby and shared assets')
    require(run['asset_staging_script_sha256']==sha(WS/'scripts/client455_asset_staging.py'),'Current shared staging')
    review=load('client455-login-visual');check(review['native_report']);check(review['before_report']);check(review['after'])
    require(review['manually_reviewed'] and review['after']==run['captured_frame'] and not review['full455Login_UI_accepted'],'Inspected partial UI result')
    mapping=(WS/link['map']['file']).read_text()
    found=re.findall(r'\?Add@CGUIScreen@@\S+\s+([0-9a-fA-F]{8})',mapping)
    require(len(found)==1,'Ordinary root registration retained in linked own PE')
    source=WS/'work/client455-port/normal/source/userinterface/guicontroller/guiscreen.cpp'
    raw=source.read_bytes();start=raw.index(b'CGUIScreen::Add( CGUIWindow * pi_pWindow )');end=raw.index(b'CGUIScreen::Remove(',start);body=raw[start:end]
    require(body.index(b'AddFront455')<body.index(b'SetParent(this)')<body.index(b'Show(FALSE)'),'Confirmed root registration order in normal source')
    snapshot=WS/'artifacts/client455-progress/login138-before-window-registration/manifest.json'
    before=json.loads(snapshot.read_text());require(len(before)==13,'Frozen previous own build')
    for row in before:check(row)
    engine=load('client455-startup-engine-build');check(dict(file=engine['library'],sha256=engine['library_sha256']))
    historical=WS/'artifacts/client455-progress/before138/inventory/client455-startup-engine-build.json'
    require(json.loads(historical.read_text())['library_sha256']==engine['library_sha256'],'Engine137 unchanged')
    names=['login-registration-reference','login-frame-native','login-visual','normal-preparation','normal-build','normal-consumers','normal-link','startup-engine-build','own-entry','startup-native','startup-audit']
    out=dict(status='PARTIAL',scope='Ordinary own WinMain/Title/Login render with real lobby and recovered root registration;not complete455Title/Login/auth',
        script=record(Path(__file__)),normal_link_sha256=link_hash,normal_executable=link['executable'],engine_sha256=engine['library_sha256'],
        ordinary_root_registration=dict(rva=hex(int(found[0],16)-0x400000),source=record(source)),
        restored=['Localized455sprite filenames for existing legacy mouse/common/loading/login/main consumers','Root null/AlwaysTop insertion/SetParent/Show(FALSE) behavior','Actual normal Login render without overlapping unopened panels'],
        observed_frame=run['captured_frame'],capture=run['capture_result'],fresh_evidence={name:record(WS/f'inventory/client455-{name}.json') for name in names},
        snapshot=record(snapshot),diagnostic_capture=record(WS/'scripts/native/client455_login_capture.inc'),
        tested_full455_stage_factory=False,full455Login_UI=False,auth_character_selection_world_flow=False,
        gaps=ref['gaps']+['Ordinary waiting-state progression through455network responses and all bootstrap tables','Legacy label/partial windows/camera remain;no visual equivalence claim','Full game/client acceptance and all historical gaps'],
        input_exe_executed=False,server_modified=False,full_client=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-login-checkpoint.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('PARTIAL: ordinary Login/lobby frame and root registration verified;Title/auth/selection/world/full455/M9 OPEN')


if __name__=='__main__':
    main()
