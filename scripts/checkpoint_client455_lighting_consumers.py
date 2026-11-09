"""Current partialM6 gate for actual geometry/material/entity lighting consumers."""
import json
from pathlib import Path
from audit_client455_item_payloads import record
from checkpoint_client455_rvp_effects import check,load,require,sha
from checkpoint_client455_sky_material import reviewed
from checkpoint_client455_sky_lighting import provenance
from client455_normal_link_evidence import validate_normal_link
from compare_client_binaries import WS
from probe_client455_lighting_consumers import verify as verify_consumers
from probe_client455_weather_owner import verify as verify_weather
from probe_client455_sky_lighting import verify as verify_lighting
from probe_client455_world_frame import verify as verify_world
from probe_client455_sky_fade import verify as verify_fade
from probe_client455_sky_material import verify as verify_material


def reused(prefix,native):
    review=load('client455-'+prefix+'-visual-review')
    require(review['reused_pixels_byte_equal'] and not review['new_visual_inspection']
            and review['script_sha256']==sha(WS/'scripts/reuse_client455_visual_review.py'),'Explicitly reused visual evidence '+prefix)
    check(review['reused_from_review']);check(review['reused_from_native'])
    before=json.loads((WS/review['reused_from_native']['file']).read_text());old_review=json.loads((WS/review['reused_from_review']['file']).read_text())
    require(old_review['reviewed'] and old_review['native_sha256']==review['reused_from_native']['sha256'],'Original review provenance')
    old={Path(x['file']).name:x for x in before['frames']};same=[]
    for row in native['frames']:
        previous=old[Path(row['file']).name];check(row);check(row['preview']);check(previous);check(previous['preview'])
        require(row['sha256']==previous['sha256'] and row['preview']['sha256']==previous['preview']['sha256'],'Exact previously reviewed pixels '+prefix)
        same.append(Path(row['file']).name)
    return same


def main():
    ref=load('client455-lighting-consumers-reference');require(ref['status']=='CONFIRMED_SELECTED' and ref['full_assembly']==17 and ref['instructions']==3450 and ref['verified_ranges']==18
            and ref['CFG_complete'] and ref['script_sha256']==sha(WS/'scripts/audit_client455_lighting_consumers.py'),'Current pinned reference/source audit')
    for row in ref['raw']+ref['sessions']+ref['sources']+[ref[x] for x in ['transform_context','port_script','vertex_header','engine','old_engine']]:check(row)
    link=load('client455-normal-link');require(validate_normal_link(link)=='PASS','Exact current normal link');lh=sha(WS/'inventory/client455-normal-link.json')
    engine=load('client455-startup-engine-build');require(engine['library_sha256']==ref['engine']['sha256'] and any(x['file']==engine['library'] and x['sha256']==ref['engine']['sha256'] for x in link['libraries']),'Current engine retained')
    consumers=reviewed('client455-lighting-consumers',5);provenance(consumers,lh)
    require(consumers['driver_script']['sha256']==sha(WS/'scripts/probe_client455_lighting_consumers.py'),'Current independent verifier')
    for row in [consumers[x] for x in ['source','included_source','world_source','driver_script','trace','vertices','resolved_input','normal_diagnostic','exe','map','console','output']]+consumers['captured_shaders']+consumers['inputs']:check(row)
    cv=verify_consumers((WS/consumers['exe']['file']).parent,consumers)
    require(cv==consumers['verdict'] and cv['geometry']['vertices']==5328 and cv['geometry']['normal_bit_mismatches']==0 and not consumers['native']['warnings'],'Actual geometry and consumers')
    results={};stable={}
    for prefix,verify in [('weather-owner',verify_weather),('sky-lighting',verify_lighting),('world-frame',verify_world),('sky-fade',verify_fade),('sky-material',verify_material)]:
        native=reviewed('client455-'+prefix,5);provenance(native,lh)
        if prefix in ['weather-owner','sky-lighting']:value=verify((WS/native['exe']['file']).parent,native)
        else:value=verify((WS/native['exe']['file']).parent)
        require(value==native['verdict'],'Current regression '+prefix);results[prefix]=value;stable[prefix]=reused(prefix,native)
    verification=load('client455-world-frame-verification');require(verification['native_sha256']==sha(WS/'inventory/client455-world-frame-native.json') and verification['verdict']==results['world-frame'],'Current world verification')
    ordinary=load('client455-normal-consumers');require(ordinary['native']['status']=='PASS' and ordinary['normal_build_sha256']==link['normal_build_sha256'],'Current ANI/BBX consumers')
    for row in ordinary['libraries']+ordinary['objects']:check(row)
    early,ui,contracts=load('client455-startup-native'),load('client455-ui-startup-native'),load('client455-startup-contracts-native')
    require(early['normal_link_sha256']==ui['normal_link_sha256']==lh and not early['debugger_exit'] and early['sound_return']==1
            and not ui['debugger_exit'] and ui['completed_existing_client_create'] and any(x['name']=='after_client_create' and x['eax']==1 for x in ui['markers'])
            and contracts['build_sha256']==sha(WS/'inventory/client455-startup-engine-build.json'),'Exact current PE startup/window/device/existingCreate1')
    check(early['events']);check(ui['events']);audit=load('client455-startup-audit');require(audit['normal_link_sha256']==lh and not audit['unresolved_provider_modules'],'Current startup providers')
    previous=WS/'artifacts/client455-progress/client455-weather-owner-checkpoint-before130.json';old=json.loads(previous.read_text())
    require(old['normal_executable']['sha256']==sha(WS/'artifacts/client455-progress/normal-before130.bin') and old['engine']['sha256']==ref['old_engine']['sha256'],'Exact129 backup')
    fresh=['lighting-consumers-reference','lighting-consumers-native','lighting-consumers-visual-review','weather-owner-native','weather-owner-visual-review','sky-lighting-native','sky-lighting-visual-review',
           'world-frame-native','world-frame-verification','world-frame-visual-review','sky-fade-native','sky-fade-visual-review','sky-material-native','sky-material-visual-review','startup-engine-build',
           'normal-build','normal-preparation','normal-consumers','normal-link','own-entry','startup-audit','startup-native','startup-contracts-native','ui-startup-native']
    out=dict(status='PARTIAL',scope=ref['scope'],script_sha256=sha(Path(__file__)),normal_executable=link['executable'],normal_link_sha256=lh,engine=ref['engine'],old_engine=ref['old_engine'],
             consumers=cv,regressions=results,visually_accounted_GPU_frames=30,newly_viewed_GPU_frames=5,previously_reviewed_byte_equal129=stable,
             shared_headers_changed=True,client_objects=182,kernel_objects=20,previous129_gate=record(previous),fresh_evidence={x:record(WS/f'inventory/client455-{x}.json') for x in fresh},
             unchanged_bulk_suites_rerun=False,gaps=ref['gaps'],full_lighting=False,full_world=False,full_client=False,input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-lighting-consumers-checkpoint.json').write_text(json.dumps(out,indent=2)+'\n')
    print('PARTIAL:normal36/5328 exact selected normals/5actual paths/pinned GPU shaders/8material cases/Create1;5new GPUviewed/25oldpixelsstable;M6/M9OPEN')


if __name__=='__main__':main()
