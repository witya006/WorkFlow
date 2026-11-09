"""Current selected ordinary material/light chain;full455 acceptance stays open."""
import json
from pathlib import Path
from compare_client_binaries import WS
from audit_client455_item_payloads import record
from audit_client455_own_entry import validated_entry
from checkpoint_client455_rvp_effects import require,check,load,sha
from checkpoint_client455_special_shaders import call_evidence
from client455_normal_link_evidence import validate_normal_link
from probe_client455_material_shaders import verify
from probe_client455_world_frame import verify as verify_world
from prepare_client455_special_shaders import parse_init

def main():
    ref=load('client455-material-shaders-reference');require(ref['script']['sha256']==sha(WS/'scripts/audit_client455_material_shaders.py') and ref['full_assembly']==12 and ref['instructions']==2063 and ref['verified_ranges']==13 and ref['CFG_complete'],'Current complete selected reference')
    for key in ['script','contract_verifier','raw','session','engine','snapshot']:check(ref[key])
    for row in ref['inherited_dispatch_proofs']:check(row['reference']);check(row['raw']);check(row['session'])
    link=load('client455-normal-link');require(validate_normal_link(link)=='PASS','Exact current own client link');lh=sha(WS/'inventory/client455-normal-link.json');require(ref['normal_link_sha256']==lh,'Current reference linked runtime')
    native=load('client455-material-shaders-native');require(native['status']=='PASS_SELECTED' and native['normal_link_sha256']==lh and not native['natural_exit'] and native['driver_script']['sha256']==sha(WS/'scripts/probe_client455_material_shaders.py') and native['native']['warnings']==0,'Successful ordinary material probe')
    for row in [native[k] for k in ['source','included_source','exe','map','console','output','driver_script','trace']]+native['inputs']+native['fixtures']:check(row)
    run=(WS/native['exe']['file']).parent;verdict=verify(run,native);require(verdict==native['verdict'],'Independent exact PS18/PS17 and actual owner checks')
    variant=parse_init((run/'plasma.r3o').read_bytes());require([x['name'] for x in variant['stages']]==['vPlazma.shr','vFraction.shr','pPlazma.shr','pFraction.shr'],'Second actual source pair selected through staged binary list')
    require(parse_init((run/'System/shader/init.r3o').read_bytes())==load('client455-special-shaders-inputs')['init'],'Pinned original shader list restored')
    review=load('client455-material-shaders-visual-review');require(review['reviewed'] and review['reviewed_frames']==4 and review['new_visual_inspection'] and review['native_sha256']==sha(WS/'inventory/client455-material-shaders-native.json'),'Four actual controlled frames inspected');check(review['sheet']);check(review['script'])
    for row in native['frames']:check(row);check(row['preview'])
    world=load('client455-world-frame-native');require(world['normal_link_sha256']==lh and not world['natural_exit'] and world['native']['status']=='PASS','Fresh ordinary effect/light scene');wv=verify_world((WS/world['exe']['file']).parent);require(wv==world['verdict'],'Ordinary76queue/16clock checks');check(world['world_manifest'])
    verification=load('client455-world-frame-verification');require(verification['native_sha256']==sha(WS/'inventory/client455-world-frame-native.json'),'Fresh world verification')
    previous=WS/'artifacts/client455-progress/before135';oldfile=previous/'inventory/client455-world-frame-native.json';reviewfile=previous/'inventory/client455-world-frame-visual-review.json';old=json.loads(oldfile.read_text());oldreview=json.loads(reviewfile.read_text());require(oldreview['reviewed'] and oldreview['reviewed_frames']==5 and oldreview['native_sha256']==sha(oldfile),'Verified prior134 visual review');check(oldreview['sheet']);oldframes={Path(x['file']).name:x for x in old['frames']}
    require(len(world['frames'])==5,'Five fresh ordinary GPU frames')
    for row in world['frames']:
        before=oldframes[Path(row['file']).name]
        for x in [row,row['preview'],before,before['preview']]:check(x)
        require(row['sha256']==before['sha256'] and row['preview']['sha256']==before['preview']['sha256'],'Exact previously reviewed ordinary scene pixels')
    oldreview.update(native_sha256=sha(WS/'inventory/client455-world-frame-native.json'),frames=world['frames'],reused_from_native=record(oldfile),reused_from_review=record(reviewfile),reused_pixels_byte_equal=True,new_visual_inspection=False,script_sha256=sha(Path(__file__)))
    (WS/'inventory/client455-world-frame-visual-review.json').write_text(json.dumps(oldreview,indent=2)+'\n')
    full=load('client455-world-bellato-native');require(full['normal_link_sha256']==lh and not full['natural_exit'] and full['native']['status']=='PASS' and full['native']['actual_land_owner'] and full['native']['reload_and_global_clear'] and full['native']['memory_before']==full['native']['memory_after'] and full['native']['memory_loaded']==full['native']['memory_reloaded'],'Fresh full ordinary Bellato load/render/reload/release')
    visual=load('client455-world-visual');require(visual['manually_reviewed'],'Normal world frames reviewed')
    for row in full['frames']:
        check(row);require(sha(WS/row['preview'])==row['preview_sha256'],'Current Bellato preview');require(any(x['file']==row['file'] and x['native_sha256']==sha(WS/'inventory/client455-world-bellato-native.json') for x in visual['frames']),'Current two Bellato frames inspected')
    engine=load('client455-startup-engine-build');require(engine['library_sha256']==ref['engine']['sha256'],'Current engine object ownership')
    require(validated_entry()['normal_link_sha256']==lh,'Decoded own entry');calls=call_evidence(link);early,ui,audit,contract=load('client455-startup-native'),load('client455-ui-startup-native'),load('client455-startup-audit'),load('client455-startup-contracts-native')
    require(early['normal_link_sha256']==ui['normal_link_sha256']==audit['normal_link_sha256']==lh and early['sound_return']==1 and not early['debugger_exit'] and not ui['debugger_exit'] and ui['completed_existing_client_create'] and any(x['name']=='after_client_create' and x['eax']==1 for x in ui['markers']) and not audit['unresolved_provider_modules'] and contract['build_sha256']==sha(WS/'inventory/client455-startup-engine-build.json'),'Current own sound/window/device/existingCreate1/contracts/providers');check(early['events']);check(ui['events'])
    names=['material-shaders-reference','material-shaders-native','material-shaders-visual-review','normal-link','startup-engine-build','own-entry','startup-audit','startup-native','startup-contracts-native','ui-startup-native','world-frame-native','world-frame-verification','world-frame-visual-review','world-bellato-native','world-visual']
    out=dict(status='PARTIAL',scope=ref['scope'],script=record(Path(__file__)),reference=record(WS/'inventory/client455-material-shaders-reference.json'),normal_executable=link['executable'],normal_link_sha256=lh,engine=ref['engine'],material_shaders=verdict,full_Bellato_scene=full['native'],ordinary_world_effects=wv,loader_restore_calls=calls,shared_headers_changed=False,full_client_recompile_needed=False,newly_inspected_frames=6,reused_review_frames=5,fresh_GPU_frames=11,previous134_gate=record(previous/'inventory/client455-special-shaders-checkpoint.json'),snapshot=ref['snapshot'],fresh_evidence={x:record(WS/f'inventory/client455-{x}.json') for x in names},gaps=ref['gaps'],unchanged_bulk_suites_rerun=False,full_special_renderer=False,full_client=False,input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-material-shaders-checkpoint.json').write_text(json.dumps(out,indent=2)+'\n');print('PARTIAL:ordinary BSP shaders/PS18/7textures/particle light producer/splat/ownCreate1/11freshframes;full455/M9OPEN')
if __name__=='__main__':main()
