"""Gate selected actual nuclear registry; full455/M9 remains unproven/open."""
import hashlib,json,re,struct,subprocess
from pathlib import Path
from audit_client455_item_payloads import record
from audit_client455_own_entry import symbol
from build_client455_x87_math import read_va
from checkpoint_client455_item_icon_metadata import checked_native
from checkpoint_client455_rvp_effects import check,load,require,sha
from client455_normal_link_evidence import validate_normal_link
from compare_client_binaries import WS,pe


def main():
    ref=load('client455-nuclear-registry-reference');require(ref['status']=='CONFIRMED_SELECTED' and ref['script_sha256']==sha(WS/'scripts/audit_client455_nuclear_registry.py') and (ref['selected_functions'],ref['full_assembly_functions'],ref['instructions'],ref['new_assembly_functions'],ref['new_instructions'])==(34,31,1394,30,1339),'Reference selected coverage/provenance')
    for row in [ref['raw'],ref['session'],ref['magic_manifest'],ref['sound_manifest']]+ref['cached_reference']:check(row)
    for row in ref['resource_scripts']:
        check(row['archive']);check(row['copy']);require((WS/row['copy']['file']).stat().st_size==row['bytes'],'Saved actual resource script')
    state=json.loads((WS/ref['session']['file']).read_text());require(state['closed']['success'] and state['closed']['saved'] and state['after']['count']==0,'Owned IDA close/save/list0')
    pins=json.loads((WS/'config/client-target.json').read_text())
    for folder,key,pin in zip(['current','reference-backup'],['behavior_reference','secondary_reference'],ref['references']):
        file=WS/f'work/client-reference/{folder}/RF_Online.bin';image=file.read_bytes();require(sha(file)==pins[key]['sha256']==pin['sha256'] and pe(image)['architecture']=='x86','Actual pinned455')
        for row in pin['ranges']+pin['tails']+[pin['unknown_race_empty_literal']]:require(hashlib.sha256(read_va(image,0x400000+int(row['rva'],16),row['bytes'])).hexdigest()==row['sha256'],'Pinned code/EH/literal')
        for row in pin['decoded_calls']+pin['stage_calls']:
            at=0x400000+int(row['rva'],16);data=read_va(image,at,5);require(data[0]==0xe8 and at+5+struct.unpack('<i',data[1:])[0]==0x400000+int(row['target_rva'],16),'Decoded pinned CALL')
    link=load('client455-normal-link');require(validate_normal_link(link)=='PASS' and link['client_objects']==182 and not link['unique_unresolved'],'Normal build/link');link_hash=sha(WS/'inventory/client455-normal-link.json');prep,build=load('client455-normal-preparation'),load('client455-normal-build')
    require(prep['script_sha256']==sha(WS/'scripts/prepare_client455_normal.py') and prep['nuclear_registry_port_sha256']==sha(WS/'scripts/client455_nuclear_registry_port.py'),'Prepared port provenance')
    require(not build['build_exit'] and not build['errors'] and build['canonical_kernel_objects']==20 and build['source_manifest_sha256']==prep['manifest_sha256'] and len(list((WS/'work/client455-port/normal/build/RFClient455Facade.dir/Release').glob('*.obj')))==67,'182client/20kernel/67facade build')
    sources=[record(WS/'scripts/native'/name) for name in ['client455_nuclear_registry.h','client455_nuclear_registry.cpp','client455_nuclear_aiming.h']]
    for row in sources:require(prep['record_inputs'][Path(row['file']).name]==row['sha256'],'Prepared source '+row['file'])
    check(dict(file=prep['manifest'],sha256=prep['manifest_sha256']));check(dict(file=build['log'],sha256=build['log_sha256']));manifest=json.loads((WS/prep['manifest']).read_text());providers=[]
    for suffix in ['source/mainapp.h','source/mainapp.cpp','source/gameprogress/cgp_maingame.cpp','generated/client455_nuclear_registry.cpp','include/client455_nuclear_registry.h']:
        rows=[x for x in manifest if x['file'].lower().endswith('/'+suffix)];require(len(rows)==1,'Generated actual owner '+suffix)
        for row in rows:check(row);check(dict(file=row['input'],sha256=row['input_sha256']))
        providers+=rows
    mapping=(WS/link['map']['file']).read_text();own=(WS/link['executable']['file']).read_bytes();base=pe(own)['image_base'];starts=sorted({int(x,16) for x in re.findall(r'^\s+0001:[0-9a-fA-F]{8}\s+\S+\s+([0-9a-fA-F]{8})\b',mapping,re.M)});dumpbin=Path(load('msvc-verification')['compiler_path'].splitlines()[0]).with_name('dumpbin.exe');decoded=[]
    def calls(name):
        begin=symbol(mapping,name);end=next(x for x in starts if x>begin);out=subprocess.run([str(dumpbin),'/DISASM:BYTES',f'/RANGE:0x{begin:x},0x{end:x}',str(WS/link['executable']['file'])],capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW);require(not out.returncode,'Own decode')
        file=WS/f'artifacts/client455-progress/registry115-own-{len(decoded)}.txt';file.write_bytes(out.stdout);edges=[]
        for line in out.stdout.decode(errors='replace').splitlines():
            match=re.match(r'^\s+([0-9A-F]{8}): ((?:[0-9A-F]{2} )+)\s+(\w+)\s*(.*?)\s*$',line)
            if not match:continue
            at=int(match[1],16);data=bytes.fromhex(match[2])
            if at>=end:continue
            require(data==read_va(own,at,len(data)),'Own decoded bytes')
            if match[3] in ['call','jmp'] and len(data)==5 and data[0] in [0xe8,0xe9]:edges.append(dict(rva=hex(at-base),target_rva=hex(at+5+struct.unpack('<i',data[1:])[0]-base)))
        decoded.append(dict(function=name,rva=hex(begin-base),disassembly=record(file),edges=edges));return edges
    render=calls('?Render@CGP_MainGame@@MAEJXZ');target=hex(symbol(mapping,'?FrameMove@RF455NuclearContainer@@QAEXXZ')-base);require(any(x['target_rva']==target for x in render),'Ordinary late MainGame render calls registry frame')
    destroy=calls('?Destroy@CMainApp@@QAEHXZ');target=hex(symbol(mapping,'?ClearAll@RF455NuclearContainer@@QAEHXZ')-base);require(any(x['target_rva']==target for x in destroy),'Ordinary shutdown clears records')
    calls('?FrameMove@RF455NuclearContainer@@QAEXXZ')
    require('?Launch@RF455NuclearContainer@@' not in mapping and '?NotifyRace@RF455NuclearContainer@@' not in mapping,'Actual receiver/record production callers still absent;helpers stripped')
    run=checked_native('client455-nuclear-registry-native',link_hash);require(run['source']['sha256']==sha(WS/'scripts/native/client455_nuclear_registry_probe.cpp') and run['script_sha256']==sha(WS/'scripts/probe_client455_nuclear_registry.py') and run['builder_sha256']==sha(WS/'scripts/client455_own_probe.py') and run['runtime_inputs_sha256']==sha(WS/'scripts/client455_runtime_inputs.py'),'Current registry native provenance')
    for row in run['inputs']+[run['source'],run['console'],run['world_input_manifest'],run['archive_input_manifest']]:check(row)
    result=run['native'];require((result['checks'],result['warnings'],result['record_bytes'],result['impact_tracks'],result['GPU_frames'],result['pixels'][-2:])==(109,20,32,15,5,[0,0]),'Selected native domain and explicit texture warning limit')
    for name in ['actual_MainApp_registry','unknown_DWORD12_untouched','unsigned_WORD_keys','real_radar_tag2_and_aiming_tag1','real_launch_impact_scripts','target_reset_detaches_launch_impact','real_C15_C17_and_literal','shared_process_clock_and_sorted_order','clock_survives_clear']:require(result[name],'Native behavior '+name)
    for name in ['ordinary_receiver','full_stage_lifecycle','full_world_effects','full_client']:require(not result[name],'No whole feature acceptance')
    aim=checked_native('client455-nuclear-aiming-native',link_hash);require(aim['native']['checks']==29 and aim['native']['scoped_memory_balanced'] and aim['source']['sha256']==sha(WS/'scripts/native/client455_nuclear_aiming_probe.cpp') and aim['script_sha256']==sha(WS/'scripts/probe_client455_nuclear_aiming.py'),'Existing aim regression');check(aim['source']);check(aim['console'])
    for row in aim['inputs']:check(row)
    native_groups=[('nuclear-registry',5,109),('nuclear-minimap',6,702),('message-dispatch',5,83)];review=load('client455-nuclear-registry-visual-review');require(review['reviewed'] and review['reviewed_frames']==16 and review['normal_link_sha256']==link_hash and review['script_sha256']==sha(WS/'scripts/review_client455_nuclear_registry.py'),'Viewed current registry/marker/message captures');baseline_frames=[]
    for name,frames,count in native_groups:
        current=checked_native('client455-'+name+'-native',link_hash);require(current['native']['checks']==count and len(current['frames'])==frames,'Current selected native '+name);group=next(x for x in review['groups'] if x['name']==name);require(group['frames']==current['frames'] and group['reviewed_frames']==frames,'Exact viewed frames');check(group['native']);check(group['sheet'])
        for row in current['inputs']+current['frames']:check(row)
        for row in current['frames']:check(row['preview'])
        if name!='nuclear-registry':
            previous_file=WS/f'artifacts/client455-progress/client455-{name}-native-before115.json';previous=json.loads(previous_file.read_text());older={Path(x['file']).name:x for x in previous['frames']}
            for row in current['frames']:check(older[Path(row['file']).name]);require(row['sha256']==older[Path(row['file']).name]['sha256'],'Prior114 pixels unchanged '+name)
            baseline_frames.append(record(previous_file))
    early,ui=load('client455-startup-native'),load('client455-ui-startup-native');require(early['normal_link_sha256']==ui['normal_link_sha256']==link_hash and not early['debugger_exit'] and early['sound_return']==1 and not ui['debugger_exit'] and ui['completed_existing_client_create'] and any(x['name']=='after_client_create' and x['eax']==1 for x in ui['markers']) and all(x['first_chance']==1 for x in ui['exceptions']),'Exact own PE Create1');check(early['events']);check(ui['events'])
    engine=load('client455-startup-engine-build');require(sha(WS/engine['library'])==engine['library_sha256']=='546a7529b51139e856b1a108fcad7849c14b2d00563b7abbfdcc8db10026fa5a','Unchanged engine67');check(engine['baseline_library'])
    previous=WS/'artifacts/client455-progress/client455-nuclear-minimap-checkpoint-before115.json';old_gate=json.loads(previous.read_text());historical=old_gate['historical_not_rerun'];historical.update({name:record(WS/f'artifacts/client455-progress/client455-{name}-before115.json') for name in ['minimap-opacity-native','nuclear-minimap-reference']})
    for name,row in list(historical.items()):
        if (WS/row['file']).is_file() and sha(WS/row['file'])==row['sha256']:continue
        archived=WS/f'artifacts/client455-progress/client455-{name}-historical-before115.json';require(archived.is_file() and sha(archived)==row['sha256'],'Exact archived historical evidence '+name);historical[name]=record(archived)
    for row in historical.values():check(row)
    fresh=['nuclear-registry-reference','nuclear-registry-native','nuclear-registry-visual-review','nuclear-aiming-native','nuclear-minimap-native','message-dispatch-native','normal-preparation','normal-build','normal-consumers','normal-link','own-entry','startup-audit','startup-native','ui-startup-native']
    report=dict(status='PARTIAL',scope=ref['scope'],script_sha256=sha(Path(__file__)),sources=sources,generated_providers=providers,normal_link_sha256=link_hash,normal_executable=link['executable'],own_decoded_calls=decoded,native_registry_checks=109,aim_regression_checks=29,marker_regression_checks=702,message_regression_checks=83,viewed_GPU_frames=16,byte_equal_prior_marker_message_frames=11,baselines=baseline_frames,ordinary_registry_frame_and_shutdown=True,record_creation_FX_messages_in_fullobject_lab=True,ordinary_receiver=False,full_stage_lifecycle=False,full_world_effects=False,registry_R3T_release_warnings=20,complete_registry_texture_lifetime=False,previous114_gate=record(previous),previous114_runtime_gate='HISTORICAL',historical_not_rerun=historical,fresh_evidence={name:record(WS/f'inventory/client455-{name}.json') for name in fresh},derived_engine_unchanged=engine['library_sha256'],unchanged_bulk_suites_rerun=False,gaps=ref['gaps']+['Registry lab emits20 legacy R3T-release warnings during teardown;complete texture ownership/memory balance not accepted','All prior Character/action/movement/64bit status/fullminimap and client-acceptance gaps remain'],input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-nuclear-registry-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n');print('PARTIAL:record32/registry/sharedclock/tag2/launch/impact;native109/aim29/marker702/message83/16viewedGPU/11byteequal/Create1;ordinaryreceiver/stagelifecycle/world/texturelifetime/M9OPEN')


if __name__=='__main__':main()
