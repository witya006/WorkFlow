"""Gate actual marker UI ownership; registry/receiver/world producer stay open."""
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
    ref=load('client455-nuclear-minimap-reference');require(ref['script_sha256']==sha(WS/'scripts/audit_client455_nuclear_minimap.py') and (ref['selected_functions'],ref['full_assembly_functions'],ref['instructions'],ref['new_assembly_functions'],ref['new_instructions'])==(26,24,2594,19,2028),'Reference coverage/provenance')
    for row in [ref['raw'],ref['session'],ref['input_raw'],ref['input_session']]+ref['cached_reference']:check(row)
    state=json.loads((WS/ref['session']['file']).read_text());require(state['closed']['success'] and state['closed']['saved'] and state['after']['count']==0,'IDA cleanup')
    pins=json.loads((WS/'config/client-target.json').read_text())
    for folder,key,pin in zip(['current','reference-backup'],['behavior_reference','secondary_reference'],ref['references']):
        file=WS/f'work/client-reference/{folder}/RF_Online.bin';image=file.read_bytes();require(sha(file)==pins[key]['sha256']==pin['sha256'] and pe(image)['architecture']=='x86','Actual455 pin')
        for row in pin['ranges']+pin['tails']+[x['vtable'] for x in pin['identities']]:require(hashlib.sha256(read_va(image,0x400000+int(row['rva'],16),row['bytes'])).hexdigest()==row['sha256'],'Pinned body/EH/vtable')
        for row in pin['decoded_calls']:
            at=0x400000+int(row['rva'],16);code=read_va(image,at,5);require(code[0]==0xe8 and at+5+struct.unpack('<i',code[1:])[0]==0x400000+int(row['target_rva'],16),'Pinned direct edge')
    link=load('client455-normal-link');link_hash=sha(WS/'inventory/client455-normal-link.json');require(validate_normal_link(link)=='PASS' and link['client_objects']==182 and not link['unique_unresolved'],'Ordinary build/link')
    prep,build=load('client455-normal-preparation'),load('client455-normal-build');require(prep['script_sha256']==sha(WS/'scripts/prepare_client455_normal.py') and prep['nuclear_minimap_port_sha256']==sha(WS/'scripts/client455_nuclear_minimap_port.py'),'Current port provenance')
    require(not build['build_exit'] and not build['errors'] and build['canonical_kernel_objects']==20 and build['source_manifest_sha256']==prep['manifest_sha256'] and len(list((WS/'work/client455-port/normal/build/RFClient455Facade.dir/Release').glob('*.obj')))==66,'182/20/66 build')
    sources=[record(WS/'scripts/native'/name) for name in ['client455_nuclear_minimap.h','client455_nuclear_minimap.cpp','client455_image_text.h']]
    for row in sources:require(prep['record_inputs'][Path(row['file']).name]==row['sha256'],'Prepared source bytes')
    check(dict(file=prep['manifest'],sha256=prep['manifest_sha256']));check(dict(file=build['log'],sha256=build['log_sha256']));manifest=json.loads((WS/prep['manifest']).read_text());providers=[]
    for suffix in ['source/userinterface/gamewindow/etcwin/guiminimapwindow.h','source/userinterface/gamewindow/etcwin/guiminimapwindow.cpp','generated/client455_nuclear_minimap.cpp','include/client455_nuclear_minimap.h','include/client455_image_text.h']:
        rows=[x for x in manifest if x['file'].lower().endswith('/'+suffix)];require(len(rows)==1,'Generated actual owner '+suffix)
        for row in rows:check(row);check(dict(file=row['input'],sha256=row['input_sha256']))
        providers+=rows
    mapping=(WS/link['map']['file']).read_text();own=(WS/link['executable']['file']).read_bytes();base=pe(own)['image_base'];starts=sorted({int(x,16) for x in re.findall(r'^\s+0001:[0-9a-fA-F]{8}\s+\S+\s+([0-9a-fA-F]{8})\b',mapping,re.M)});dumpbin=Path(load('msvc-verification')['compiler_path'].splitlines()[0]).with_name('dumpbin.exe');decoded=[]
    def calls(name):
        begin=symbol(mapping,name);end=next(x for x in starts if x>begin);out=subprocess.run([str(dumpbin),'/DISASM:BYTES',f'/RANGE:0x{begin:x},0x{end:x}',str(WS/link['executable']['file'])],capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW);require(not out.returncode,'Own decode')
        file=WS/f'artifacts/client455-progress/minimap114-own-{len(decoded)}.txt';file.write_bytes(out.stdout);edges=[]
        for line in out.stdout.decode(errors='replace').splitlines():
            match=re.match(r'^\s+([0-9A-F]{8}): ((?:[0-9A-F]{2} )+)\s+(\w+)\s*(.*?)\s*$',line)
            if not match:continue
            at=int(match[1],16);data=bytes.fromhex(match[2])
            if at>=end:continue
            require(data==read_va(own,at,len(data)),'Own decoded bytes')
            if match[3] in ['call','jmp'] and len(data)==5 and data[0] in [0xe8,0xe9]:edges.append(dict(rva=hex(at-base),target_rva=hex(at+5+struct.unpack('<i',data[1:])[0]-base)))
        decoded.append(dict(function=name,rva=hex(begin-base),disassembly=record(file),edges=edges));return edges
    init=calls('?Init@CGUIMiniMapWindow@@UAEXXZ');target=hex(symbol(mapping,'?InitNuclearMarkers455@CGUIMiniMapWindow@@AAEXXZ')-base);require(any(x['target_rva']==target for x in init),'Ordinary MiniMap Init registers markers')
    bound=calls('?SetMapBound@CGUIMiniMapWindow@@QAEXAAUtagRECT@@@Z');target=hex(symbol(mapping,'?SetMapBound455@CGUINuclearBomb455@@QAEXABUtagRECT@@@Z')-base);require(any(x['target_rva']==target for x in bound),'Ordinary map bounds invoke marker bounds')
    calls('?Draw@CGUINuclearBomb455@@UAEHXZ');vtable=symbol(mapping,'??_7CGUINuclearBomb455@@6B@');draw=symbol(mapping,'?Draw@CGUINuclearBomb455@@UAEHXZ');own_slots=[i for i in range(0,192,4) if struct.unpack('<I',read_va(own,vtable+i,4))[0]==draw];require(len(own_slots)==1,'Actual own marker virtual Draw retained')
    require('?Display455@CGUINuclearBomb455@@' not in mapping and '?SetNuclearMapGeometry455@CGUIMiniMapWindow@@' not in mapping and '?SetNuclearMarker455@CGUIMiniMapWindow@@' not in mapping,'Registry/world/receiver callers still absent and UI helpers stripped')
    native=checked_native('client455-nuclear-minimap-native',link_hash);require(native['script_sha256']==sha(WS/'scripts/probe_client455_nuclear_minimap.py') and native['source']['sha256']==sha(WS/'scripts/native/client455_nuclear_minimap_probe.cpp') and native['builder_sha256']==sha(WS/'scripts/client455_own_probe.py'),'Native provenance');check(native['source']);check(native['console'])
    result=native['native'];require((result['checks'],result['draw_alpha_states'],result['GPU_frames'],result['icon_size'],result['first_changed_pixels'],result['warm_changed_pixels'])==(702,256,6,[24,24],566,2217),'Selected actual UI domain')
    for key in ['actual_MiniMap_three_owners','actual_bound_fanout','root_inputflag_and_child_propagation','typed_geometry_and_position_API','first_position_before_configure','real_sprite4_main5_frame43','real_imagefont7x9','alpha_after_ordinary_not_clipped_Draw','empty_draw_still_advances_alpha','missing_record_retains_UI','hide_preserves_child_state']:require(result[key],'Native selected behavior '+key)
    for key in ['registry_race_lookup','ordinary_geometry_world_producer','normal_receiver','full_minimap','full_client']:require(not result[key],'No unjustified whole feature acceptance')
    for row in native['inputs']+native['frames']:check(row)
    compatibility=native['header_compatibility_build'];require(not compatibility['executed'] and compatibility['source']['sha256']==sha(WS/'scripts/native/client455_linker_window_probe.cpp'),'Earlier Linker window header build compatibility,no runtime claim')
    for key in ['source','exe','map']:check(compatibility[key])
    for row in native['frames']:check(row['preview'])
    review=load('client455-nuclear-minimap-visual-review');require(review['reviewed'] and review['reviewed_frames']==6 and review['frames']==native['frames'] and review['native_sha256']==sha(WS/'inventory/client455-nuclear-minimap-native.json') and review['script_sha256']==sha(WS/'scripts/review_client455_nuclear_minimap.py'),'Viewed current6marker frames');check(review['sheet'])
    opacity=load('client455-minimap-opacity-native');require(opacity['normal_link_sha256']==link_hash and opacity['script_sha256']==sha(WS/'scripts/probe_client455_minimap_opacity.py') and opacity['generator_sha256']==prep['script_sha256'] and opacity['builder_sha256']==sha(WS/'scripts/client455_own_probe.py') and len(opacity['runs'])==2,'Fresh actual opacity owner regression');check(opacity['map'])
    previous_opacity=WS/'artifacts/client455-progress/client455-minimap-opacity-native-before114.json';old_opacity=json.loads(previous_opacity.read_text());old_frames={row['nation']:{Path(x['file']).name:x for x in row['frames']} for row in old_opacity['runs']};opacity_frames=[]
    for row in opacity['runs']:
        for item in row['inputs']+[row['exe'],row['output']]:check(item)
        require(not row['exit'] and row['native']==json.loads((WS/row['output']['file']).read_text()) and row['native']['status']=='PASS' and row['native']['queued_amounts']==81,'Actual queued opacity behavior')
        for frame in row['frames']:
            check(frame);require(sha(WS/frame['preview'])==frame['preview_sha256'] and frame['sha256']==old_frames[row['nation']][Path(frame['file']).name]['sha256'],'Opacity prior pixels preserved');check(old_frames[row['nation']][Path(frame['file']).name]);opacity_frames.append(frame)
    require(review['opacity_native_sha256']==sha(WS/'inventory/client455-minimap-opacity-native.json') and review['opacity_reviewed_frames']==6 and review['opacity_frames']==opacity_frames,'Viewed current6opacity frames');check(review['opacity_sheet'])
    messages=checked_native('client455-message-dispatch-native',link_hash);require(messages['script_sha256']==sha(WS/'scripts/probe_client455_message_dispatch.py') and messages['source']['sha256']==sha(WS/'scripts/native/client455_message_dispatch_probe.cpp') and messages['native']['checks']==83,'Actual MainGame message regression');view=load('client455-message-dispatch-visual-review');require(view['reviewed'] and view['reviewed_frames']==5 and view['frames']==messages['frames'] and view['native_sha256']==sha(WS/'inventory/client455-message-dispatch-native.json'),'Viewed current5message frames');check(view['sheet'])
    previous_messages=WS/'artifacts/client455-progress/client455-message-dispatch-native-before114.json';old_messages={Path(x['file']).name:x for x in json.loads(previous_messages.read_text())['frames']}
    for row in messages['frames']:check(row);check(row['preview']);check(old_messages[Path(row['file']).name]);require(row['sha256']==old_messages[Path(row['file']).name]['sha256'],'Message prior pixels preserved')
    early,ui=load('client455-startup-native'),load('client455-ui-startup-native');require(early['normal_link_sha256']==ui['normal_link_sha256']==link_hash and not early['debugger_exit'] and early['sound_return']==1 and not ui['debugger_exit'] and ui['completed_existing_client_create'] and any(x['name']=='after_client_create' and x['eax']==1 for x in ui['markers']) and all(x['first_chance']==1 for x in ui['exceptions']),'Exact own PE Create1');check(early['events']);check(ui['events'])
    engine=load('client455-startup-engine-build');require(sha(WS/engine['library'])==engine['library_sha256']=='546a7529b51139e856b1a108fcad7849c14b2d00563b7abbfdcc8db10026fa5a','Engine unchanged');check(engine['baseline_library'])
    previous=WS/'artifacts/client455-progress/client455-character-flags-checkpoint-before114.json';old_gate=json.loads(previous.read_text());historical=old_gate['historical_not_rerun'];historical.update({name:record(WS/f'artifacts/client455-progress/client455-{name}-before114.json') for name in ['character-flags-native','character-flags-reference']})
    for row in historical.values():check(row)
    fresh=['nuclear-minimap-reference','nuclear-minimap-native','nuclear-minimap-visual-review','minimap-opacity-native','message-dispatch-native','message-dispatch-visual-review','normal-preparation','normal-build','normal-consumers','normal-link','own-entry','startup-audit','startup-native','ui-startup-native']
    report=dict(status='PARTIAL',scope=ref['scope'],script_sha256=sha(Path(__file__)),sources=sources,generated_providers=providers,normal_link_sha256=link_hash,normal_executable=link['executable'],own_decoded_calls=decoded,own_Draw_slot=own_slots[0],native_checks=702,draw_alpha_states=256,opacity_regression_nations=2,queued_opacity_amounts_per_nation=81,message_regression_checks=83,viewed_GPU_frames=17,byte_equal_prior_opacity_message_frames=11,baselines=[record(previous_opacity),record(previous_messages)],normal_marker_owners_init_bounds_Draw=True,typed_post_lookup_UI_in_fullobject_lab=True,registry_race_lookup=False,ordinary_geometry_world_producer=False,normal_receiver=False,full_minimap=False,previous113_gate=record(previous),previous113_runtime_gate='HISTORICAL',historical_not_rerun=historical,fresh_evidence={name:record(WS/f'inventory/client455-{name}.json') for name in fresh},derived_engine_unchanged=engine['library_sha256'],unchanged_bulk_suites_rerun=False,gaps=ref['gaps']+['All previous Character/SetAction/movement/full64bit status and client-acceptance gaps remain'],input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-nuclear-minimap-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n');print('PARTIAL:actual3marker owners/init/bounds/Draw;native702/6GPU,2nationopacity81/message83/17viewedGPU/11byteequal/Create1;registry/worldproducer/receiver/M9OPEN')


if __name__=='__main__':main()
