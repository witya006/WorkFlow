"""Current partialM6 gate for connected weather producers and ordinary map owner."""
import json
from pathlib import Path
from audit_client455_item_payloads import record
from checkpoint_client455_rvp_effects import check,load,require,sha
from checkpoint_client455_sky_material import reviewed
from checkpoint_client455_sky_lighting import provenance
from client455_normal_link_evidence import validate_normal_link
from compare_client_binaries import WS
from probe_client455_weather_owner import verify as verify_weather
from probe_client455_sky_lighting import verify as verify_lighting
from probe_client455_sky_material import verify as verify_material
from probe_client455_sky_fade import verify as verify_fade
from probe_client455_world_frame import verify as verify_world


def old_pixels(native,name):
    old=load_backup(name);before={Path(x['file']).name:x for x in old['frames']};same=[]
    for row in native['frames']:
        previous=before[Path(row['file']).name];check(previous);require(row['sha256']==previous['sha256'],'128 regression pixels preserved')
        same.append(Path(row['file']).name)
    return same


def load_backup(name):return json.loads((WS/f'artifacts/client455-progress/{name}-before129.json').read_text())


def main():
    ref=load('client455-weather-owner-reference');require(ref['status']=='CONFIRMED_SELECTED' and ref['full_assembly']==6 and ref['instructions']==1546 and ref['verified_ranges']==7 and ref['CFG_complete']
            and ref['shared_headers_changed'] and ref['script_sha256']==sha(WS/'scripts/audit_client455_weather_owner.py'),'Current reference/source audit')
    for row in [ref[x] for x in ['raw','session','engine','old_engine','level_header_overlay']]+ref['sources']+ref['reused_sources']:check(row)
    link=load('client455-normal-link');require(validate_normal_link(link)=='PASS','Exact normal link');lh=sha(WS/'inventory/client455-normal-link.json')
    engine=load('client455-startup-engine-build');require(engine['library_sha256']==ref['engine']['sha256'] and any(x['file']==engine['library'] and x['sha256']==ref['engine']['sha256'] for x in link['libraries']),'Actual current engine retained')
    weather=reviewed('client455-weather-owner',5);provenance(weather,lh)
    require(weather['driver_script']['sha256']==sha(WS/'scripts/probe_client455_weather_owner.py'),'Current weather verifier')
    for row in [weather[x] for x in ['source','included_source','world_source','driver_script','trace','exe','map','console','output']]+weather['inputs']:check(row)
    wv=verify_weather((WS/weather['exe']['file']).parent,weather)
    require(weather['status']=='PASS_SELECTED' and wv==weather['verdict'] and wv['packed_cases']==90 and wv['software_aggregate_cases']==5 and weather['native']['warnings']==1,'Actual packed producers/map owner/selected fog aggregates')
    lighting=reviewed('client455-sky-lighting',5);provenance(lighting,lh);check(lighting['trace']);check(lighting['world_source'])
    lv=verify_lighting((WS/lighting['exe']['file']).parent,lighting)
    require(lv==lighting['verdict'] and lv['software_samples']==867 and lv['additional_fog_frames']==3 and lighting['native']['warnings']==2,'Current both-fog/frame/loader regression')
    world=reviewed('client455-world-frame',5);provenance(world,lh);validation=load('client455-world-frame-verification')
    require(validation['native_sha256']==sha(WS/'inventory/client455-world-frame-native.json') and verify_world((WS/world['exe']['file']).parent)==world['verdict']==validation['verdict'],'Current world/FX/light regression')
    fade=reviewed('client455-sky-fade',5);provenance(fade,lh)
    require(verify_fade((WS/fade['exe']['file']).parent)==fade['verdict'] and not fade['native']['warnings'],'Current fade regression')
    material=reviewed('client455-sky-material',5);provenance(material,lh)
    require(verify_material((WS/material['exe']['file']).parent)==material['verdict'] and material['native']['warnings']==1,'Current material/night regression')
    same={name:old_pixels(native,name) for native,name in [(lighting,'client455-sky-lighting-native'),(world,'client455-world-frame-native'),(fade,'client455-sky-fade-native'),(material,'client455-sky-material-native')]}
    consumers=load('client455-normal-consumers');require(consumers['native']['status']=='PASS' and consumers['normal_build_sha256']==link['normal_build_sha256'],'Current ANI/BBX consumers')
    for row in consumers['libraries']+consumers['objects']:check(row)
    early,ui,contracts=load('client455-startup-native'),load('client455-ui-startup-native'),load('client455-startup-contracts-native')
    require(early['normal_link_sha256']==ui['normal_link_sha256']==lh and not early['debugger_exit'] and early['sound_return']==1 and not ui['debugger_exit']
            and ui['completed_existing_client_create'] and any(x['name']=='after_client_create' and x['eax']==1 for x in ui['markers'])
            and contracts['build_sha256']==sha(WS/'inventory/client455-startup-engine-build.json'),'Current exact PE sound/window/device/Create1/contracts')
    check(early['events']);check(ui['events']);audit=load('client455-startup-audit');require(audit['normal_link_sha256']==lh and not audit['unresolved_provider_modules'],'Current startup dependencies')
    old_gate_file=WS/'artifacts/client455-progress/client455-sky-lighting-checkpoint-before129.json';old_gate=json.loads(old_gate_file.read_text())
    require(old_gate['normal_executable']['sha256']==sha(WS/'artifacts/client455-progress/normal-before129.bin')
            and old_gate['engine']['sha256']==ref['old_engine']['sha256'],'Exact previous128 checkpoint/engine/PE backup')
    fresh=['weather-owner-reference','weather-owner-native','weather-owner-visual-review','sky-lighting-inputs','sky-lighting-native','sky-lighting-visual-review',
           'world-frame-native','world-frame-verification','world-frame-visual-review','sky-fade-native','sky-fade-visual-review','sky-material-native','sky-material-visual-review',
           'startup-engine-build','normal-build','normal-consumers','normal-link','own-entry','startup-audit','startup-native','startup-contracts-native','ui-startup-native']
    out=dict(status='PARTIAL',scope=ref['scope'],script_sha256=sha(Path(__file__)),normal_executable=link['executable'],normal_link_sha256=lh,
             engine=ref['engine'],old_engine=ref['old_engine'],weather=wv,lighting=lv,world=world['verdict'],fade=fade['verdict'],material=material['verdict'],
             viewed_GPU_frames=25,regression_frames_byte_equal128=same,previous128_gate=record(old_gate_file),fresh_evidence={x:record(WS/f'inventory/client455-{x}.json') for x in fresh},
             shared_headers_changed=True,client_objects=182,kernel_objects=20,casefold_correction=ref['casefold_correction'],gaps=ref['gaps'],
             unchanged_bulk_suites_rerun=False,full_lighting=False,full_world=False,full_client=False,input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-weather-owner-checkpoint.json').write_text(json.dumps(out,indent=2)+'\n')
    print('PARTIAL:90 packed script cases/actual map virtual owner/5 fog aggregates/25GPUviewed/20oldframesstable/Create1;M6/M9OPEN')


if __name__=='__main__':main()
