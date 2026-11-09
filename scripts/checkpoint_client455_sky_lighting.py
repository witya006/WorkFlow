"""Current partialM6 gate for ordinary lighting and both fog branches."""
import json
from pathlib import Path
from audit_client455_item_payloads import record
from checkpoint_client455_rvp_effects import check,load,require,sha
from checkpoint_client455_sky_material import reviewed
from client455_normal_link_evidence import validate_normal_link
from compare_client_binaries import WS
from probe_client455_sky_lighting import verify as verify_lighting
from probe_client455_sky_material import verify as verify_material
from probe_client455_sky_fade import verify as verify_fade
from probe_client455_world_frame import verify as verify_world


def previous_pixels(native,name):
    old=json.loads((WS/f'artifacts/client455-progress/{name}-before128.json').read_text())
    before={Path(x['file']).name:x for x in old['frames']};result=[]
    for row in native['frames']:
        previous=before[Path(row['file']).name];check(previous)
        require(row['sha256']==previous['sha256'],'Previous126 regression frame retained')
        result.append(Path(row['file']).name)
    return result


def provenance(native,lh):
    require(native['normal_link_sha256']==lh and not native['natural_exit'] and native['inputs_unchanged']
            and native['builder_sha256']==sha(WS/'scripts/client455_own_probe.py')
            and native['script_sha256']==sha(WS/'scripts/probe_client455_nuclear_registry.py')
            and native['runtime_inputs_sha256']==sha(WS/'scripts/client455_runtime_inputs.py'),'Current normal libraries/lab/resources')
    for key in ['source','included_source','driver_script','exe','map','console','output']:check(native[key])
    for row in native['inputs']:check(row)


