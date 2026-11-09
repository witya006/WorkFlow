"""Current selected map-lighting owner proof;M6/M9 stay open."""
import json
from pathlib import Path
from audit_client455_item_payloads import record
from audit_client455_own_entry import validated_entry
from checkpoint_client455_rvp_effects import load,require,check,sha
from checkpoint_client455_sky_material import reviewed
from checkpoint_client455_sky_lighting import provenance
from checkpoint_client455_lighting_consumers import reused
from client455_normal_link_evidence import validate_normal_link
from compare_client_binaries import WS
from probe_client455_entity_owner import verify as owner_verify
from probe_client455_light_direction import verify as direction_verify
from probe_client455_lighting_consumers import verify as consumers_verify
from probe_client455_world_frame import verify as world_verify
from probe_client455_sky_material import verify as material_verify
from probe_client455_sky_fade import verify as fade_verify
from probe_client455_sky_lighting import verify as lighting_verify
from probe_client455_weather_owner import verify as weather_verify


def main():
    ref=load('client455-entity-owner-reference');require(ref['status']=='CONFIRMED_SELECTED' and ref['script']['sha256']==sha(WS/'scripts/audit_client455_entity_owner.py') and ref['full_assembly']==5 and ref['instructions']==1665 and ref['verified_ranges']==5 and ref['CFG_complete'],'Complete selected source/reference proof')
    for key in ['raw','session','reused1025_instruction_body','inputs','source','generated_source','engine','old_engine','previous131_gate']:check(ref[key])
    require(len(ref['changed_members'])==1 and len(ref['unchanged_members'])==66 and not ref['shared_headers_changed'],'Only BSP payload changed')
    link=load('client455-normal-link');require(validate_normal_link(link)=='PASS','Current own full PE');lh=sha(WS/'inventory/client455-normal-link.json');require(ref['normal_link_sha256']==lh,'Current linked evidence')
    previous=json.loads((WS/ref['previous131_gate']['file']).read_text());require(sha(WS/'artifacts/client455-progress/normal-before132.bin')==previous['normal_executable']['sha256'] and link['normal_build_sha256']==sha(WS/'artifacts/client455-progress/client455-normal-build-before132.json'),'Exact131 preserved;182/20client objects stable')
    native=reviewed('client455-entity-owner',4);provenance(native,lh)
    for row in [native[k] for k in ['world_source','material_source','input_parser','trace']]:check(row)
    require(native['driver_script']['sha256']==sha(WS/'scripts/probe_client455_entity_owner.py') and native['native']['warnings']==2,'Current own map probe/known missing input warnings')
    ov=owner_verify((WS/native['exe']['file']).parent,native);require(ov==native['verdict'],'Actual original EBP flags and ordinary map draw route')
    direction=reviewed('client455-light-direction',5);provenance(direction,lh);folder=(WS/direction['exe']['file']).parent;dv=direction_verify(folder);cv=consumers_verify(folder,direction)
    require(dv==direction['verdict'] and cv==direction['consumer_verdict'],'Retained direction and normal/material paths')
    for key in ['oracle','consumer_verifier','trace','consumers_trace','world_source','material_source','vertices','resolved_input','normal_diagnostic']:check(direction[key])
    old_math=load('client455-light-direction-math')
    for row in old_math['implementation']+[old_math[k] for k in ['script','oracle','source','exe','object','map','console','trace','x87_library']]:check(row)
    require(old_math['verdict']==previous['CPU_math'],'Unchanged240CPU math proof explicitly retained')
    stable={'light-direction':reused('light-direction',direction)};results={}
    for prefix,verify in [('world-frame',world_verify),('sky-material',material_verify),('sky-fade',fade_verify),('sky-lighting',lighting_verify),('weather-owner',weather_verify)]:
        n=reviewed('client455-'+prefix,5);provenance(n,lh);folder=(WS/n['exe']['file']).parent;value=verify(folder,n) if prefix in ['sky-lighting','weather-owner'] else verify(folder)
        require(value==n['verdict'],'Current native regression '+prefix);results[prefix]=value;stable[prefix]=reused(prefix,n)
    validation=load('client455-world-frame-verification');require(validation['native_sha256']==sha(WS/'inventory/client455-world-frame-native.json') and validation['verdict']==results['world-frame'],'Fresh current world validation')
    ordinary=load('client455-normal-consumers');require(ordinary['native']['status']=='PASS' and ordinary['normal_build_sha256']==link['normal_build_sha256'],'Current short ANI/BBX consumers')
    for row in ordinary['libraries']+ordinary['objects']:check(row)
    entry=validated_entry();require(entry['normal_link_sha256']==lh,'Current decoded own-entry points');engine=load('client455-startup-engine-build');early,ui,contracts,audit=load('client455-startup-native'),load('client455-ui-startup-native'),load('client455-startup-contracts-native'),load('client455-startup-audit')
    require(early['normal_link_sha256']==ui['normal_link_sha256']==audit['normal_link_sha256']==lh and not early['debugger_exit'] and early['sound_return']==1 and not ui['debugger_exit'] and ui['completed_existing_client_create']
            and any(x['name']=='after_client_create' and x['eax']==1 for x in ui['markers']) and contracts['build_sha256']==sha(WS/'inventory/client455-startup-engine-build.json') and not audit['unresolved_provider_modules'],'Exact current PE sound/window/device/existingCreate1/providers')
    check(early['events']);check(ui['events']);require(engine['library_sha256']==ref['engine']['sha256'] and any(x['sha256']==ref['engine']['sha256'] for x in link['libraries']),'Current engine actually linked')
    fresh=['entity-owner-reference','entity-owner-native','entity-owner-visual-review','entity-flags-inputs','light-direction-native','light-direction-visual-review','normal-build','normal-consumers','normal-link','own-entry','startup-engine-build','startup-audit','startup-native','startup-contracts-native','ui-startup-native','world-frame-verification']
    for prefix in results:fresh.extend([prefix+'-native',prefix+'-visual-review'])
    out=dict(status='PARTIAL',scope=ref['scope'],script=record(Path(__file__)),normal_executable=link['executable'],normal_link_sha256=lh,engine=ref['engine'],old_engine=ref['old_engine'],map_owner=ov,inventory=load('client455-entity-flags-inputs')['totals'],direction=dv,consumers=cv,regressions=results,
             retained_unchanged_CPU_math=record(WS/'inventory/client455-light-direction-math.json'),previously_reviewed_byte_equal131=stable,newly_viewed_GPU_frames=4,visually_accounted_GPU_frames=34,shared_headers_changed=False,client_objects=182,kernel_objects=20,
             previous131_gate=ref['previous131_gate'],fresh_evidence={name:record(WS/f'inventory/client455-{name}.json') for name in fresh},gaps=ref['gaps'],unchanged_bulk_suites_rerun=False,full_lighting=False,full_world=False,full_client=False,input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-entity-owner-checkpoint.json').write_text(json.dumps(out,indent=2)+'\n');print('PARTIAL:real map flag40 owner/20available NeutralB entries/two loads/4BSPdraws/4newGPUviewed/30oldpixelsstable/Create1;M6/M9OPEN')


if __name__=='__main__':main()
