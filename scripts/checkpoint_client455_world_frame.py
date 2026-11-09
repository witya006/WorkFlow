"""Current partial M6 proof,including retraction of119wrong class view claim."""
import json
from pathlib import Path
from audit_client455_item_payloads import record
from checkpoint_client455_rvp_effects import check,load,require,sha
from client455_normal_link_evidence import validate_normal_link
from compare_client_binaries import WS
from probe_client455_quake import verify as verify_cpu
from probe_client455_quake_effects import verify as verify_fx
from probe_client455_world_frame import verify as verify_world

def main():
    ref=load('client455-world-frame-reference');require(ref['status']=='CONFIRMED_SELECTED' and ref['script_sha256']==sha(WS/'scripts/audit_client455_world_frame.py') and ref['full_assembly']==26 and ref['instructions']==2772,'Static455class/lighting proof')
    for row in [ref['raw'],ref['session'],ref['extra_session'],ref['source'],ref['engine'],ref['old_engine']]:check(row)
    link=load('client455-normal-link');validate_normal_link(link);lh=sha(WS/'inventory/client455-normal-link.json');engine=load('client455-startup-engine-build');require(engine['library_sha256']==ref['engine']['sha256'] and any(x['file']==engine['library'] and x['sha256']==engine['library_sha256'] for x in link['libraries']),'Current engine in ordinary PE');check(link['executable']);check(link['map'])
    cpu=load('client455-quake-native');require(cpu['normal_link_sha256']==lh and cpu['script_sha256']==sha(WS/'scripts/probe_client455_quake.py') and cpu['engine_report_sha256']==sha(WS/'inventory/client455-startup-engine-build.json'),'Current corrected camera CPU')
    for row in [cpu['source'],cpu['oracle'],cpu['exe'],cpu['map'],cpu['trace'],cpu['console']]:check(row)
    require(verify_cpu(json.loads((WS/cpu['trace']['file']).read_text()))==cpu['verdict'],'Corrected current-view oracle')
    fx=load('client455-quake-effects-native');require(fx['normal_link_sha256']==lh and fx['status']=='PASS' and fx['script_sha256']==sha(WS/'scripts/probe_client455_nuclear_registry.py') and not fx['natural_exit'] and fx['native']['warnings']==20,'Current archived explosion')
    for row in [fx['source'],fx['oracle'],fx['exe'],fx['map'],fx['trace'],fx['console'],fx['output'],fx['registry_template'],fx['trace_header'],fx['driver_script']]+fx['inputs']:check(row)
    require(verify_fx(json.loads((WS/fx['trace']['file']).read_text()))==fx['verdict'],'Actual impact oracle')
    world=load('client455-world-frame-native');verification=load('client455-world-frame-verification');require(world['normal_link_sha256']==lh and world['status']=='PASS' and verification['status']=='PASS_SELECTED' and verification['script_sha256']==sha(WS/'scripts/verify_client455_world_frame.py') and verification['native_sha256']==sha(WS/'inventory/client455-world-frame-native.json') and verification['reference_sha256']==sha(WS/'inventory/client455-world-frame-reference.json'),'Current world validation')
    for row in [world['source'],world['included_source'],world['driver_script'],world['oracle'],world['exe'],world['map'],world['console'],world['output'],verification['diagnostic'],verification['texture'],verification['texture_preview']]+world['trace']+world['inputs']:check(row)
    require(verify_world((WS/world['exe']['file']).parent)==world['verdict']==verification['verdict'],'Reproduce76queue/live clock/matched light controls')
    for key in ['world-frame','quake']:
        review=load('client455-'+key+'-visual-review');native_name='world-frame-native' if key=='world-frame' else 'quake-effects-native';require(review['reviewed'] and review['reviewed_frames']==5 and review['native_sha256']==sha(WS/('inventory/client455-'+native_name+'.json')),'Current visual review');check(review['sheet'])
        for row in review['frames']:check(row);check(row['preview'])
    maps=load('client455-map-data-native');require(maps['normal_link_sha256']==lh and maps['native']['checks']==2692 and maps['native']['geometry_cases']==330 and maps['canonical_equal'] and not maps['natural_exit'],'Fresh map regression');check(maps['output']);check(maps['canonical_actual'])
    early,ui,contracts=load('client455-startup-native'),load('client455-ui-startup-native'),load('client455-startup-contracts-native');require(contracts['build_sha256']==sha(WS/'inventory/client455-startup-engine-build.json') and early['normal_link_sha256']==ui['normal_link_sha256']==lh and not early['debugger_exit'] and early['sound_return']==1 and not ui['debugger_exit'] and ui['completed_existing_client_create'] and any(x['name']=='after_client_create' and x['eax']==1 for x in ui['markers']) and all(x['first_chance']==1 for x in ui['exceptions']),'Own PE startup/window/device/Create1');check(early['events']);check(ui['events'])
    old=WS/'artifacts/client455-progress/client455-quake-checkpoint-before120.json';require(old.exists(),'119 historical gate retained')
    fresh=['world-frame-reference','world-frame-native','world-frame-verification','world-frame-visual-review','quake-native','quake-effects-native','quake-visual-review','startup-engine-build','normal-link','normal-consumers','own-entry','startup-audit','startup-native','startup-contracts-native','ui-startup-native','map-data-native']
    result=dict(status='PARTIAL',scope=ref['scope'],script_sha256=sha(Path(__file__)),normal_executable=link['executable'],normal_link_sha256=lh,engine=ref['engine'],old_engine=ref['old_engine'],correction119=ref['correction119'],native_cpu=cpu['verdict'],actual_impact=fx['verdict'],world=world['verdict'],viewed_GPU_frames=10,previous119_gate=record(old),fresh_evidence={x:record(WS/f'inventory/client455-{x}.json') for x in fresh},known_geometry_differences_restored=False,full_world=False,full_renderer=False,gaps=ref['gaps'],old_runtime_gates='HISTORICAL;119previous-view claim retracted;older texture/receiver/Character/bulk not rerun',unchanged_bulk_suites_rerun=False,input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-world-frame-checkpoint.json').write_text(json.dumps(result,indent=2)+'\n');print('PARTIAL:correct CLevel current-view/26asm2772;76light queue cases/16OSclock±1/real Bellato light+FX/10GPUviewed/maps2692/Create1;geometry differences+M9OPEN')

if __name__=='__main__':main()
