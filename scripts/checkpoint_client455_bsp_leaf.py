"""Current partialM6 evidence for inverse-affine leaf lookup and its real callers."""
import json
from pathlib import Path
from audit_client455_item_payloads import record
from checkpoint_client455_rvp_effects import check,load,require,sha
from client455_normal_link_evidence import validate_normal_link
from compare_client_binaries import WS
from probe_client455_bsp_leaf import verify as verify_leaf
from probe_client455_world_frame import verify as verify_world


def main():
    ref=load('client455-bsp-leaf-reference');require(ref['status']=='CONFIRMED_SELECTED' and ref['script_sha256']==sha(WS/'scripts/audit_client455_bsp_leaf.py') and ref['full_assembly']==13 and ref['instructions']==971 and ref['shared_headers_unchanged'],'Current affine/owner proof')
    for row in [ref['raw'],ref['session'],ref['cached_raw'],ref['source'],ref['engine'],ref['old_engine']]:check(row)
    link=load('client455-normal-link');require(validate_normal_link(link)=='PASS','Normal client link');lh=sha(WS/'inventory/client455-normal-link.json');engine=load('client455-startup-engine-build');require(engine['library_sha256']==ref['engine']['sha256'] and any(x['file']==engine['library'] and x['sha256']==ref['engine']['sha256'] for x in link['libraries']),'Restored engine in ordinary PE');require('GetLeafNum@CBsp' in (WS/link['map']['file']).read_text(errors='replace'),'Actual ordinary GetLeafNum retained')
    native=load('client455-bsp-leaf-native');require(native['status']=='PASS_SELECTED' and not native['natural_exit'] and native['normal_link_sha256']==lh and native['engine_report_sha256']==sha(WS/'inventory/client455-startup-engine-build.json') and native['script_sha256']==sha(WS/'scripts/probe_client455_bsp_leaf.py'),'Current actual query probe')
    for row in [native[x] for x in ['source','included_source','oracle','exe','map','fixture','trace','console']]:check(row)
    verdict=verify_leaf((WS/native['exe']['file']).parent);require(verdict==native['verdict'] and verdict['cases']==140,'Reproduce finite queries/bytes/leaf0 quirk')
    world=load('client455-world-frame-native');validation=load('client455-world-frame-verification');review=load('client455-world-frame-visual-review');require(world['status']=='PASS' and world['normal_link_sha256']==lh and validation['native_sha256']==review['native_sha256']==sha(WS/'inventory/client455-world-frame-native.json') and validation['status']=='PASS_SELECTED' and review['reviewed'] and review['reviewed_frames']==5,'New world runtime/visual evidence')
    for row in [world[x] for x in ['source','included_source','driver_script','oracle','exe','map','console','output','world_manifest']]+world['trace']+world['inputs']+[validation[x] for x in ['diagnostic','texture','texture_preview']]:check(row)
    require(world['driver_script']['sha256']==sha(WS/'scripts/probe_client455_world_frame.py') and world['script_sha256']==sha(WS/'scripts/probe_client455_nuclear_registry.py'),'Exact world producers');require(verify_world((WS/world['exe']['file']).parent)==world['verdict']==validation['verdict'],'World queue/clock/light reproduced');check(review['sheet'])
    before=json.loads((WS/'artifacts/client455-progress/client455-world-frame-native-before122.json').read_text());previous={Path(x['file']).name:x for x in before['frames']};same=[]
    for row in review['frames']:
        check(row);check(row['preview']);old=previous[Path(row['file']).name];check(old);require(row['sha256']==old['sha256'],'Actual ordinary identity-world GPU frame preserved');same.append(Path(row['file']).name)
    require(world['native']['warnings']==6 and (WS/world['console']['file']).read_text(errors='replace').count('light-state bind=00000000 validate=00000000 passes=1 cull=3 zfunc=4')==3,'Actual light passes/known warnings retained')
    maps=load('client455-map-data-native');require(maps['normal_link_sha256']==lh and maps['native']['checks']==2692 and maps['native']['geometry_cases']==330 and maps['canonical_equal'] and not maps['natural_exit'],'Actual map regression');check(maps['output']);check(maps['canonical_actual'])
    early,ui,contracts=load('client455-startup-native'),load('client455-ui-startup-native'),load('client455-startup-contracts-native');require(contracts['build_sha256']==sha(WS/'inventory/client455-startup-engine-build.json') and early['normal_link_sha256']==ui['normal_link_sha256']==lh and not early['debugger_exit'] and early['sound_return']==1 and not ui['debugger_exit'] and ui['completed_existing_client_create'] and any(x['name']=='after_client_create' and x['eax']==1 for x in ui['markers']) and all(x['first_chance']==1 for x in ui['exceptions']),'Exact new PE startup/window/device/Create1');check(early['events']);check(ui['events'])
    beforebuild=WS/'artifacts/client455-progress/client455-normal-build-before122.json';require(sha(beforebuild)==sha(WS/'inventory/client455-normal-build.json'),'Normal182client/20kernel build unchanged;shared declarations unchanged')
    old=WS/'artifacts/client455-progress/client455-light-geometry-checkpoint-before122.json';require(old.exists(),'Historical121 checkpoint preserved')
    fresh=['bsp-leaf-reference','bsp-leaf-native','world-frame-native','world-frame-verification','world-frame-visual-review','startup-engine-build','normal-link','own-entry','startup-audit','startup-native','startup-contracts-native','ui-startup-native','map-data-native']
    out=dict(status='PARTIAL',scope=ref['scope'],script_sha256=sha(Path(__file__)),normal_executable=link['executable'],normal_link_sha256=lh,engine=ref['engine'],old_engine=ref['old_engine'],leaf=verdict,world=world['verdict'],viewed_GPU_frames=5,identity_world_frames_byte_equal121=same,previous121_gate=record(old),fresh_evidence={x:record(WS/f'inventory/client455-{x}.json') for x in fresh},normal_client_build_unchanged=True,ordinary_placed_transform_owners_restored=False,full_world=False,full_renderer=False,gaps=ref['gaps'],historical_suites='Lightgeometry33/ANI-BBX/quake/explosion/texture/Character/receiver/bulk historical,not rerun',unchanged_bulk_suites_rerun=False,input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-bsp-leaf-checkpoint.json').write_text(json.dumps(out,indent=2)+'\n');print('PARTIAL:140inverse-affine leaf queries/1680exact local bytes/leaf0fallback;13asm971/real Bellato5GPU byteequal121/maps2692/Create1;fullrenderer+M9OPEN')


if __name__=='__main__':main()
