"""Current selected resource checkpoint;no complete refraction or game acceptance."""
import json
from pathlib import Path
from audit_client455_item_payloads import record
from audit_client455_own_entry import validated_entry
from checkpoint_client455_rvp_effects import require,check,load,sha
from client455_normal_link_evidence import validate_normal_link
from compare_client_binaries import WS

def main():
    ref=load('client455-scene-capture-reference');require(ref['script']['sha256']==sha(WS/'scripts/audit_client455_scene_capture.py') and ref['selected_full_functions']==12 and ref['CFG_complete'],'Current complete selected reference')
    for key in ['script','raw','session','engine','snapshot']:check(ref[key])
    link=load('client455-normal-link');lh=sha(WS/'inventory/client455-normal-link.json');require(validate_normal_link(link)=='PASS' and ref['normal_link_sha256']==lh,'Exact ordinary own client link')
    native=load('client455-fullscreen-effect-native');require(native['normal_link_sha256']==lh and native['engine_report_sha256']==sha(WS/'inventory/client455-startup-engine-build.json') and not native['natural_exit'] and native['source_sha256']==sha(WS/native['source']) and native['script_sha256']==sha(WS/'scripts/probe_client455_fullscreen_effect.py'),'Current successful actual resource run')
    for key in ['exe','map','console','output']:check(native[key])
    for row in native['inputs']:check(row)
    n=native['native'];require(n['status']=='PASS' and n['GPU_frames']==18 and n['resource_configurations']==8 and n['capture_cases']==2 and n['targets']==5 and n['resize_cases']==3 and not n['warnings'],'Fiveactual targets/eightconfigurations/twocaptures/eighteen prior effect frames')
    for key in ['perturbation_load_release','missing_perturbation_supported','framebuffer_copy_exact','active_target_selection','framebuffer_depth_viewport_UI_restored','capture_surface_references_balanced']:require(n.get(key),key)
    review=load('client455-fullscreen-effect-visual');require(review['manually_reviewed'] and review['native_sha256']==sha(WS/'inventory/client455-fullscreen-effect-native.json') and len(native['frames'])==5,'Five fresh GPU views inspected');check(review['sheet'])
    for row in native['frames']:check(row);require(sha(WS/row['preview'])==row['preview_sha256'],'Current GPU PNG')
    early,ui,contracts,audit=load('client455-startup-native'),load('client455-ui-startup-native'),load('client455-startup-contracts-native'),load('client455-startup-audit')
    require(early['normal_link_sha256']==ui['normal_link_sha256']==audit['normal_link_sha256']==lh and early['sound_return']==1 and not early['debugger_exit'] and not ui['debugger_exit'] and ui['completed_existing_client_create'] and not audit['unresolved_provider_modules'] and contracts['build_sha256']==sha(WS/'inventory/client455-startup-engine-build.json') and validated_entry()['normal_link_sha256']==lh,'Fresh own sound/window/device/existing Create1/contracts/providers')
    for report,driver in [(native,'probe_client455_fullscreen_effect.py'),(early,'probe_client455_startup.py'),(ui,'probe_client455_device_startup.py')]:
        require(report['script_sha256']==sha(WS/'scripts'/driver) and report['asset_staging_script_sha256']==sha(WS/'scripts/client455_asset_staging.py'),'Current shared staging driver')
        require(report['shared_asset_staging']['assets']>0,'Actually used shared input staging')
    check(early['events']);check(ui['events']);staging=load('client455-asset-staging-native');require(staging['status']=='PASS' and staging['staging_script_sha256']==sha(WS/'scripts/client455_asset_staging.py') and staging['verifier_sha256']==sha(WS/'scripts/probe_client455_asset_staging.py'),'Current file identities/original isolation/mutable config boundaries')
    names=['scene-capture-reference','fullscreen-effect-native','fullscreen-effect-visual','normal-link','startup-engine-build','own-entry','startup-audit','startup-native','startup-contracts-native','ui-startup-native','asset-staging-native']
    out=dict(status='PARTIAL',scope=ref['scope'],script=record(Path(__file__)),normal_executable=link['executable'],engine=ref['engine'],normal_link_sha256=lh,resource_targets=5,resource_configurations=8,capture_cases=2,fresh_fullscreen_frames=18,inspected_GPU_frames=5,full_normal_recompile_needed=False,shared_headers_changed=False,
        shared_asset_staging={k:r['shared_asset_staging'] for k,r in [('startup',early),('existingCreate',ui),('fullscreen',native)]},
        fresh_evidence={x:record(WS/f'inventory/client455-{x}.json') for x in names},snapshot=ref['snapshot'],gaps=ref['gaps'],full_refraction_renderer=False,ordinary_Title_Login_accepted=False,full_client=False,input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-scene-capture-checkpoint.json').write_text(json.dumps(out,indent=2)+'\n');print('PARTIAL:five scene resources/actual capture/fresh existingCreate1/sharedstaging;Title/Login/fullgame/M9 OPEN')

if __name__=='__main__':main()
