"""Current partialM6 gate for ordinary sky2/day/material reconstruction."""
import json
from pathlib import Path
from audit_client455_item_payloads import record
from checkpoint_client455_rvp_effects import load,check,require,sha
from client455_normal_link_evidence import validate_normal_link
from compare_client_binaries import WS
from probe_client455_sky_material import verify as verify_material
from probe_client455_sky_fade import verify as verify_fade
from probe_client455_world_frame import verify as verify_world


def reviewed(prefix,count):
    native=load(prefix+'-native');review=load(prefix+'-visual-review');require(review['reviewed'] and review['reviewed_frames']==count and review['native_sha256']==sha(WS/f'inventory/{prefix}-native.json'),'Current visual review '+prefix);check(review['sheet'])
    for row in review['frames']:check(row);check(row['preview'])
    return native


def unchanged_frames(native,oldname):
    old=json.loads((WS/f'artifacts/client455-progress/{oldname}-before125.json').read_text());byname={Path(x['file']).name:x for x in old['frames']};same=[]
    for row in native['frames']:
        before=byname[Path(row['file']).name];check(before);require(row['sha256']==before['sha256'],'Previous124 pixels preserved');same.append(Path(row['file']).name)
    return same


def main():
    ref=load('client455-sky-material-reference');require(ref['status']=='CONFIRMED_SELECTED' and ref['full_assembly']==8 and ref['instructions']==1696 and ref['headers_unchanged'] and ref['script_sha256']==sha(WS/'scripts/audit_client455_sky_material.py'),'Current reference/source proof')
    for row in [ref[x] for x in ['raw','session','engine','old_engine']]+ref['sources']:check(row)
    link=load('client455-normal-link');require(validate_normal_link(link)=='PASS','Exact normal link');lh=sha(WS/'inventory/client455-normal-link.json');engine=load('client455-startup-engine-build');require(engine['library_sha256']==ref['engine']['sha256'] and any(x['file']==engine['library'] and x['sha256']==ref['engine']['sha256'] for x in link['libraries']),'Current engine retained');mapping=(WS/link['map']['file']).read_text(errors='replace');require(all(x in mapping for x in ['DrawSkyBoxRender@CLevel','DrawSkyBox@CSkyBox','RF455_UpdateSkyNightWeight','RF455_GetSkyNightWeight','RF455_SetSkyDayEnabled']),'Ordinary PE retains new map/frame/material methods')
    material=reviewed('client455-sky-material',5);require(material['status']=='PASS_SELECTED' and not material['natural_exit'] and material['normal_link_sha256']==lh and material['native']['actual_neutralB_sky2'] and material['native']['Bellato_fallback'] and material['driver_script']['sha256']==sha(WS/'scripts/probe_client455_sky_material.py'),'Current real material run')
    for row in [material[x] for x in ['source','included_source','driver_script','oracle','trace','exe','map','console','output']]+material['inputs']:check(row)
    mv=verify_material((WS/material['exe']['file']).parent);require(mv==material['verdict'] and mv['profile_cases']==60 and mv['material_cases']==36 and mv['direct_unloaded_state'],'Reproduced independent profile/submission/unloaded oracle')
    missing=Path(json.loads((WS/'config/paths.json').read_text())['client_455'])/'Map/Entity/e_neutrala/trade_bel/trade_bel.r3e';require(not missing.exists() and material['native']['warnings']==1,'Known missing original resource warning,not substituted')
    world=reviewed('client455-world-frame',5);validation=load('client455-world-frame-verification');require(world['status']=='PASS' and world['normal_link_sha256']==lh and validation['native_sha256']==sha(WS/'inventory/client455-world-frame-native.json'),'Current actual world regression');require(verify_world((WS/world['exe']['file']).parent)==world['verdict']==validation['verdict'],'Actual world oracle');sameworld=unchanged_frames(world,'client455-world-frame-native')
    fade=reviewed('client455-sky-fade',5);require(fade['status']=='PASS_SELECTED' and not fade['natural_exit'] and fade['normal_link_sha256']==lh and not fade['native']['warnings'],'Current fade regression');require(verify_fade((WS/fade['exe']['file']).parent)==fade['verdict'],'Actual fade oracle');samefade=unchanged_frames(fade,'client455-sky-fade-native')
    consumers=load('client455-normal-consumers');require(consumers['native']['status']=='PASS' and consumers['normal_build_sha256']==link['normal_build_sha256'],'Actual ANI/BBX smoke')
    for row in consumers['libraries']+consumers['objects']:check(row)
    early,ui,contracts=load('client455-startup-native'),load('client455-ui-startup-native'),load('client455-startup-contracts-native');require(early['normal_link_sha256']==ui['normal_link_sha256']==lh and not early['debugger_exit'] and early['sound_return']==1 and not ui['debugger_exit'] and ui['completed_existing_client_create'] and any(x['name']=='after_client_create' and x['eax']==1 for x in ui['markers']) and contracts['build_sha256']==sha(WS/'inventory/client455-startup-engine-build.json'),'Current exact PE startup/device/Create1');check(early['events']);check(ui['events'])
    previous=WS/'artifacts/client455-progress/client455-sky-fade-checkpoint-before125.json';require(previous.exists(),'Historical124 gate preserved');fresh=['sky-material-reference','sky-material-inputs','sky-material-native','sky-material-visual-review','sky-fade-native','sky-fade-visual-review','world-frame-native','world-frame-verification','world-frame-visual-review','startup-engine-build','normal-consumers','normal-link','own-entry','startup-audit','startup-native','startup-contracts-native','ui-startup-native'];out=dict(status='PARTIAL',scope=ref['scope'],script_sha256=sha(Path(__file__)),normal_executable=link['executable'],normal_link_sha256=lh,engine=ref['engine'],old_engine=ref['old_engine'],material=mv,fade=fade['verdict'],world=world['verdict'],world_frames_byte_equal124=sameworld,fade_frames_byte_equal124=samefade,viewed_GPU_frames=15,previous124_gate=record(previous),fresh_evidence={x:record(WS/f'inventory/client455-{x}.json') for x in fresh},full_sky_renderer=False,full_atmosphere=False,full_world=False,gaps=ref['gaps'],historical_suites='Map2692/projection12/otherunchangedBSP/Character/bulk historical,not rerun',unchanged_bulk_suites_rerun=False,input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN');(WS/'inventory/client455-sky-material-checkpoint.json').write_text(json.dumps(out,indent=2)+'\n');print('PARTIAL:60profile/3frame/36material/unloaded/5sky2GPU+5fade+5worldviewed/oldpixelsstable/Create1;fullatmosphere+M9OPEN')


if __name__=='__main__':main()
