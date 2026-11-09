"""Current partialM6 gate: exact selected fade state/math and real sky pixels."""
import json
from pathlib import Path
from audit_client455_item_payloads import record
from checkpoint_client455_rvp_effects import load,check,require,sha
from client455_normal_link_evidence import validate_normal_link
from compare_client_binaries import WS
from probe_client455_sky_fade import verify as verify_fade
from probe_client455_world_frame import verify as verify_world


def main():
    ref=load('client455-sky-fade-reference');require(ref['status']=='CONFIRMED_SELECTED' and ref['full_assembly']==4 and ref['instructions']==282 and ref['script_sha256']==sha(WS/'scripts/audit_client455_sky_fade.py'),'Current reference proof')
    for row in [ref[x] for x in ['raw','session','engine','old_engine']]+ref['sources']:check(row)
    link=load('client455-normal-link');require(validate_normal_link(link)=='PASS','Current exact normal link');lh=sha(WS/'inventory/client455-normal-link.json');engine=load('client455-startup-engine-build');require(engine['library_sha256']==ref['engine']['sha256'] and any(x['file']==engine['library'] and x['sha256']==ref['engine']['sha256'] for x in link['libraries']),'Updated engine retained');mapping=(WS/link['map']['file']).read_text(errors='replace')
    require(all(x in mapping for x in ['DrawSkyBoxRender@CLevel','DrawFadeSKy','GetColorToColorAlpha','SetFadeFactor']),'Ordinary PE retains actual fade path')
    native=load('client455-sky-fade-native');require(native['status']=='PASS_SELECTED' and not native['natural_exit'] and native['normal_link_sha256']==lh and native['driver_script']['sha256']==sha(WS/'scripts/probe_client455_sky_fade.py') and not native['native']['warnings'],'Actual current engine fade run')
    for row in [native[x] for x in ['source','included_source','driver_script','exe','map','trace','console','output']]+native['inputs']:check(row)
    verdict=verify_fade((WS/native['exe']['file']).parent);require(verdict==native['verdict'] and verdict['frame_cases']==90 and verdict['shared_helper_cases']==27 and verdict['legacy_SSE_fog_differences']==8,'Independent rational oracle reproduced');review=load('client455-sky-fade-visual-review');require(review['reviewed'] and review['reviewed_frames']==5 and review['native_sha256']==sha(WS/'inventory/client455-sky-fade-native.json'),'Five actual sky fade frames reviewed');check(review['sheet'])
    for row in review['frames']:check(row);check(row['preview'])
    world=load('client455-world-frame-native');wr=load('client455-world-frame-visual-review');wv=load('client455-world-frame-verification');require(world['status']=='PASS' and world['normal_link_sha256']==lh and wr['reviewed'] and wr['reviewed_frames']==5 and wr['native_sha256']==wv['native_sha256']==sha(WS/'inventory/client455-world-frame-native.json'),'Actual current world regression')
    for row in [world[x] for x in ['source','included_source','driver_script','oracle','exe','map','console','output','world_manifest']]+world['trace']+world['inputs']+[wv[x] for x in ['diagnostic','texture','texture_preview']]:check(row)
    require(verify_world((WS/world['exe']['file']).parent)==world['verdict']==wv['verdict'],'Reproduced actual world oracle');oldworld=json.loads((WS/'artifacts/client455-progress/client455-world-frame-native-before124.json').read_text());oldframes={Path(x['file']).name:x for x in oldworld['frames']};equal=[];check(wr['sheet'])
    for row in wr['frames']:
        check(row);check(row['preview']);old=oldframes[Path(row['file']).name];check(old);require(row['sha256']==old['sha256'],'Matched world pixels preserved123');equal.append(Path(row['file']).name)
    consumers=load('client455-normal-consumers');require(consumers['native']['status']=='PASS' and consumers['normal_build_sha256']==link['normal_build_sha256'],'Actual ANI/BBX consumer smoke')
    for row in consumers['libraries']+consumers['objects']:check(row)
    early,ui,contracts=load('client455-startup-native'),load('client455-ui-startup-native'),load('client455-startup-contracts-native');require(early['normal_link_sha256']==ui['normal_link_sha256']==lh and not early['debugger_exit'] and early['sound_return']==1 and not ui['debugger_exit'] and ui['completed_existing_client_create'] and any(x['name']=='after_client_create' and x['eax']==1 for x in ui['markers']) and contracts['build_sha256']==sha(WS/'inventory/client455-startup-engine-build.json'),'Current ownPE startup/window/device/Create1');check(early['events']);check(ui['events'])
    previous=WS/'artifacts/client455-progress/client455-sky-projection-checkpoint-before124.json';require(previous.exists(),'Historical123gate preserved');fresh=['sky-fade-reference','sky-fade-native','sky-fade-visual-review','world-frame-native','world-frame-verification','world-frame-visual-review','startup-engine-build','normal-consumers','normal-link','own-entry','startup-audit','startup-native','startup-contracts-native','ui-startup-native'];out=dict(status='PARTIAL',scope=ref['scope'],script_sha256=sha(Path(__file__)),normal_executable=link['executable'],normal_link_sha256=lh,engine=ref['engine'],old_engine=ref['old_engine'],fade=verdict,world=world['verdict'],world_frames_byte_equal123=equal,viewed_GPU_frames=10,previous123_gate=record(previous),fresh_evidence={x:record(WS/f'inventory/client455-{x}.json') for x in fresh},full_sky_renderer=False,full_atmosphere=False,full_fade=False,full_world=False,gaps=ref['gaps'],historical_suites='Map2692/projection12/loadedsky123/BSPleaf140/geometry33/quake/texture/Character/bulk historical,not rerun without new cause',unchanged_bulk_suites_rerun=False,input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN');(WS/'inventory/client455-sky-fade-checkpoint.json').write_text(json.dumps(out,indent=2)+'\n');print('PARTIAL:90fade frames+27shared helper cases/3FPprecision/exactfog+quad/5skyGPU+5worldGPUviewed/Create1;fullsky+M9OPEN')


if __name__=='__main__':main()
