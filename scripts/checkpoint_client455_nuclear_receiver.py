"""Gate ordinary Nuclear integration; full client455/M9 remains OPEN."""
import hashlib,json,re,struct,subprocess
from pathlib import Path
from audit_client455_item_payloads import record
from audit_client455_own_entry import symbol
from audit_client455_tutorial_integration import rtti
from build_client455_x87_math import read_va
from checkpoint_client455_item_icon_metadata import checked_native
from checkpoint_client455_rvp_effects import check,load,require,sha
from client455_normal_link_evidence import validate_normal_link
from compare_client_binaries import WS,pe


def main():
    ref=load('client455-nuclear-receiver-reference');require(ref['script_sha256']==sha(WS/'scripts/audit_client455_nuclear_receiver.py') and (ref['selected_functions'],ref['full_assembly_functions'],ref['instructions'],ref['new_assembly_functions'],ref['new_instructions'])==(44,42,2473,18,1354),'Selected reference coverage/provenance')
    for row in [ref['raw'],ref['session']]+ref['cached_reference']:check(row)
    state=json.loads((WS/ref['session']['file']).read_text());require(state['closed']['success'] and state['closed']['saved'] and state['after']['count']==0,'Owned IDA close/save/list0')
    pins=json.loads((WS/'config/client-target.json').read_text())
    for folder,key,pin in zip(['current','reference-backup'],['behavior_reference','secondary_reference'],ref['references']):
        image_path=WS/f'work/client-reference/{folder}/RF_Online.bin';image=image_path.read_bytes();require(sha(image_path)==pins[key]['sha256']==pin['sha256'] and pe(image)['architecture']=='x86','Pinned455/x86')
        for row in pin['ranges']+pin['tails']+[pin['inventory_vtable']]:require(hashlib.sha256(read_va(image,0x400000+int(row['rva'],16),row['bytes'])).hexdigest()==row['sha256'],'Pinned body/EH/vtable')
        for row in pin['decoded_calls']:
            at=0x400000+int(row['rva'],16);data=read_va(image,at,5);require(data[0]==0xe8 and at+5+struct.unpack('<i',data[1:])[0]==0x400000+int(row['target_rva'],16),'Pinned decoded CALL')
    link=load('client455-normal-link');require(validate_normal_link(link)=='PASS' and link['client_objects']==182 and not link['unique_unresolved'],'Normal build/link');link_hash=sha(WS/'inventory/client455-normal-link.json');prep,build=load('client455-normal-preparation'),load('client455-normal-build')
    require(prep['script_sha256']==sha(WS/'scripts/prepare_client455_normal.py') and prep['nuclear_receiver_port_sha256']==sha(WS/'scripts/client455_nuclear_receiver_port.py'),'Current preparation/port')
    require(not build['build_exit'] and not build['errors'] and build['canonical_kernel_objects']==20 and build['source_manifest_sha256']==prep['manifest_sha256'] and len(list((WS/'work/client455-port/normal/build/RFClient455Facade.dir/Release').glob('*.obj')))==69,'182client/20kernel/69facade')
    names=['client455_nuclear_receiver.h','client455_nuclear_receiver.cpp','client455_player_use.h','client455_nuclear_registry.h','client455_nuclear_registry.cpp','client455_board_hover.h','client455_board_hover.cpp','client455_nuclear_wire.h','client455_nuclear_wire.cpp'];sources=[record(WS/'scripts/native'/name) for name in names]
    for row in sources:require(prep['record_inputs'][Path(row['file']).name]==row['sha256'],'Prepared source bytes')
    check(dict(file=prep['manifest'],sha256=prep['manifest_sha256']));check(dict(file=build['log'],sha256=build['log_sha256']));manifest=json.loads((WS/prep['manifest']).read_text());providers=[]
    for suffix in ['source/mainapp.h','source/mainapp.cpp','source/gameprogress/cgp_maingame.h','source/gameprogress/cgp_maingame.cpp','source/character/player/cplayer.h','source/network/cnetworkmgr.cpp','source/network/cnetworkmgr.h','source/gameobject/board/common/cboard.cpp','source/gameobject/board/common/cboardmanager.cpp','source/gameobject/board/itemboard/cinventoryboard.cpp','generated/client455_nuclear_receiver.cpp','generated/client455_nuclear_registry.cpp','generated/client455_nuclear_wire.cpp','generated/client455_board_hover.cpp']:
        rows=[x for x in manifest if x['file'].lower().endswith('/'+suffix)];require(len(rows)==1,'Generated actual owner '+suffix)
        for row in rows:check(row);check(dict(file=row['input'],sha256=row['input_sha256']))
        providers+=rows
    require('RF455NuclearContainer m_nuclear455;' not in (WS/'work/client455-port/normal/source/mainapp.h').read_text(),'MainApp static owner removed')
    mapping=(WS/link['map']['file']).read_text();own=(WS/link['executable']['file']).read_bytes();base=pe(own)['image_base'];starts=sorted({int(x,16) for x in re.findall(r'^\s+0001:[0-9a-fA-F]{8}\s+\S+\s+([0-9a-fA-F]{8})\b',mapping,re.M)});dumpbin=Path(load('msvc-verification')['compiler_path'].splitlines()[0]).with_name('dumpbin.exe');decoded=[]
    def name(prefix):
        values=re.findall(r'^\s+0001:[0-9a-fA-F]{8}\s+('+re.escape(prefix)+r'\S*)\s+[0-9a-fA-F]{8}\b',mapping,re.M);require(len(values)==1,'Unique own symbol '+prefix);return values[0]
    def calls(prefix):
        full=name(prefix);begin=symbol(mapping,full);end=next(x for x in starts if x>begin);run=subprocess.run([str(dumpbin),'/DISASM:BYTES',f'/RANGE:0x{begin:x},0x{end:x}',str(WS/link['executable']['file'])],capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW);require(not run.returncode,'Own disassembly')
        file=WS/f'artifacts/client455-progress/receiver116-own-{len(decoded)}.txt';file.write_bytes(run.stdout);edges=[]
        for line in run.stdout.decode(errors='replace').splitlines():
            match=re.match(r'^\s+([0-9A-F]{8}): ((?:[0-9A-F]{2} )+)\s+(\w+)\s*(.*?)\s*$',line)
            if not match:continue
            at=int(match[1],16);data=bytes.fromhex(match[2])
            if at>=end:continue
            require(data==read_va(own,at,len(data)),'Own decoded bytes')
            if match[3] in ['call','jmp'] and len(data)==5 and data[0] in [0xe8,0xe9]:edges.append(dict(rva=hex(at-base),target_rva=hex(at+5+struct.unpack('<i',data[1:])[0]-base)))
        decoded.append(dict(function=full,rva=hex(begin-base),disassembly=record(file),edges=edges));return edges
    def edge(caller,target):
        edges=calls(caller);expected=hex(symbol(mapping,name(target))-base);require(any(x['target_rva']==expected for x in edges),'Ordinary linked edge '+caller+'→'+target)
    edge('?Init@CGP_MainGame@@','?RF455_BindNuclearContainer@@');edge('?Destroy@CGP_MainGame@@','?ReleaseNuclear455@CGP_MainGame@@');edge('??_GCGP_MainGame@@','?ReleaseNuclear455@CGP_MainGame@@');edge('?SetHoverObject@CBoardManager@@','?RF455_RequireHoverCancellation@@');edge('?Render@CGP_MainGame@@','?FrameMove@RF455NuclearContainer@@')
    calls('?AnalysisServerPacket@CNetworkMgr@@');calls('?AnalysisServerPacket@CNetMsgProcessor_Nuclear@@');calls('?UI_UseResult@CObjectBoard@@')
    table=symbol(mapping,'??_7CNetMsgProcessor_Nuclear@@6B@');analysis=symbol(mapping,name('?AnalysisServerPacket@CNetMsgProcessor_Nuclear@@'));require(struct.unpack('<I',read_va(own,table+4,4))[0]==analysis and rtti(own,table)['class_name']=='CNetMsgProcessor_Nuclear','Actual own Nuclear vtable slot4')
    retained=[name(prefix) for prefix in ['?Launch@RF455NuclearContainer@@','?Impact@RF455NuclearContainer@@','?NotifyRace@RF455NuclearContainer@@','?Position@RF455NuclearContainer@@','?SetNuclearMarker455@CGUIMiniMapWindow@@','?RF455_ReadNuclearPayload@@']]
    native_groups=[('nuclear-receiver',4,101),('nuclear-registry',5,109),('nuclear-minimap',6,702),('message-dispatch',5,83)];review=load('client455-nuclear-receiver-visual-review');require(review['reviewed'] and review['reviewed_frames']==20 and review['normal_link_sha256']==link_hash and review['script_sha256']==sha(WS/'scripts/review_client455_nuclear_receiver.py'),'Viewed current20 frames');baselines=[]
    for group,frames,count in native_groups:
        native=checked_native('client455-'+group+'-native',link_hash);require(native['native']['checks']==count and len(native['frames'])==frames and native['source']['sha256']==sha(WS/'scripts/native'/('client455_'+group.replace('-','_')+'_probe.cpp')) and native['script_sha256']==sha(WS/'scripts'/('probe_client455_'+group.replace('-','_')+'.py')) and native['builder_sha256']==sha(WS/'scripts/client455_own_probe.py'),'Current native provenance '+group)
        viewed=next(x for x in review['groups'] if x['name']==group);require(viewed['frames']==native['frames'] and viewed['reviewed_frames']==frames,'Exact viewed captures');check(viewed['native']);check(viewed['sheet']);check(native['source']);check(native['console'])
        for row in native['inputs']+native['frames']:check(row)
        for row in native['frames']:check(row['preview'])
        if group in ['nuclear-minimap','message-dispatch']:
            previous=WS/f'artifacts/client455-progress/client455-{group}-native-before116.json';older={Path(x['file']).name:x for x in json.loads(previous.read_text())['frames']}
            for row in native['frames']:check(older[Path(row['file']).name]);require(row['sha256']==older[Path(row['file']).name]['sha256'],'Prior115 marker/message pixels preserved')
            baselines.append(record(previous))
    receive=load('client455-nuclear-receiver-native')['native']
    for key in ['ordinary_factory_and_DataAnalysis','all_nine_opcodes','real_MainGame_registry_owner','original_serial_plain6_encrypted19_CNG','real_encrypted_receive_ring','hover_backup_preserves_operation','actual_type33_inventory_use_callback','player_use_only_field4_clear','actual_registry_lookup_to_MiniMap','guard_blocked_errors_repeat','real_BSP_effects_Miles']:require(receive[key],'Actual receiver behavior '+key)
    require(receive['warnings']==20 and not receive['pixels'][-1] and all(not receive[x] for x in ['full_socket_auth','full_inventory_use','full_stage_lifecycle','full_world_effects','full_client']),'Explicit limits retained')
    registry=load('client455-nuclear-registry-native')['native'];require(registry['actual_stage_registry'] and registry['shared_process_clock_and_sorted_order'] and registry['clock_survives_clear'] and registry['warnings']==20,'Actual stage registry/clock/texture warning limit')
    aiming=checked_native('client455-nuclear-aiming-native',link_hash);require(aiming['native']['checks']==30 and aiming['native']['actual_MainGame_owner'] and aiming['native']['scoped_memory_balanced'] and aiming['source']['sha256']==sha(WS/'scripts/native/client455_nuclear_aiming_probe.cpp') and aiming['script_sha256']==sha(WS/'scripts/probe_client455_nuclear_aiming.py'),'Actual stage aiming regression');check(aiming['source']);check(aiming['console'])
    for row in aiming['inputs']:check(row)
    early,ui=load('client455-startup-native'),load('client455-ui-startup-native');require(early['normal_link_sha256']==ui['normal_link_sha256']==link_hash and not early['debugger_exit'] and early['sound_return']==1 and not ui['debugger_exit'] and ui['completed_existing_client_create'] and any(x['name']=='after_client_create' and x['eax']==1 for x in ui['markers']) and all(x['first_chance']==1 for x in ui['exceptions']),'Exact own PE Create1');check(early['events']);check(ui['events'])
    engine=load('client455-startup-engine-build');require(sha(WS/engine['library'])==engine['library_sha256']=='546a7529b51139e856b1a108fcad7849c14b2d00563b7abbfdcc8db10026fa5a','Unchanged engine67');check(engine['baseline_library'])
    old_file=WS/'artifacts/client455-progress/client455-nuclear-registry-checkpoint-before116.json';old=json.loads(old_file.read_text());historical=old['historical_not_rerun']
    for row in historical.values():check(row)
    fresh=['nuclear-receiver-reference','nuclear-receiver-native','nuclear-receiver-visual-review','nuclear-registry-native','nuclear-aiming-native','nuclear-minimap-native','message-dispatch-native','normal-preparation','normal-build','normal-consumers','normal-link','own-entry','startup-audit','startup-native','ui-startup-native']
    report=dict(status='PARTIAL',scope=ref['scope'],script_sha256=sha(Path(__file__)),sources=sources,generated_providers=providers,normal_link_sha256=link_hash,normal_executable=link['executable'],own_decoded_calls=decoded,own_receiver_vtable=dict(rva=hex(table-base),bytes=8,sha256=hashlib.sha256(read_va(own,table,8)).hexdigest()),retained_normal_consumers=retained,receiver_checks=101,registry_checks=109,aim_checks=30,marker_checks=702,message_checks=83,viewed_GPU_frames=20,byte_equal_prior_marker_message_frames=11,baselines=baselines,ordinary_Nuclear_factory_receiver=True,MainGame_registry_owner=True,selected_type33_item_use=True,full_socket_auth=False,full_inventory_use=False,full_stage_lifecycle=False,full_world_effects=False,R3T_release_warnings_per_nuclear_lab=20,complete_texture_lifetime=False,previous115_gate=record(old_file),previous115_runtime_gate='HISTORICAL',historical_not_rerun=historical,fresh_evidence={name:record(WS/f'inventory/client455-{name}.json') for name in fresh},engine_unchanged=engine['library_sha256'],unchanged_bulk_suites_rerun=False,gaps=ref['gaps']+['Worldgeometry588 data producer/loader,full world frame/trajectory/quake/light/quality and all prior client-acceptance gaps remain'],input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-nuclear-receiver-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n');print('PARTIAL:ordinary Nuclear group60/all9/source-stage owner/type33use;101/109/30/702/83;20viewedGPU/11byteequal/Create1;fullsocket/auth/inventory/stage/world/texturelifetime/M9OPEN')


if __name__=='__main__':main()
