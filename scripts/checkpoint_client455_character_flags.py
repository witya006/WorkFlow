"""Gate selected Character flags/runtime regressions; full455 acceptance stays open."""
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
    ref=load('client455-character-flags-reference');require(ref['script_sha256']==sha(WS/'scripts/audit_client455_character_flags.py') and (ref['selected_functions'],ref['pseudocode_functions'],ref['full_assembly_functions'],ref['instructions'])==(30,29,14,760),'Selected reference coverage')
    for row in [ref['raw'],ref['session']]+ref['cached_reference']:check(row)
    session=json.loads((WS/ref['session']['file']).read_text());require(session['closed']['success'] and session['closed']['saved'] and session['after']['count']==0,'Owned IDA cleanup')
    pins=json.loads((WS/'config/client-target.json').read_text())
    for folder,key,pin in zip(['current','reference-backup'],['behavior_reference','secondary_reference'],ref['references']):
        file=WS/f'work/client-reference/{folder}/RF_Online.bin';image=file.read_bytes();require(sha(file)==pins[key]['sha256']==pin['sha256'] and pe(image)['architecture']=='x86','Actual455 pin')
        for row in pin['ranges']+pin['tails']+[pin['player_vtable']]:require(hashlib.sha256(read_va(image,0x400000+int(row['rva'],16),row['bytes'])).hexdigest()==row['sha256'],'Pinned body/tail/vtable bytes')
        for row in pin['decoded_calls']:
            at=0x400000+int(row['rva'],16);code=read_va(image,at,5);require(code[0]==0xe8 and at+5+struct.unpack('<i',code[1:])[0]==0x400000+int(row['target_rva'],16),'Pinned direct edge')
    require(ref['references'][0]['ranges']==ref['references'][1]['ranges'],'Both455 selected bytes')
    link=load('client455-normal-link');link_hash=sha(WS/'inventory/client455-normal-link.json');require(validate_normal_link(link)=='PASS' and link['client_objects']==182 and not link['unique_unresolved'],'Actual ordinary source link')
    prep,build=load('client455-normal-preparation'),load('client455-normal-build');require(prep['script_sha256']==sha(WS/'scripts/prepare_client455_normal.py') and prep['character_flags_port_sha256']==sha(WS/'scripts/client455_character_flags_port.py'),'Prepared migration provenance')
    require(not build['build_exit'] and not build['errors'] and build['canonical_kernel_objects']==20 and build['source_manifest_sha256']==prep['manifest_sha256'] and len(list((WS/'work/client455-port/normal/build/RFClient455Facade.dir/Release').glob('*.obj')))==65,'182client/20kernel/65facade')
    sources=[record(WS/'scripts/native'/name) for name in ['client455_character_flags.h','client455_character_flags.cpp']]
    for row in sources:require(prep['record_inputs'][Path(row['file']).name]==row['sha256'],'Prepared Character flags input')
    check(dict(file=prep['manifest'],sha256=prep['manifest_sha256']));check(dict(file=build['log'],sha256=build['log_sha256']));manifest=json.loads((WS/prep['manifest']).read_text());providers=[]
    for suffix in ['source/character/character/ccharacter.h','source/character/character/ccharacter_etc.cpp','source/character/player/cplayer.h','source/character/player/cplayer.cpp','generated/client455_character_flags.cpp','include/client455_character_flags.h']:
        rows=[row for row in manifest if row['file'].lower().endswith('/'+suffix)];require(len(rows)==1,'Actual source provider '+suffix)
        for row in rows:check(row);check(dict(file=row['input'],sha256=row['input_sha256']))
        providers+=rows
    mapping=(WS/link['map']['file']).read_text();own=(WS/link['executable']['file']).read_bytes();base=pe(own)['image_base'];starts=sorted({int(x,16) for x in re.findall(r'^\s+0001:[0-9a-fA-F]{8}\s+\S+\s+([0-9a-fA-F]{8})\b',mapping,re.M)});dumpbin=Path(load('msvc-verification')['compiler_path'].splitlines()[0]).with_name('dumpbin.exe');decoded=[]
    def calls(name):
        begin=symbol(mapping,name);end=next(x for x in starts if x>begin);out=subprocess.run([str(dumpbin),'/DISASM:BYTES',f'/RANGE:0x{begin:x},0x{end:x}',str(WS/link['executable']['file'])],capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW);require(not out.returncode,'Own code decode')
        file=WS/f'artifacts/client455-progress/character113-own-{len(decoded)}.txt';file.write_bytes(out.stdout);edges=[];instructions=[]
        for line in out.stdout.decode(errors='replace').splitlines():
            match=re.match(r'^\s+([0-9A-F]{8}): ((?:[0-9A-F]{2} )+)\s+(\w+)\s*(.*?)\s*$',line)
            if not match:continue
            at=int(match[1],16);data=bytes.fromhex(match[2])
            if at>=end:continue
            require(data==read_va(own,at,len(data)),'Own decoded bytes');instructions.append(dict(rva=hex(at-base),bytes=data.hex(),mnemonic=match[3],operand=match[4]))
            if match[3] in ['call','jmp'] and len(data)==5 and data[0] in [0xe8,0xe9]:edges.append(dict(rva=hex(at-base),target_rva=hex(at+5+struct.unpack('<i',data[1:])[0]-base)))
        require(instructions and int(instructions[0]['rva'],16)==begin-base,'Decoded actual own entry');decoded.append(dict(function=name,rva=hex(begin-base),disassembly=record(file),instructions=instructions,edges=edges));return edges
    owner=calls('?SetServerStatusFlag@CPlayer@@QAEX_K@Z')
    def edge(name):
        target=hex(symbol(mapping,name)-base);hits=[int(x['rva'],16) for x in owner if x['target_rva']==target];require(len(hits)==1,'Unique ordinary producer '+name);return hits[0]
    # ApplyStatusFlags455 is inline in this build. Locate its decoded bit16
    # predicate rather than inventing a non-existent out-of-line call.
    status=[int(x['rva'],16) for x in decoded[0]['instructions'] if x['mnemonic']=='and' and x['operand']=='ecx,10000h']
    require(len(status)==1 and edge('?ApplyCharacterControlFlags455@CPlayer@@QAEH_K@Z')<status[0],'Ordinary internal flags before inline status conversion')
    calls('?IsDeath@CCharacter@@QAEHXZ');calls('?ApplyCharacterControlFlags455@CPlayer@@QAEH_K@Z')
    native=checked_native('client455-character-flags-native',link_hash);require(native['script_sha256']==sha(WS/'scripts/probe_client455_character_flags.py') and native['source']['sha256']==sha(WS/'scripts/native/client455_character_flags_probe.cpp') and native['builder_sha256']==sha(WS/'scripts/client455_own_probe.py'),'Native source provenance');check(native['source']);check(native['console'])
    result=native['native'];require((result['checks'],result['target_trace_cases'],result['action_highnibbles'],result['internal_masks'])==(173,8,16,8),'Selected native boundary coverage')
    for key in ['actual_Avatar','actual_ordinary_IsDeath','any_none_semantics','source_flag_clock','ordinary64bit_producer','control_before_status','action_transitions_kernel_only']:require(result[key],'Actual flags '+key)
    for key in ['full_movement_controller','full_action_pipeline','full_455_status_writer','normal_nuclear_receiver','full_client']:require(not result[key],'No full acceptance claim '+key)
    regressions={name:checked_native('client455-'+name+'-native',link_hash) for name in ['player-status','message-dispatch','center-messages','board-hover']}
    require(regressions['player-status']['native']['checks']==62 and regressions['message-dispatch']['native']['checks']==83 and regressions['center-messages']['native']['checks']==69,'Selected existing behavior')
    for name,count in [('message-dispatch',5),('center-messages',4),('board-hover',6)]:
        run=regressions[name];review=load('client455-'+name+'-visual-review');require(review['reviewed'] and review['reviewed_frames']==count and review['frames']==run['frames'] and review['native_sha256']==sha(WS/f'inventory/client455-{name}-native.json'),'Viewed actual current frames');check(review['sheet'])
        for row in run['inputs']+run['frames']:check(row)
        for row in run['frames']:check(row['preview'])
    baselines=[]
    for name,count in [('center-messages',4),('board-hover',6)]:
        file=WS/f'artifacts/client455-progress/client455-{name}-native-before113.json';old={Path(x['file']).name:x for x in json.loads(file.read_text())['frames']};rows=regressions[name]['frames'];require(len(rows)==len(old)==count,'Baseline frame count')
        for row in rows:check(old[Path(row['file']).name]);require(old[Path(row['file']).name]['sha256']==row['sha256'],'Previous pixels preserved')
        baselines.append(record(file))
    early,ui=load('client455-startup-native'),load('client455-ui-startup-native');require(early['normal_link_sha256']==ui['normal_link_sha256']==link_hash and not early['debugger_exit'] and early['sound_return']==1 and not ui['debugger_exit'] and ui['completed_existing_client_create'] and any(x['name']=='after_client_create' and x['eax']==1 for x in ui['markers']) and all(x['first_chance']==1 for x in ui['exceptions']),'Exact normal PE Create1');check(early['events']);check(ui['events'])
    engine=load('client455-startup-engine-build');require(sha(WS/engine['library'])==engine['library_sha256']=='546a7529b51139e856b1a108fcad7849c14b2d00563b7abbfdcc8db10026fa5a','Engine unchanged');check(engine['baseline_library'])
    previous=WS/'artifacts/client455-progress/client455-message-dispatch-checkpoint-before113.json';old=json.loads(previous.read_text());historical=old['historical_not_rerun']
    for row in historical.values():check(row)
    fresh=['character-flags-reference','character-flags-native','normal-preparation','normal-build','normal-consumers','normal-link','own-entry','startup-audit','startup-native','ui-startup-native']+[name+suffix for name in regressions for suffix in (['-native'] if name=='player-status' else ['-native','-visual-review'])]
    report=dict(status='PARTIAL',scope=ref['scope'],script_sha256=sha(Path(__file__)),sources=sources,generated_providers=providers,normal_link_sha256=link_hash,normal_executable=link['executable'],own_decoded_producers=decoded,native_checks=173,status_regression_checks=62,message_regression_checks=83,center_regression_checks=69,viewed_GPU_frames=15,prior_center_hover_byte_equal_frames=10,baselines=baselines,ordinary_guard_and_selected64bit_control=True,source_clock_actual_Avatar_lab_only=True,full_action_pipeline=False,full_movement_controller=False,full_455_status_writer=False,normal_nuclear_receiver=False,MiniMap_marker_source_integration=False,previous111_gate=record(previous),previous111_runtime_gate='HISTORICAL',component112_historical=record(WS/'inventory/client455-nuclear-wire-checkpoint.json'),component112_decoder_unchanged=True,historical_not_rerun=historical,fresh_evidence={name:record(WS/f'inventory/client455-{name}.json') for name in fresh},derived_engine_unchanged=engine['library_sha256'],unchanged_bulk_suites_rerun=False,gaps=ref['gaps']+old['gaps']+['Bit1 timestamp has no ordinary SetAction/movement-controller/frame consumer yet;source API exercised in full-object lab','Source Character layout intentionally owned;private455 ABI not accepted;full constructor/action/status sideeffects remain open'],input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-character-flags-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n');print('PARTIAL:Character173/ordinary guard+selected64bit producer;status62/message83/center69/15viewedGPU/Create1;fullaction/movement/Nuclearreceiver/M9OPEN')


if __name__=='__main__':main()
