"""Accept actual ordinary common-object migration with affected regressions."""
import hashlib,json,re
from pathlib import Path
from audit_client455_item_payloads import record
from build_client455_x87_math import read_va
from checkpoint_client455_rvp_effects import check,load,require,sha
from client455_normal_link_evidence import validate_normal_link
from compare_client_binaries import WS,pe

def main():
    ref=load('client455-resource-object-reference')
    require(ref['script_sha256']==sha(WS/'scripts/audit_client455_resource_object.py') and len(ref['assembly'])==14 and ref['actual_instructions']==765,'Reference provenance')
    for row in ref['raw_evidence']+ref['fixtures']:check(row)
    pins=json.loads((WS/'config/client-target.json').read_text())
    for folder,key,pin in zip(['current','reference-backup'],['behavior_reference','secondary_reference'],ref['references']):
        binary=WS/f'work/client-reference/{folder}/RF_Online.bin';raw=binary.read_bytes()
        require(sha(binary)==pin['sha256']==pins[key]['sha256'] and pe(raw)['architecture']=='x86' and len(pin['ranges'])==23,'Changed pinned client')
        for row in pin['ranges']+pin['external_assembly_windows']:
            require(hashlib.sha256(read_va(raw,0x400000+int(row['rva'],16),row['bytes'])).hexdigest()==row['sha256'],'Function/EH range drift')
        for row in pin['profile_constants']:require(read_va(raw,0x400000+int(row['rva'],16),4).hex()==row['bytes'],'Secondary defaults drift')
    session_path=WS/'artifacts/client455-progress/res-object090-session.json';session=json.loads(session_path.read_text())
    require(session['closed']['success'] and session['closed']['saved'] and session['after']['count']==0,'IDA session cleanup')
    link=load('client455-normal-link');require(validate_normal_link(link)=='PASS' and not link['unique_unresolved'] and link['client_objects']==182,'Real normal link')
    link_hash=sha(WS/'inventory/client455-normal-link.json');prep=load('client455-normal-preparation')
    require(prep['script_sha256']==sha(WS/'scripts/prepare_client455_normal.py') and prep['resource_object_port_sha256']==sha(WS/'scripts/client455_resource_object_port.py'),'Current migration source')
    for name in ['client455_object_copy.inc','client455_resource_object_ctor.inc','client455_resource_object_copy.inc']:
        require(prep['record_inputs'][name]==sha(WS/'scripts/native'/name),'Bridge drift')
    check(dict(file=prep['manifest'],sha256=prep['manifest_sha256']));manifest=json.loads((WS/prep['manifest']).read_text());selected=[]
    for suffix in ['source/cobject.h','source/cobject.cpp','source/cresobject.h','source/cresobject.cpp']:
        rows=[r for r in manifest if r['file'].endswith('/'+suffix)];require(len(rows)==1,'Generated common-object provider')
        for row in rows:check(row);check(dict(file=row['input'],sha256=row['input_sha256']))
        selected+=rows
    native=load('client455-resource-object-native')
    require(native['script_sha256']==sha(WS/'scripts/probe_client455_resource_object.py') and native['builder_sha256']==sha(WS/'scripts/client455_own_probe.py') and
            native['reference_sha256']==sha(WS/'inventory/client455-resource-object-reference.json') and native['normal_link_sha256']==link_hash,'Native provenance')
    for key in ['source','exe','map','console','output']:check(native[key])
    for row in native['inputs']:check(row)
    require({Path(r['file']).name:r['sha256'] for r in native['inputs']}=={Path(r['file']).name:r['sha256'] for r in ref['fixtures']},'Oracle copy drift')
    require(native['natural_exit']==0 and native['architecture']=='x86' and native['native']==json.loads((WS/native['output']['file']).read_text()),'Actual source execution')
    result=native['native'];require(result['status']=='PASS' and result['CObject_size']==80 and result['CResObject_size']==584 and result['named_offsets']==28 and
        result['whole_record_oracles']==2 and result['flag_cases']==160 and result['effect_retained_cases']==20 and result['effect_cleared_cases']==140 and result['receive_reset_cases']==48,'Actual source coverage')
    require(result['real_timeGetTime'] and result['virtual_base_clear'] and result['real_effect_clear_provider'] and not result['live_effect_cache_loaded'] and
            not result['actual_item_wrapper_binding'] and not result['full_resource_methods'] and not result['full_client'],'Acceptance boundary')
    for mapping in [(WS/native['map']['file']).read_text(),(WS/link['map']['file']).read_text()]:
        for symbol,provider in [('??0CObject@@QAE@ABV0@@Z','cobject.obj'),('??0CResObject@@QAE@ABV0@@Z','cresobject.obj'),
                               ('?Enable@CResObject','cresobject.obj'),('?Disable@CResObject','cresobject.obj'),('SetDisapearTimeMagicEffect','effectcore.obj')]:
            require(re.search(re.escape(symbol)+r'[^\r\n]*'+re.escape(provider),mapping),'Actual source provider missing '+symbol)
    fresh_names=['client455-normal-build','client455-normal-consumers','client455-normal-preparation','client455-own-entry','client455-startup-audit',
        'client455-startup-native','client455-ui-startup-native','client455-hotbar-native','client455-storage-native','client455-account-native',
        'client455-rvp-actor-native','client455-rvp-actor-visual','client455-world-visual','client455-item-payloads-native']
    fresh={name:sha(WS/'inventory'/(name+'.json')) for name in fresh_names}
    for name in ['client455-hotbar-native','client455-account-native','client455-rvp-actor-native']:
        report=load(name);require(report['normal_link_sha256']==link_hash and report['natural_exit']==0 and report['native']['status']=='PASS','Affected runtime '+name)
        for field in ['exe','map','output']:check(report[field])
        require(report['native']==json.loads((WS/report['output']['file']).read_text()),'Affected runtime result drift')
        if name!='client455-account-native':check(report['console'])
    storage=load('client455-storage-native');require(storage['normal_link_sha256']==link_hash and all(r['natural_exit']==0 and r['native']['registered']==17 for r in storage['runs']),'Actual storage regression')
    for field in ['source','exe','map']:check(storage[field])
    for run in storage['runs']:
        for field in ['exe','fixture','console']:check(run[field])
        require(json.loads((WS/run['console']['file']).read_text())==run['native'],'Actual storage console drift')
    require(load('client455-hotbar-native')['native']['actual_packets']==7 and not load('client455-account-native')['authentication_performed'],'Hotbar/account scope')
    actor=load('client455-rvp-actor-native');visual=load('client455-rvp-actor-visual')
    require(actor['native']['actors']==12 and actor['native']['memory_before']==actor['native']['memory_after'] and actor['inputs_unchanged'] and
            visual['native_sha256']==fresh['client455-rvp-actor-native'] and visual['manually_reviewed'] and len(visual['frames'])==9,'Actor/FX GPU regression')
    check(visual['sheet'])
    for row in visual['frames']:check(dict(file=row['preview'],sha256=row['preview_sha256']))
    shader=load('client455-shaders-reference');world_visual=load('client455-world-visual');require(world_visual['manually_reviewed'] and len(world_visual['frames'])==6,'World visual review')
    for race in ['bellato','cora','accretia']:
        name='client455-world-'+race+'-native';report=load(name);fresh[name]=sha(WS/'inventory'/(name+'.json'))
        require(report['normal_link_sha256']==link_hash and report['script_sha256']==sha(WS/'scripts/probe_client455_world.py') and
                report['natural_exit']==0 and report['native']['status']=='PASS' and report['native']['memory_before']==report['native']['memory_after'],'Real world/reload regression')
        for field in ['exe','map','console','output']:check(report[field])
        for frame in report['frames']:check(frame);check(dict(file=frame['preview'],sha256=frame['preview_sha256']))
        inputs={Path(r['file']).name:r for r in report['inputs']}
        for row in shader['programs']:
            actual=inputs[row['name']+'.sho'];check(actual);require(actual['sha256']==row['sha256'],'Required Character shader staging')
        for frame in world_visual['frames']:
            if frame['race']==race:require(frame['native_sha256']==fresh[name],'Stale world view')
    payload=load('client455-item-payloads-native')
    require(payload['normal_link_sha256']==link_hash and payload['script_sha256']==sha(WS/'scripts/probe_client455_item_payloads.py') and
            payload['edf_source_sha256']==sha(WS/'scripts/native/client455_language.cpp') and sha(WS/payload['library'])==payload['library_sha256'],'Renewed payload dependencies')
    for row in payload['sources']+payload['objects']+[payload['edf_dependency'],payload['build_log']]:check(row)
    for run in payload['runs']:
        require(run['natural_exit']==0 and run['native']['status']=='PASS','Renewed source payload/SF regression')
        for field in ['exe','map','console','output']:check(run[field])
    require(len(payload['runs'])==4 and payload['runs'][0]['native']['fresh_payloads']==575 and payload['runs'][2]['native']['real_SF_payloads']==1447,'Renewed source payload scope')
    early=load('client455-startup-native');ui=load('client455-ui-startup-native')
    require(early['normal_link_sha256']==ui['normal_link_sha256']==link_hash and not early['debugger_exit'] and not ui['debugger_exit'] and
            early['sound_return']==1 and ui['completed_existing_client_create'] and ui['summary']['final_checkpoint_reached'] and
            any(r['name']=='after_client_create' and r['eax']==1 for r in ui['markers']),'Exact new PE Create')
    check(early['events']);check(ui['events'])
    require(all(r['first_chance']==1 for r in ui['exceptions']),'Unhandled startup exception')
    engine=load('client455-startup-engine-build');require(sha(WS/engine['library'])==engine['library_sha256']=='9caa283a6bf8a2fa1c9a05251b6cad451296bb03bda8a1860c22a872e88fe769','Unexpected engine change')
    report=dict(status='PARTIAL',scope='Ordinary common-object80/resource584 ctor-copy-name-flags-effect lifecycle;actual itemwrapper/owners still open',
        script_sha256=sha(Path(__file__)),reference_sha256=sha(WS/'inventory/client455-resource-object-reference.json'),native_sha256=sha(WS/'inventory/client455-resource-object-native.json'),
        session=record(session_path),generated_providers=selected,normal_link_sha256=link_hash,normal_executable=link['executable'],
        engine_unchanged_sha256=engine['library_sha256'],selected_functions=23,assembly_instructions=765,whole_record_oracles=2,flag_cases=160,
        fresh_evidence=fresh,viewed_actor_frames=9,viewed_world_frames=6,renewed_payloads575_SF1447='PASS_BOUNDED',
        fixture_correction='Initial world-bellato run lacked Character shaders;added existing verified shader inputs to lab only;production unchanged by this fix',
        earlier_gates='086ordinary and088/089source gates historical after new normal/source-dependency reports;their static references retained',
        gaps=ref['gaps'],unchanged_159k_suites_rerun=False,input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-resource-object-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PARTIAL:ordinary CObject80/CResObject584 ctor-copy/160flags;hotbar/account/storage/actorFX/3worlds/exactPECreate1/sourcepayload regression PASS;M9 OPEN')
if __name__=='__main__':main()
