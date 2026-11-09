"""Selected ordinary light-direction checkpoint;full455 acceptance stays open."""
import json
from pathlib import Path
from audit_client455_item_payloads import record
from audit_client455_own_entry import validated_entry
from checkpoint_client455_rvp_effects import check,load,require,sha
from checkpoint_client455_sky_material import reviewed
from checkpoint_client455_sky_lighting import provenance
from checkpoint_client455_lighting_consumers import reused
from client455_normal_link_evidence import validate_normal_link
from compare_client_binaries import WS
from probe_client455_light_direction_math import verify as math_verify
from probe_client455_light_direction import verify as GPU_verify
from probe_client455_lighting_consumers import verify as consumer_verify
from probe_client455_world_frame import verify as world_verify
from probe_client455_sky_material import verify as material_verify
from probe_client455_sky_fade import verify as fade_verify
from probe_client455_sky_lighting import verify as lighting_verify
from probe_client455_weather_owner import verify as weather_verify


def main():
    ref=load('client455-light-direction-reference');require(ref['status']=='CONFIRMED_SELECTED' and ref['script']['sha256']==sha(WS/'scripts/audit_client455_light_direction.py')
            and ref['full_assembly']==10 and ref['primary_instructions']==315 and ref['CRT_context_instructions']==96 and ref['verified_ranges']==11 and ref['CFG_complete'],'Current411-instruction static evidence')
    for row in ref['sources']+[ref[k] for k in ['raw','session','engine','old_engine','previous130_gate']]:check(row)
    require(not ref['shared_headers_changed'] and len(ref['changed_members'])==1 and len(ref['unchanged_members'])==66,'One changed engine payload;shared headers stable')
    link=load('client455-normal-link');require(validate_normal_link(link)=='PASS','Exact current link');lh=sha(WS/'inventory/client455-normal-link.json');require(ref['normal_link_sha256']==lh,'Current linked math proof')
    previous=json.loads((WS/ref['previous130_gate']['file']).read_text());require(sha(WS/'artifacts/client455-progress/normal-before131.bin')==previous['normal_executable']['sha256'],'Exact130 PE preserved')
    require(link['normal_build_sha256']==sha(WS/'artifacts/client455-progress/client455-normal-build-before131.json'),'Client182/20 objects preserved;no shared-header change')
    math=load('client455-light-direction-math');require(math['status']=='PASS_SELECTED','Own CPU math completion')
    for row in math['implementation']+[math[k] for k in ['script','oracle','source','exe','object','map','console','trace','x87_library']]:check(row)
    mv=math_verify(WS/math['trace']['file']);require(mv==math['verdict'] and not math['native']['failures'],'Independent240 CPU cases')
    native=reviewed('client455-light-direction',5);provenance(native,lh)
    for row in [native[k] for k in ['world_source','material_source','oracle','consumer_verifier','trace','consumers_trace','vertices','resolved_input','normal_diagnostic']]+native['captured_shaders']:check(row)
    require(native['driver_script']['sha256']==sha(WS/'scripts/probe_client455_light_direction.py') and native['oracle']['sha256']==sha(WS/'scripts/lit_transform455.py'),'Current GPU oracle')
    run=(WS/native['exe']['file']).parent;gv=GPU_verify(run);cv=consumer_verify(run,native)
    require(gv==native['verdict'] and cv==native['consumer_verdict'] and not native['native']['warnings'],'72 actual LitGrass draws plus normal36/material/5paths')
    stable={'light-direction':reused('light-direction',native)};regressions={}
    for prefix,verify in [('world-frame',world_verify),('sky-material',material_verify),('sky-fade',fade_verify),('sky-lighting',lighting_verify),('weather-owner',weather_verify)]:
        n=reviewed('client455-'+prefix,5);provenance(n,lh);folder=(WS/n['exe']['file']).parent
        verdict=verify(folder,n) if prefix in ['sky-lighting','weather-owner'] else verify(folder)
        require(verdict==n['verdict'],'Fresh current regression '+prefix);regressions[prefix]=verdict;stable[prefix]=reused(prefix,n)
    world=load('client455-world-frame-verification');require(world['native_sha256']==sha(WS/'inventory/client455-world-frame-native.json') and world['verdict']==regressions['world-frame'],'Current world evidence')
    ordinary=load('client455-normal-consumers');require(ordinary['native']['status']=='PASS' and ordinary['normal_build_sha256']==link['normal_build_sha256'],'Current short ANI/BBX consumer checks')
    for row in ordinary['libraries']+ordinary['objects']:check(row)
    entry=validated_entry();require(entry['normal_link_sha256']==lh,'Current decoded own-entry points')
    early,ui,contracts=load('client455-startup-native'),load('client455-ui-startup-native'),load('client455-startup-contracts-native');engine=load('client455-startup-engine-build');audit=load('client455-startup-audit')
    require(early['normal_link_sha256']==ui['normal_link_sha256']==audit['normal_link_sha256']==lh and not early['debugger_exit'] and early['sound_return']==1
            and not ui['debugger_exit'] and ui['completed_existing_client_create'] and any(x['name']=='after_client_create' and x['eax']==1 for x in ui['markers'])
            and contracts['build_sha256']==sha(WS/'inventory/client455-startup-engine-build.json') and not audit['unresolved_provider_modules'],'Exact own PE sound/device/existingCreate1/providers')
    require(engine['library_sha256']==ref['engine']['sha256'] and any(x['sha256']==ref['engine']['sha256'] for x in link['libraries']),'Current engine linked')
    check(early['events']);check(ui['events']);fresh=['light-direction-reference','light-direction-math','light-direction-native','light-direction-visual-review','normal-build','normal-consumers','normal-link','own-entry','startup-engine-build','startup-audit','startup-native','startup-contracts-native','ui-startup-native','world-frame-verification']
    for prefix in regressions:fresh.extend([prefix+'-native',prefix+'-visual-review'])
    out=dict(status='PARTIAL',scope=ref['scope'],script=record(Path(__file__)),normal_executable=link['executable'],normal_link_sha256=lh,engine=ref['engine'],old_engine=ref['old_engine'],CPU_math=mv,GPU_direction=gv,consumers=cv,regressions=regressions,
             previously_reviewed_byte_equal130=stable,visually_accounted_GPU_frames=30,new_visual_inspection=False,shared_headers_changed=False,client_objects=182,kernel_objects=20,engine_payload_changed=1,engine_payload_unchanged=66,
             previous130_gate=ref['previous130_gate'],fresh_evidence={name:record(WS/f'inventory/client455-{name}.json') for name in fresh},gaps=ref['gaps'],unchanged_bulk_suites_rerun=False,
             full_CRT=False,full_lighting=False,full_world=False,full_client=False,input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-light-direction-checkpoint.json').write_text(json.dumps(out,indent=2)+'\n');print('PARTIAL:240CPU/12FPmodes/72actual LitGrass directions/exact3linked bodies/30freshpixelsstable/Create1;M6/M9OPEN')


if __name__=='__main__':main()
