"""Verify real center-message dependency and late aiming hook, not full dispatch."""
import hashlib
import json
import re
import struct
import subprocess
from pathlib import Path
from audit_client455_item_payloads import record
from audit_client455_own_entry import symbol
from build_client455_x87_math import read_va
from checkpoint_client455_item_icon_metadata import checked_native
from checkpoint_client455_rvp_effects import check,load,require,sha
from client455_normal_link_evidence import validate_normal_link
from compare_client_binaries import WS,pe


def main():
    ref=load('client455-system-messages-reference')
    require(ref['script_sha256']==sha(WS/'scripts/audit_client455_system_messages.py') and (ref['selected_functions'],ref['complete_assembly_functions'],ref['instructions'])==(25,21,2914) and ref['current_source_timing_matches_target'],'Current selected reference')
    for row in [ref['raw_evidence'],ref['additional_evidence'],ref['session'],ref['implementation_session']]+ref['current_sources']:check(row)
    for item in ['session','implementation_session']:
        state=json.loads((WS/ref[item]['file']).read_text());require(state['closed']['success'] and state['closed']['saved'] and not state['after']['count'],'IDA cleanup')
    pins=json.loads((WS/'config/client-target.json').read_text())
    for folder,key,pin in zip(['current','reference-backup'],['behavior_reference','secondary_reference'],ref['references']):
        binary=WS/f'work/client-reference/{folder}/RF_Online.bin';data=binary.read_bytes();require(sha(binary)==pin['sha256']==pins[key]['sha256'] and pe(data)['architecture']=='x86' and len(pin['ranges'])==25,'Pinned x86 input')
        for row in pin['ranges']:require(hashlib.sha256(read_va(data,0x400000+int(row['rva'],16),row['bytes'])).hexdigest()==row['sha256'],'Selected range drift')
    require(ref['references'][0]['ranges']==ref['references'][1]['ranges'],'Reference equivalence')
    link=load('client455-normal-link');link_hash=sha(WS/'inventory/client455-normal-link.json');require(validate_normal_link(link)=='PASS' and link['client_objects']==182,'Normal executable')
    prep,build=load('client455-normal-preparation'),load('client455-normal-build')
    require(prep['script_sha256']==sha(WS/'scripts/prepare_client455_normal.py') and prep['center_messages_port_sha256']==sha(WS/'scripts/client455_center_messages_port.py') and prep['nuclear_aiming_port_sha256']==sha(WS/'scripts/client455_nuclear_aiming_port.py'),'Port provenance')
    require(not build['build_exit'] and not build['errors'] and build['canonical_kernel_objects']==20 and build['source_manifest_sha256']==prep['manifest_sha256'] and len(list((WS/'work/client455-port/normal/build/RFClient455Facade.dir/Release').glob('*.obj')))==61,'Current full object build')
    sources=[record(WS/'scripts/native'/name) for name in ['client455_center_messages.h','client455_center_messages.cpp','client455_font.h','client455_font.cpp']]
    for row in sources:require(prep['record_inputs'][Path(row['file']).name]==row['sha256'],'Prepared source drift')
    check(dict(file=prep['manifest'],sha256=prep['manifest_sha256']));check(dict(file=build['log'],sha256=build['log_sha256']))
    manifest=json.loads((WS/prep['manifest']).read_text());providers=[]
    for suffix in ['source/gameprogress/cgp_maingame.h','source/gameprogress/cgp_maingame.cpp','source/addcodebyjang/foreffect.cpp','generated/client455_center_messages.cpp','generated/client455_font.cpp']:
        rows=[row for row in manifest if row['file'].lower().endswith('/'+suffix)];require(len(rows)==1,'Generated provider '+suffix)
        for row in rows:check(row);check(dict(file=row['input'],sha256=row['input_sha256']))
        providers+=rows
    root=WS/'work/client455-port/normal/source';stage=(root/'gameprogress/cgp_maingame.cpp').read_bytes();header=(root/'gameprogress/cgp_maingame.h').read_bytes();effects=(root/'addcodebyjang/foreffect.cpp').read_bytes()
    require(header.index(b'm_uiOptionWindow;')<header.index(b'RF455CenterMessages m_centerMessages455;'),'Owner constructed after UI members')
    require(stage.index(b'_GetGBM()->FrameMove();')<stage.index(b'm_centerMessages455.FrameMove();')<stage.index(b'::FrameMoveEffect();'),'Selected update placement')
    require(stage.count(b'RF455_NuclearAiming().FrameMove();')==1 and stage.index(b'_GetUIScreen()->Draw();')<stage.index(b'RF455_NuclearAiming().FrameMove();')<stage.index(b'm_centerMessages455.Draw();') and b'RF455_NuclearAiming().FrameMove();' not in effects,'Single late aiming hook')
    mapping=(WS/link['map']['file']).read_text();raw=(WS/link['executable']['file']).read_bytes();base=pe(raw)['image_base']
    names={'render':'?Render@CGP_MainGame@@MAEJXZ','update':'?FrameMove@CGP_MainGame@@MAEJXZ','old_effect_frame':'?FrameMoveEffect@@YAXXZ','aiming':'?FrameMove@RF455NuclearAiming@@QAEXXZ','messages_update':'?FrameMove@RF455CenterMessages@@QAEXXZ','messages_draw':'?Draw@RF455CenterMessages@@QBEXXZ'}
    addresses={key:symbol(mapping,value) for key,value in names.items()};starts=sorted({int(row,16) for row in re.findall(r'^\s+0001:[0-9a-fA-F]{8}\s+\S+\s+([0-9a-fA-F]{8})\b',mapping,re.M)})
    info=load('msvc-verification');dumpbin=Path(info['compiler_path'].splitlines()[0]).with_name('dumpbin.exe');art=WS/'artifacts/client455-progress/messages108-own';art.mkdir(parents=True,exist_ok=True);decoded={};calls={};disassembly=[]
    for key in ['render','update','old_effect_frame']:
        start=addresses[key];end=next(at for at in starts if at>start)
        result=subprocess.run([str(dumpbin),'/DISASM:BYTES',f'/RANGE:0x{start:x},0x{end:x}',str(WS/link['executable']['file'])],capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW);require(not result.returncode,'Own PE decode')
        path=art/(key+'.txt');path.write_bytes(result.stdout);disassembly.append(record(path));rows=[];edges=[]
        for line in result.stdout.decode(errors='replace').splitlines():
            match=re.match(r'^\s+([0-9A-F]{8}): ((?:[0-9A-F]{2} )+)\s+(\w+)\s*(.*?)\s*$',line)
            if not match:continue
            at=int(match[1],16);data=bytes.fromhex(match[2])
            if at>=end:continue
            require(data==read_va(raw,at,len(data)),'Decoded bytes drift');rows.append(at)
            if match[3]=='call' and len(data)==5 and data[0]==0xe8:edges.append(dict(rva=hex(at-base),target=at+5+struct.unpack('<i',data[1:])[0]))
        require(rows and rows[0]==start,'Full own function begins at decoded entry');decoded[key]=dict(rva=hex(start-base),bytes=end-start,sha256=hashlib.sha256(read_va(raw,start,end-start)).hexdigest());calls[key]=edges
    def edge(owner,target):
        rows=[row for row in calls[owner] if row['target']==addresses[target]];require(len(rows)==1,'Compiled single edge '+owner+'->'+target);return rows[0]['rva']
    render_aim=edge('render','aiming');render_messages=edge('render','messages_draw');update_messages=edge('update','messages_update');update_effects=edge('update','old_effect_frame')
    require(int(render_aim,16)<int(render_messages,16) and int(update_messages,16)<int(update_effects,16) and all(row['target']!=addresses['aiming'] for row in calls['old_effect_frame']),'Compiled selected phase order')
    run=checked_native('client455-center-messages-native',link_hash)
    require(run['script_sha256']==sha(WS/'scripts/probe_client455_center_messages.py') and run['source']['sha256']==sha(WS/'scripts/native/client455_center_messages_probe.cpp') and run['builder_sha256']==sha(WS/'scripts/client455_own_probe.py') and run['reference_sha256']==sha(WS/'inventory/client455-system-messages-reference.json'),'Center native provenance')
    check(run['source']);check(run['console'])
    for row in run['inputs']:check(row)
    result=run['native'];require((result['checks'],result['record_bytes'],result['chunk_bytes'],result['active_capacity'],result['GPU_frames'])==(69,84,64,3,4) and all(n>0 for n in result['pixels'][:3]) and result['pixels'][3]==0 and result['fade_drain_ticks']<80,'Native selected domain')
    for key in ['actual_MainGame_owner','real_language_C1A_CE7','real_medium_GDI_oracle','DBCS_boundary','queue500ms_and_flood','fade3600ms_and_single_eviction','unsigned_elapsed','unclamped_factor','owner_unbound','all_center_records_released','legacy_uncreated_MainGame_allocations_gap']:require(result[key],'Native '+key)
    for key in ['full_stage_teardown','full_C1A_dispatch','live_hover_cancel','full_chat','full_world_frame_order','full_client']:require(not result[key],'Unjustified full acceptance '+key)
    hover=checked_native('client455-board-hover-native',link_hash)
    for name,report,count in [('center-messages',run,4),('board-hover',hover,6)]:
        review=load(f'client455-{name}-visual-review');require(review['reviewed'] and review['reviewed_frames']==count and review['frames']==report['frames'] and review['native_sha256']==sha(WS/f'inventory/client455-{name}-native.json'),'Current viewed '+name);check(review['sheet'])
        for row in report['frames']:check(row);check(row['preview'])
    baseline=WS/'artifacts/client455-progress/client455-board-hover-native-before108.json';before={Path(row['file']).name:row for row in json.loads(baseline.read_text())['frames']};require(len(before)==len(hover['frames'])==6,'Hover coverage')
    for row in hover['frames']:check(before[Path(row['file']).name]);require(row['sha256']==before[Path(row['file']).name]['sha256'],'Changed hover pixels')
    require(checked_native('client455-player-status-native',link_hash)['native']['checks']==62,'Avatar/hover regression');aiming=checked_native('client455-nuclear-aiming-native',link_hash)
    require(aiming['native']['checks']==29 and aiming['native']['real_world_cursor'] and aiming['native']['real_Miles_radar'] and aiming['native']['scoped_memory_balanced'],'Real aiming regression')
    early,ui=load('client455-startup-native'),load('client455-ui-startup-native');require(early['normal_link_sha256']==ui['normal_link_sha256']==link_hash and early['sound_return']==1 and not early['debugger_exit'] and not ui['debugger_exit'] and ui['completed_existing_client_create'] and any(row['name']=='after_client_create' and row['eax']==1 for row in ui['markers']) and all(row['first_chance']==1 for row in ui['exceptions']),'Exact own Create1');check(early['events']);check(ui['events'])
    engine=load('client455-startup-engine-build');require(sha(WS/engine['library'])==engine['library_sha256']=='546a7529b51139e856b1a108fcad7849c14b2d00563b7abbfdcc8db10026fa5a','Unchanged engine');check(engine['baseline_library'])
    previous=WS/'artifacts/client455-progress/client455-nuclear-aiming-checkpoint-before108.json';history=json.loads(previous.read_text());historical={}
    for name in ['magic-native','effect-resources-native','effect-runtime-native','tagged-audio-native','account-native','hotbar-native','storage-native']:
        row=history['fresh_evidence'][name];check(row);historical[name]=row
    fresh=['system-messages-reference','center-messages-native','center-messages-visual-review','normal-preparation','normal-build','normal-consumers','normal-link','own-entry','startup-audit','startup-native','ui-startup-native','nuclear-aiming-native','player-status-native','board-hover-native','board-hover-visual-review']
    report=dict(status='PARTIAL',scope='Ordinary center-message dependency and selected late aiming frame placement; full C1A/chat/hover/gameplay remains open',script_sha256=sha(Path(__file__)),sources=sources,generated_providers=providers,normal_link_sha256=link_hash,normal_executable=link['executable'],own_decoded_functions=decoded,own_disassembly=disassembly,compiled_edges=dict(late_aiming=render_aim,center_draw=render_messages,center_update=update_messages,effect_update=update_effects),native_checks=69,ordinary_FrameMove_checked=True,actual_MainGame_member=True,viewed_GPU_frames=10,byte_equal_hover_frames=6,current_source_timing_matches_target=True,full_world_frame_order=False,game_message_producers_present=False,full_C1A_dispatch=False,live_hover_cancel=False,full_stage_teardown=False,legacy_uncreated_MainGame_allocations_gap=True,fresh_evidence={name:record(WS/f'inventory/client455-{name}.json') for name in fresh},historical_not_rerun=historical,previous107_checkpoint=record(previous),previous107_runtime_gate='HISTORICAL',baseline=record(baseline),unchanged_bulk_suites_rerun=False,other32_GUI_frames_rerun=False,derived_engine_unchanged=engine['library_sha256'],gaps=ref['gaps']+['Own center message record and singleton lifetime accepted only in selected domain; modern STL/privateABI/OOM/FP/CRT startup/camera/font reset/full stage teardown remain open'],input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-center-messages-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n');print('PARTIAL:MainGame center84/queue64/69checks/4viewedGPU/lateaiming ownCALLS verified;fullchat/C1A/M9OPEN')


if __name__=='__main__':main()
