"""Verify selected chat profile/pane integration, leaving full dispatch/UI open."""
import configparser,hashlib,json,re,struct,subprocess
from pathlib import Path
from audit_client455_item_payloads import record
from audit_client455_own_entry import symbol
from build_client455_x87_math import read_va
from checkpoint_client455_item_icon_metadata import checked_native
from checkpoint_client455_rvp_effects import check,load,require,sha
from client455_normal_link_evidence import validate_normal_link
from compare_client_binaries import WS,pe


def main():
    ref=load('client455-chat-reference');require(ref['script_sha256']==sha(WS/'scripts/audit_client455_chat.py') and (ref['selected_functions'],ref['full_assembly_functions'],ref['instructions'])==(44,31,3615),'Selected provenance')
    for row in [ref['raw_evidence'],ref['lexer_evidence'],ref['session'],ref['lexer_session'],ref['generated']]+ref['inputs']:check(row)
    for key in ['session','lexer_session']:
        state=json.loads((WS/ref[key]['file']).read_text());require(state['closed']['success'] and state['closed']['saved'] and not state['after']['count'],'IDA cleanup')
    pins=json.loads((WS/'config/client-target.json').read_text())
    for folder,key,pin in zip(['current','reference-backup'],['behavior_reference','secondary_reference'],ref['references']):
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';data=path.read_bytes();require(sha(path)==pin['sha256']==pins[key]['sha256'] and pe(data)['architecture']=='x86' and len(pin['ranges'])==44,'Pinned x86 input')
        for row in pin['ranges']+pin['data']:require(hashlib.sha256(read_va(data,0x400000+int(row['rva'],16),row['bytes'])).hexdigest()==row['sha256'],'Reference bytes')
    require(ref['references'][0]['ranges']==ref['references'][1]['ranges'] and ref['references'][0]['data']==ref['references'][1]['data'],'Reference equality')
    require(len(ref['inputs'])==8 and [row['nation'] for row in ref['inputs'] if row['utf16_bom_without_decoding']]==[8] and [row['nation'] for row in ref['missing_script_inputs']]==[3,9,10],'Actual script availability')
    for row in ref['inputs']:require(sha(Path(row['original']))==row['sha256'],'Original script drift')
    link=load('client455-normal-link');link_hash=sha(WS/'inventory/client455-normal-link.json');require(validate_normal_link(link)=='PASS' and link['client_objects']==182,'Ordinary link')
    prep,build=load('client455-normal-preparation'),load('client455-normal-build')
    require(prep['script_sha256']==sha(WS/'scripts/prepare_client455_normal.py') and prep['chat_port_sha256']==sha(WS/'scripts/client455_chat_port.py') and prep['chat_reference_sha256']==sha(WS/'inventory/client455-chat-reference.json'),'Current port provenance')
    require(not build['build_exit'] and not build['errors'] and build['canonical_kernel_objects']==20 and build['source_manifest_sha256']==prep['manifest_sha256'] and len(list((WS/'work/client455-port/normal/build/RFClient455Facade.dir/Release').glob('*.obj')))==63,'Full source build')
    sources=[record(WS/'scripts/native'/name) for name in ['client455_chat_profile.h','client455_chat_profile.cpp','client455_chat_window.h','client455_chat_window.cpp']]
    for row in sources:require(prep['record_inputs'][Path(row['file']).name]==row['sha256'],'Prepared source drift')
    check(dict(file=prep['manifest'],sha256=prep['manifest_sha256']));check(dict(file=build['log'],sha256=build['log_sha256']));manifest=json.loads((WS/prep['manifest']).read_text());providers=[]
    for suffix in ['source/gameprogress/cgp_maingame.h','source/gameprogress/cgp_maingame.cpp','source/userinterface/gamewindow/guichatwindow.h','source/userinterface/guicontroller/guitextboard.h','generated/client455_chat_profile.cpp','generated/client455_chat_window.cpp','include/client455_chat_reference_tables.h']:
        rows=[row for row in manifest if row['file'].lower().endswith('/'+suffix)];require(len(rows)==1,'Generated '+suffix)
        for row in rows:check(row);check(dict(file=row['input'],sha256=row['input_sha256']))
        providers+=rows
    root=WS/'work/client455-port/normal/source';header=(root/'gameprogress/cgp_maingame.h').read_bytes();stage=(root/'gameprogress/cgp_maingame.cpp').read_bytes()
    require(header.index(b'RF455ChatProfile m_chatProfile455;')<header.index(b'm_uiChatWindow;') and stage.count(b'm_uiChatWindow.InitializeChat455();')==1,'Actual stage member/init')
    mapping=(WS/link['map']['file']).read_text();raw=(WS/link['executable']['file']).read_bytes();base=pe(raw)['image_base'];begin=symbol(mapping,'?Create_UI@CGP_MainGame@@IAEXXZ');target=symbol(mapping,'?InitializeChat455@CGUIChatWindow@@QAEXPBD@Z')
    starts=sorted({int(row,16) for row in re.findall(r'^\s+0001:[0-9a-fA-F]{8}\s+\S+\s+([0-9a-fA-F]{8})\b',mapping,re.M)});end=next(at for at in starts if at>begin);dumpbin=Path(load('msvc-verification')['compiler_path'].splitlines()[0]).with_name('dumpbin.exe')
    decoded=subprocess.run([str(dumpbin),'/DISASM:BYTES',f'/RANGE:0x{begin:x},0x{end:x}',str(WS/link['executable']['file'])],capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW);require(not decoded.returncode,'Own decode');path=WS/'artifacts/client455-progress/chat109-own-create-ui.txt';path.write_bytes(decoded.stdout);calls=[]
    for line in decoded.stdout.decode(errors='replace').splitlines():
        match=re.match(r'^\s+([0-9A-F]{8}): ((?:[0-9A-F]{2} )+)\s+(\w+)\s*(.*?)\s*$',line)
        if not match:continue
        at=int(match[1],16);data=bytes.fromhex(match[2])
        if at>=end:continue
        require(data==read_va(raw,at,len(data)),'Decoded PE bytes')
        if match[3]=='call' and len(data)==5 and data[0]==0xe8 and at+5+struct.unpack('<i',data[1:])[0]==target:calls.append(hex(at-base))
    require(len(calls)==1 and '?InsertText455@CGUIChatWindow@@' not in mapping,'Ordinary init retained; new insert producers still absent')
    run=checked_native('client455-chat-native',link_hash);require(run['script_sha256']==sha(WS/'scripts/probe_client455_chat.py') and run['oracle_sha256']==sha(WS/'scripts/client455_chat_oracle.py') and run['builder_sha256']==sha(WS/'scripts/client455_own_probe.py') and run['reference_sha256']==sha(WS/'inventory/client455-chat-reference.json') and run['source']['sha256']==sha(WS/'scripts/native/client455_chat_probe.cpp'),'Native provenance');check(run['source']);check(run['console']);check(run['persisted_settings'])
    for row in run['inputs']:check(row)
    expected={row['runtime_relative'].lower():row['sha256'] for row in ref['inputs']}
    for relative,digest in expected.items():rows=[row for row in run['inputs'] if row['file'].lower().endswith('/'+relative)];require(len(rows)==1 and rows[0]['sha256']==digest,'Stock runtime script')
    config=configparser.ConfigParser();config.read(WS/run['persisted_settings']['file']);require(config.getint('DefModeOn','All')==0x3fff and all(config.getint('ChatMode',name)==0 for name in ref['settings_keys']),'Exact intended settings output')
    high_settings=(WS/run['exe']['file']).parent/'high-mask.ini';high=configparser.ConfigParser();high.read(high_settings);require(high.get('DefModeOn','All')=='-2147467265','High DWORD persisted as target signed decimal')
    result=run['native'];require((result['checks'],result['real_script_inputs'],result['profile_records'],result['styles'],result['categories'],result['prefix_bytes'],result['font_bytes'],result['GPU_frames'])==(385,8,288,36,14,18,16,5) and all(value>0 for value in result['pixels'][:4]) and result['pixels'][4]==0,'Selected native domain')
    for key in ['actual_MainGame_profile','actual_window_4panes','fallback13_quirk','fallback19_country','ambient_prefix_DBCS','settings_default_masks','DefModeOn_persisted','ordinary_typed_Insert','real_C1A_direct_input','wrap_and_newline_quirks','style26_bypass','all_pane_records_released','profile_unbound','legacy_uncreated_stage_teardown_gap']:require(result[key],'Native '+key)
    for key in ['full_chat_UI','legacy_callers_migrated','full_C1A_dispatch','live_hover_cancel','full_client']:require(not result[key],'Unjustified full acceptance '+key)
    center=checked_native('client455-center-messages-native',link_hash);require(center['native']['checks']==69,'Center coexistence');hover=checked_native('client455-board-hover-native',link_hash)
    for name,report,count in [('chat',run,5),('center-messages',center,4),('board-hover',hover,6)]:
        review=load(f'client455-{name}-visual-review');require(review['reviewed'] and review['reviewed_frames']==count and review['frames']==report['frames'] and review['native_sha256']==sha(WS/f'inventory/client455-{name}-native.json'),'Viewed '+name);check(review['sheet'])
        for row in report['frames']:check(row);check(row['preview'])
    baselines=[]
    for baseline,report,count in [('client455-board-hover-native-before109.json',hover,6),('client455-center-messages-visual-review-before109.json',center,4)]:
        path=WS/'artifacts/client455-progress'/baseline;before={Path(row['file']).name:row for row in json.loads(path.read_text())['frames']};require(len(before)==len(report['frames'])==count,'Regression frame coverage')
        for row in report['frames']:check(before[Path(row['file']).name]);require(row['sha256']==before[Path(row['file']).name]['sha256'],'Regression pixels changed')
        baselines.append(record(path))
    early,ui=load('client455-startup-native'),load('client455-ui-startup-native');require(early['normal_link_sha256']==ui['normal_link_sha256']==link_hash and early['sound_return']==1 and not early['debugger_exit'] and not ui['debugger_exit'] and ui['completed_existing_client_create'] and any(row['name']=='after_client_create' and row['eax']==1 for row in ui['markers']) and all(row['first_chance']==1 for row in ui['exceptions']),'Exact own Create1');check(early['events']);check(ui['events'])
    engine=load('client455-startup-engine-build');require(sha(WS/engine['library'])==engine['library_sha256']=='546a7529b51139e856b1a108fcad7849c14b2d00563b7abbfdcc8db10026fa5a','Engine unchanged');check(engine['baseline_library'])
    prior=WS/'artifacts/client455-progress/client455-center-messages-checkpoint-before109.json';previous=json.loads(prior.read_text());historical=dict(previous['historical_not_rerun'])
    for name in ['nuclear-aiming-native','player-status-native']:historical[name]=previous['fresh_evidence'][name]
    for row in historical.values():check(row)
    fresh=['chat-reference','chat-native','chat-visual-review','center-messages-native','center-messages-visual-review','board-hover-native','board-hover-visual-review','normal-preparation','normal-build','normal-consumers','normal-link','own-entry','startup-audit','startup-native','ui-startup-native']
    report=dict(status='PARTIAL',scope=ref['scope'],script_sha256=sha(Path(__file__)),sources=sources,generated_providers=providers,normal_link_sha256=link_hash,normal_executable=link['executable'],own_create_ui_disassembly=record(WS/'artifacts/client455-progress/chat109-own-create-ui.txt'),own_profile_init_call_rva=calls[0],native_checks=385,record_oracle_rows=288,actual_script_inputs=8,viewed_GPU_frames=15,byte_equal_prior_center_hover_frames=10,baselines=baselines,missing_country_script_inputs=ref['missing_script_inputs'],Taiwan_UTF16_byte_fallback_preserved=True,typed_insert_only=True,legacy_callers_migrated=False,full_chat_UI=False,full_C1A_dispatch=False,live_hover_cancel=False,previous108_checkpoint=record(prior),previous108_runtime_gate='HISTORICAL',historical_not_rerun=historical,fresh_evidence={name:record(WS/f'inventory/client455-{name}.json') for name in fresh},derived_engine_unchanged=engine['library_sha256'],unchanged_bulk_suites_rerun=False,other32_GUI_frames_rerun=False,gaps=ref['gaps'],input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    report['high_DWORD_signed_settings']=record(high_settings)
    (WS/'inventory/client455-chat-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n');print('PARTIAL:profile36/8scripts/288oracle rows/4realpanes/385checks/15viewedGPU;fullUI/callers/C1A/M9OPEN')


if __name__=='__main__':main()
