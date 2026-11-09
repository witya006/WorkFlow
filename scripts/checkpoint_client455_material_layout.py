"""Current selected material migration checkpoint;full455 acceptance stays open."""
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
from probe_client455_material_layout import verify as material_layout_verify
from probe_client455_entity_owner import verify as owner_verify
from probe_client455_light_direction import verify as direction_verify
from probe_client455_lighting_consumers import verify as consumers_verify
from probe_client455_world_frame import verify as world_verify
from probe_client455_sky_material import verify as material_verify
from probe_client455_sky_fade import verify as fade_verify
from probe_client455_sky_lighting import verify as lighting_verify
from probe_client455_weather_owner import verify as weather_verify


def main():
    ref=load('client455-material-layout-reference');require(ref['status']=='CONFIRMED_SELECTED' and ref['script']['sha256']==sha(WS/'scripts/audit_client455_material_layout.py') and ref['full_assembly']==5 and ref['instructions']==1438 and ref['verified_ranges']==5 and ref['CFG_complete'],'Current5fullasm1438-instruction reference')
    for key in ['raw','session','material_header','port_script','generated_source','engine','old_engine','previous132_gate']:check(ref[key])
    require(ref['shared_headers_changed'],'Runtime layout migration requires full consumers rebuild');link=load('client455-normal-link');require(validate_normal_link(link)=='PASS','Current own full client link');lh=sha(WS/'inventory/client455-normal-link.json');require(ref['normal_link_sha256']==lh,'Current linked reference evidence')
    engine=load('client455-startup-engine-build');build=load('client455-normal-build');prep=load('client455-normal-preparation');require(not build['build_exit'] and build['objects']==182 and build['canonical_kernel_objects']==20 and prep['camera_header_overlay']['sha256']==engine['camera_header_overlay']['sha256'],'Actual changed shared header in all182/20consumers')
    native=load('client455-material-layout-native');provenance(native,lh);require(native['status']=='PASS_SELECTED' and not native['frames'] and native['driver_script']['sha256']==sha(WS/'scripts/probe_client455_material_layout.py'),'Successful CPU loader probe')
    for row in [native[k] for k in ['material_source','world_source']]+native['generated_inputs']+native['outputs']:check(row)
    mv=material_layout_verify((WS/native['exe']['file']).parent,native);require(mv==native['verdict'],'Exact runtime records/serialized prefixes and actual version failure cleanup')
    owner=reviewed('client455-entity-owner',4);provenance(owner,lh);ov=owner_verify((WS/owner['exe']['file']).parent,owner);require(ov==owner['verdict'],'Real auto-lit map owner remains working');check(owner['trace']);check(owner['input_parser'])
    direction=reviewed('client455-light-direction',5);provenance(direction,lh);folder=(WS/direction['exe']['file']).parent;dv=direction_verify(folder);cv=consumers_verify(folder,direction);require(dv==direction['verdict'] and cv==direction['consumer_verdict'],'Direction,normal36 and materialD3Dstate regressions')
    for key in ['oracle','consumer_verifier','trace','consumers_trace','world_source','material_source','vertices','resolved_input','normal_diagnostic']:check(direction[key])
    stable={'entity-owner':reused('entity-owner',owner),'light-direction':reused('light-direction',direction)};results={}
    for prefix,verify in [('world-frame',world_verify),('sky-material',material_verify),('sky-fade',fade_verify),('sky-lighting',lighting_verify),('weather-owner',weather_verify)]:
        n=reviewed('client455-'+prefix,5);provenance(n,lh);folder=(WS/n['exe']['file']).parent;value=verify(folder,n) if prefix in ['sky-lighting','weather-owner'] else verify(folder)
        require(value==n['verdict'],'Current native regression '+prefix);results[prefix]=value;stable[prefix]=reused(prefix,n)
    world=load('client455-world-frame-verification');require(world['native_sha256']==sha(WS/'inventory/client455-world-frame-native.json') and world['verdict']==results['world-frame'],'Fresh world verification')
    ordinary=load('client455-normal-consumers');require(ordinary['native']['status']=='PASS' and ordinary['normal_build_sha256']==link['normal_build_sha256'],'Fresh actual ANI/BBX consumers')
    for row in ordinary['libraries']+ordinary['objects']:check(row)
    require(validated_entry()['normal_link_sha256']==lh,'Current decoded own-entry');early,ui,contracts,audit=load('client455-startup-native'),load('client455-ui-startup-native'),load('client455-startup-contracts-native'),load('client455-startup-audit')
    require(early['normal_link_sha256']==ui['normal_link_sha256']==audit['normal_link_sha256']==lh and not early['debugger_exit'] and early['sound_return']==1 and not ui['debugger_exit'] and ui['completed_existing_client_create'] and any(x['name']=='after_client_create' and x['eax']==1 for x in ui['markers']) and contracts['build_sha256']==sha(WS/'inventory/client455-startup-engine-build.json') and not audit['unresolved_provider_modules'],'Exact own PE sound/window/device/existingCreate1/contracts/providers')
    check(early['events']);check(ui['events']);require(engine['library_sha256']==ref['engine']['sha256'] and any(x['sha256']==ref['engine']['sha256'] for x in link['libraries']),'Current engine actually linked')
    old=json.loads((WS/ref['previous132_gate']['file']).read_text());require(sha(WS/'artifacts/client455-progress/normal-before133.bin')==old['normal_executable']['sha256'],'Exact132 PE backup')
    fresh=['material-layout-reference','material-layout-native','entity-owner-native','entity-owner-visual-review','light-direction-native','light-direction-visual-review','normal-build','normal-preparation','normal-consumers','normal-link','own-entry','startup-engine-build','startup-audit','startup-native','startup-contracts-native','ui-startup-native','world-frame-verification']
    for prefix in results:fresh.extend([prefix+'-native',prefix+'-visual-review'])
    out=dict(status='PARTIAL',scope=ref['scope'],script=record(Path(__file__)),normal_executable=link['executable'],normal_link_sha256=lh,engine=ref['engine'],old_engine=ref['old_engine'],material_loaders=mv,map_owner=ov,direction=dv,consumers=cv,regressions=results,
             previously_reviewed_byte_equal132=stable,visually_accounted_GPU_frames=34,new_visual_inspection=False,shared_headers_changed=True,client_objects=182,kernel_objects=20,previous132_gate=ref['previous132_gate'],fresh_evidence={name:record(WS/f'inventory/client455-{name}.json') for name in fresh},gaps=ref['gaps'],unchanged_bulk_suites_rerun=False,full_material_shader=False,full_lighting=False,full_world=False,full_client=False,input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-material-layout-checkpoint.json').write_text(json.dumps(out,indent=2)+'\n');print('PARTIAL:7layers/54runtime/46serialized/526material/actualtext-binary loaders/full182-20/Create1/34freshpixelsstable;M6/M9OPEN')


if __name__=='__main__':main()