def main():
    ref=load('client455-sky-lighting-runtime-reference')
    require(ref['status']=='CONFIRMED_SELECTED' and ref['full_assembly']==17 and ref['instructions']==1538
            and ref['headers_unchanged'] and len(ref['payload_changed_members'])==3 and len(ref['unchanged_members'])==63
            and ref['script_sha256']==sha(WS/'scripts/audit_client455_sky_lighting_runtime.py'),'Current128 source/reference proof')
    for row in [ref[x] for x in ['reference127','raw','session','engine','old_engine']]+ref['sources']:check(row)
    link=load('client455-normal-link');require(validate_normal_link(link)=='PASS','Exact normal link')
    lh=sha(WS/'inventory/client455-normal-link.json');engine=load('client455-startup-engine-build')
    require(engine['library_sha256']==ref['engine']['sha256'] and any(x['file']==engine['library'] and x['sha256']==ref['engine']['sha256'] for x in link['libraries']),'Current engine actually retained')
    lighting=reviewed('client455-sky-lighting',5);provenance(lighting,lh)
    check(lighting['trace']);check(lighting['world_source'])
    lv=verify_lighting((WS/lighting['exe']['file']).parent,lighting)
    require(lighting['status']=='PASS_SELECTED' and lv==lighting['verdict']
            and lv['software_samples']==867 and lv['additional_fog_frames']==3
            and lv['mie_cases']==27 and lv['software_precision_bits']==[24]
            and lighting['native']['warnings']==2,'Actual ordinary frame/loaders/selected software math/GPU')
    assets=load('client455-sky-lighting-inputs')
    for row in assets['inputs']:check(row)
    require(any(x['file'].endswith('/Map/neutralB/neutralB.cam') and x['sha256']=='4d71c20bdab6507a03904bc77c3d9cac16d062e666c923f71d7370b3030f6044' for x in assets['inputs']),'Pinned actual neutralB camera')
    missing=Path(json.loads((WS/'config/paths.json').read_text())['client_455'])/'Map/Entity/e_neutrala/trade_bel/trade_bel.r3e'
    require(not missing.exists(),'Known missing original resource not replaced')
    world=reviewed('client455-world-frame',5);provenance(world,lh)
    validation=load('client455-world-frame-verification')
    require(world['status']=='PASS' and validation['native_sha256']==sha(WS/'inventory/client455-world-frame-native.json')
            and verify_world((WS/world['exe']['file']).parent)==world['verdict']==validation['verdict'],'Actual world/FX/light regression')
    fade=reviewed('client455-sky-fade',5);provenance(fade,lh)
    require(fade['status']=='PASS_SELECTED' and not fade['native']['warnings']
            and verify_fade((WS/fade['exe']['file']).parent)==fade['verdict'],'Actual fade regression')
    material=reviewed('client455-sky-material',5);provenance(material,lh)
    require(material['status']=='PASS_SELECTED' and verify_material((WS/material['exe']['file']).parent)==material['verdict']
            and material['verdict']['material_cases']==36 and material['native']['warnings']==1,'Actual material/night/unloaded regression')
    same_world=previous_pixels(world,'client455-world-frame-native')
    same_fade=previous_pixels(fade,'client455-sky-fade-native')
    same_material=previous_pixels(material,'client455-sky-material-native')
    consumers=load('client455-normal-consumers');require(consumers['native']['status']=='PASS'
            and consumers['normal_build_sha256']==link['normal_build_sha256'],'Current ANI/BBX consumers')
    for row in consumers['libraries']+consumers['objects']:check(row)
    early,ui,contracts=load('client455-startup-native'),load('client455-ui-startup-native'),load('client455-startup-contracts-native')
    require(early['normal_link_sha256']==ui['normal_link_sha256']==lh and not early['debugger_exit'] and early['sound_return']==1
            and not ui['debugger_exit'] and ui['completed_existing_client_create']
            and any(x['name']=='after_client_create' and x['eax']==1 for x in ui['markers'])
            and contracts['build_sha256']==sha(WS/'inventory/client455-startup-engine-build.json'),'Current exact PE sound/window/device/existingCreate1/contracts')
    check(early['events']);check(ui['events'])
    audit=load('client455-startup-audit')
    require(audit['normal_link_sha256']==lh and not audit['unresolved_provider_modules'],'Current startup dependency audit')
    previous=WS/'artifacts/client455-progress/client455-sky-atmosphere-checkpoint-before128.json'
    old_gate=json.loads(previous.read_text());old_link=WS/'artifacts/client455-progress/client455-normal-link-before128.json'
    require(old_gate['status']=='PARTIAL' and old_gate['engine']['sha256']==ref['old_engine']['sha256']
            and old_gate['normal_executable']['sha256']==sha(WS/'artifacts/client455-progress/normal-before128.bin')
            and old_gate['fresh_evidence']['normal-link']['sha256']==sha(old_link),'Exact previous126 gate/engine/PE/link backup')
    fresh=['sky-lighting-runtime-reference','sky-lighting-inputs','sky-lighting-native','sky-lighting-visual-review',
           'sky-material-native','sky-material-visual-review','sky-fade-native','sky-fade-visual-review',
           'world-frame-native','world-frame-verification','world-frame-visual-review','startup-engine-build',
           'normal-consumers','normal-link','own-entry','startup-audit','startup-native','startup-contracts-native','ui-startup-native']
    out=dict(status='PARTIAL',scope=ref['scope'],script_sha256=sha(Path(__file__)),normal_executable=link['executable'],normal_link_sha256=lh,
             engine=ref['engine'],old_engine=ref['old_engine'],lighting=lv,material=material['verdict'],fade=fade['verdict'],world=world['verdict'],
             world_frames_byte_equal126=same_world,fade_frames_byte_equal126=same_fade,material_frames_byte_equal126=same_material,
             viewed_GPU_frames=20,previous126_gate=record(previous),fresh_evidence={x:record(WS/f'inventory/client455-{x}.json') for x in fresh},
             historical_prepass_resource_tests='126 selected16state/resource cases retained as historical evidence;unchanged prepass/resources not broadly rerun',
             unchanged_bulk_suites_rerun=False,full_lighting=False,full_world=False,gaps=ref['gaps'],input_exe_executed=False,server_modified=False,
             M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-sky-lighting-checkpoint.json').write_text(json.dumps(out,indent=2)+'\n')
    print('PARTIAL:ordinary lighting/bothfog branches/867samples/27Mie/real loaders/29mapdraws;20GPUviewed;15oldframesstable/Create1;full lighting/M9OPEN')


if __name__=='__main__':main()
