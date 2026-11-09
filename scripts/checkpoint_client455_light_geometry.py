"""Current partialM6 checkpoint for selected BSP geometry and real world light."""
import json
from pathlib import Path
from audit_client455_item_payloads import record
from checkpoint_client455_rvp_effects import check,load,require,sha
from client455_normal_link_evidence import validate_normal_link
from compare_client_binaries import WS
from probe_client455_light_geometry import verify as verify_geometry
from probe_client455_world_frame import verify as verify_world


def main():
    ref=load('client455-light-geometry-reference');require(ref['status']=='CONFIRMED_SELECTED' and ref['script_sha256']==sha(WS/'scripts/audit_client455_light_geometry.py') and ref['full_assembly']==12 and ref['instructions']==1725 and ref['new_instructions']==712,'Selected geometry reference')
    for row in [ref['raw'],ref['session'],ref['cached_raw'],ref['cached_reference'],ref['engine'],ref['old_engine'],ref['header_overlay']]+ref['sources']:check(row)
    link=load('client455-normal-link');require(validate_normal_link(link)=='PASS','Current ordinary client link');lh=sha(WS/'inventory/client455-normal-link.json');engine=load('client455-startup-engine-build');require(engine['library_sha256']==ref['engine']['sha256'] and any(x['file']==engine['library'] and x['sha256']==engine['library_sha256'] for x in link['libraries']),'New engine retained by normal PE')
    mapping=(WS/link['map']['file']).read_text(errors='replace')
    for name in ['DrawDynamicLightSub@CBsp','DrawMagicLightSub@CBsp','RF455_CreateBspLightDeclaration','RF455_ReleaseBspLightDeclaration']:require(name in mapping,'Own PE retains restored light:'+name)
    geometry=load('client455-light-geometry-native');require(geometry['status']=='PASS_SELECTED' and geometry['natural_exit']==0 and geometry['normal_link_sha256']==lh and geometry['engine_report_sha256']==sha(WS/'inventory/client455-startup-engine-build.json') and geometry['script_sha256']==sha(WS/'scripts/probe_client455_light_geometry.py'),'Current finite geometry capture')
    for row in [geometry['source'],geometry['included_source'],geometry['oracle'],geometry['exe'],geometry['map'],geometry['trace'],geometry['vertices'],geometry['console'],geometry['output']]+geometry['inputs']:check(row)
    verdict=verify_geometry((WS/geometry['exe']['file']).parent);require(verdict==geometry['verdict'] and verdict['cases']==33 and verdict['emitted_bytes']==1580880,'All actual draw bytes and boundaries reproduced')
    world=load('client455-world-frame-native');validation=load('client455-world-frame-verification');require(world['status']=='PASS' and world['normal_link_sha256']==lh and validation['status']=='PASS_SELECTED' and validation['native_sha256']==sha(WS/'inventory/client455-world-frame-native.json') and validation['script_sha256']==sha(WS/'scripts/verify_client455_world_frame.py'),'New actual world scenario')
    for row in [world['source'],world['included_source'],world['driver_script'],world['oracle'],world['exe'],world['map'],world['console'],world['output'],world['world_manifest'],validation['diagnostic'],validation['texture'],validation['texture_preview']]+world['trace']+world['inputs']:check(row)
    require(world['driver_script']['sha256']==sha(WS/'scripts/probe_client455_world_frame.py') and world['script_sha256']==sha(WS/'scripts/probe_client455_nuclear_registry.py'),'World driver unchanged')
    world_verdict=verify_world((WS/world['exe']['file']).parent);require(world_verdict==world['verdict']==validation['verdict'] and world_verdict['queue_operations']==76 and world_verdict['live_clock_samples']==16,'Actual queue/clock reproduction')
    require(world_verdict['changed_bytes_from_matched_clear']['frame-base.bgra']==world_verdict['changed_bytes_from_matched_clear']['frame-cleared.bgra']==0,'Exact matched clear control')
    require((WS/world['console']['file']).read_text(errors='replace').count('light-state bind=00000000 validate=00000000 passes=1 cull=3 zfunc=4')==3,'All three real light passes validate')
    review=load('client455-world-frame-visual-review');require(review['reviewed'] and review['reviewed_frames']==5 and review['native_sha256']==sha(WS/'inventory/client455-world-frame-native.json'),'Five new GPU frames viewed');check(review['sheet'])
    oldworld=json.loads((WS/'artifacts/client455-progress/client455-world-frame-native-before121.json').read_text());previous={Path(x['file']).name:x for x in oldworld['frames']};exact=[]
    for row in review['frames']:
        check(row);check(row['preview']);old=previous[Path(row['file']).name];check(old);require(old['sha256']==row['sha256'],'Selected identity-world GPU output preserved');exact.append(Path(row['file']).name)
    maps=load('client455-map-data-native');require(maps['normal_link_sha256']==lh and maps['native']['checks']==2692 and maps['native']['geometry_cases']==330 and maps['canonical_equal'] and not maps['natural_exit'],'Map geometry regression');check(maps['output']);check(maps['canonical_actual'])
    consumers=load('client455-normal-consumers');require(consumers['normal_build_sha256']==sha(WS/'inventory/client455-normal-build.json') and consumers['native']['status']=='PASS' and consumers['native']['real_ani_loaded']==2 and consumers['native']['real_bbx_loaded'],'Fresh normal ANI/BBX consumers')
    early,ui,contracts=load('client455-startup-native'),load('client455-ui-startup-native'),load('client455-startup-contracts-native');require(contracts['build_sha256']==sha(WS/'inventory/client455-startup-engine-build.json') and early['normal_link_sha256']==ui['normal_link_sha256']==lh and not early['debugger_exit'] and early['sound_return']==1 and not ui['debugger_exit'] and ui['completed_existing_client_create'] and any(x['name']=='after_client_create' and x['eax']==1 for x in ui['markers']) and all(x['first_chance']==1 for x in ui['exceptions']),'Exact own PE startup/window/device/Create1');check(early['events']);check(ui['events'])
    old=WS/'artifacts/client455-progress/client455-world-frame-checkpoint-before121.json';require(old.exists(),'Exact120 checkpoint preserved')
    fresh=['light-geometry-reference','light-geometry-native','world-frame-native','world-frame-verification','world-frame-visual-review','startup-engine-build','normal-preparation','normal-build','normal-link','normal-consumers','own-entry','startup-audit','startup-native','startup-contracts-native','ui-startup-native','map-data-native']
    result=dict(status='PARTIAL',scope=ref['scope'],script_sha256=sha(Path(__file__)),normal_executable=link['executable'],normal_link_sha256=lh,engine=ref['engine'],old_engine=ref['old_engine'],geometry=verdict,world=world_verdict,viewed_GPU_frames=5,identity_world_frames_byte_equal120=exact,previous120_gate=record(old),fresh_evidence={x:record(WS/f'inventory/client455-{x}.json') for x in fresh},selected_geometry_differences_restored=True,placed_transform_game_owners_restored=False,full_world=False,full_renderer=False,gaps=ref['gaps'],old_runtime_gates='HISTORICAL;120camera correction retained;CPUquake/explosion/texture/receiver/Character/bulk not rerun',unchanged_bulk_suites_rerun=False,input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-light-geometry-checkpoint.json').write_text(json.dumps(result,indent=2)+'\n');print('PARTIAL:33geometry fixtures/all1580880vertexbytes/owned matrices+declaration;Bellato76queue/16clock/5viewedGPU byteequal120/maps2692/Create1;fullrenderer+M9OPEN')


if __name__=='__main__':main()
