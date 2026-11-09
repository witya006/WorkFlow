"""Verify actual message/cancellation integration without claiming full stages/client."""
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
    ref=load('client455-message-dispatch-reference');require(ref['script_sha256']==sha(WS/'scripts/audit_client455_message_dispatch.py') and (ref['selected_functions'],ref['full_assembly_functions'],ref['instructions'])==(22,22,1254),'Pinned reference provenance')
    check(ref['raw']);check(ref['session']);state=json.loads((WS/ref['session']['file']).read_text());require(state['closed']['success'] and state['closed']['saved'] and state['after']['count']==0,'IDA cleanup')
    pins=json.loads((WS/'config/client-target.json').read_text())
    for folder,key,pin in zip(['current','reference-backup'],['behavior_reference','secondary_reference'],ref['references']):
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';data=path.read_bytes();require(sha(path)==pins[key]['sha256']==pin['sha256'] and pe(data)['architecture']=='x86','Actual455pin')
        for row in pin['ranges']+pin['tails']+[pin['sequence_format']]:require(hashlib.sha256(read_va(data,0x400000+int(row['rva'],16),row['bytes'])).hexdigest()==row['sha256'],'Target body/tail/literal')
        for row in pin['decoded_calls']:
            at=0x400000+int(row['rva'],16);code=read_va(data,at,5);require(code[0]==0xe8 and at+5+struct.unpack('<i',code[1:])[0]==0x400000+int(row['target_rva'],16),'Target call bytes')
    require(ref['references'][0]['ranges']==ref['references'][1]['ranges'] and ref['references'][0]['tails']==ref['references'][1]['tails'],'Selected equality')
    link=load('client455-normal-link');link_hash=sha(WS/'inventory/client455-normal-link.json');require(validate_normal_link(link)=='PASS' and link['client_objects']==182,'Ordinary normal link')
    prep,build=load('client455-normal-preparation'),load('client455-normal-build')
    require(prep['script_sha256']==sha(WS/'scripts/prepare_client455_normal.py') and prep['message_dispatch_port_sha256']==sha(WS/'scripts/client455_message_dispatch_port.py'),'Current port')
    require(not build['build_exit'] and not build['errors'] and build['canonical_kernel_objects']==20 and build['source_manifest_sha256']==prep['manifest_sha256'] and len(list((WS/'work/client455-port/normal/build/RFClient455Facade.dir/Release').glob('*.obj')))==64,'182/20/64 source build')
    check(dict(file=prep['manifest'],sha256=prep['manifest_sha256']));check(dict(file=build['log'],sha256=build['log_sha256']));manifest=json.loads((WS/prep['manifest']).read_text());providers=[]
    for suffix in ['source/mainapp.h','source/global.cpp','source/gameprogress/cgp_login.h','source/gameprogress/cgp_login.cpp','source/userinterface/gamewindow/guichatwindow.h','generated/client455_message_dispatch.cpp','generated/client455_board_hover.cpp','include/client455_message_dispatch.h']:
        rows=[row for row in manifest if row['file'].lower().endswith('/'+suffix)];require(len(rows)==1,'Generated '+suffix)
        for row in rows:check(row);check(dict(file=row['input'],sha256=row['input_sha256']))
        providers+=rows
    sources=[record(WS/'scripts/native'/name) for name in ['client455_message_dispatch.cpp','client455_message_dispatch.h','client455_board_hover.cpp']]
    normal=WS/'work/client455-port/normal/source';login=(normal/'gameprogress/cgp_login.cpp').read_bytes();header=(normal/'gameprogress/cgp_login.h').read_bytes();global_code=(normal/'global.cpp').read_bytes()
    require(login.count(b'm_messages455.Clear();')==login.count(b'm_messages455.Draw();')==1 and header.count(b'RF455LoginMessages m_messages455;')==1 and b'RF455_ShowSystemMessageV(l_pFormatString,args);' in global_code,'Actual member/Init/Render/ordinary formatter')
    mapping=(WS/link['map']['file']).read_text();own=(WS/link['executable']['file']).read_bytes();base=pe(own)['image_base'];starts=sorted({int(x,16) for x in re.findall(r'^\s+0001:[0-9a-fA-F]{8}\s+\S+\s+([0-9a-fA-F]{8})\b',mapping,re.M)});dumpbin=Path(load('msvc-verification')['compiler_path'].splitlines()[0]).with_name('dumpbin.exe');decoded=[]
    def calls(name):
        begin=symbol(mapping,name);end=next(at for at in starts if at>begin)
        out=subprocess.run([str(dumpbin),'/DISASM:BYTES',f'/RANGE:0x{begin:x},0x{end:x}',str(WS/link['executable']['file'])],capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW);require(not out.returncode,'Own decode')
        path=WS/'artifacts/client455-progress'/('messages111-'+str(len(decoded))+'.txt');path.write_bytes(out.stdout);rows=[]
        for line in out.stdout.decode(errors='replace').splitlines():
            match=re.match(r'^\s+([0-9A-F]{8}): ((?:[0-9A-F]{2} )+)\s+(\w+)\s*(.*?)\s*$',line)
            if not match:continue
            at=int(match[1],16);code=bytes.fromhex(match[2])
            if at>=end:continue
            require(code==read_va(own,at,len(code)),'Own decoded bytes')
            if match[3] in ['call','jmp'] and len(code)==5 and code[0] in [0xe8,0xe9]:rows.append(dict(rva=hex(at-base),target_rva=hex(at+5+struct.unpack('<i',code[1:])[0]-base)))
        decoded.append(dict(function=name,rva=hex(begin-base),disassembly=record(path),calls=rows));return rows
    def target(name):return hex(symbol(mapping,name)-base)
    def at(rows,name):
        hits=[int(row['rva'],16) for row in rows if row['target_rva']==target(name)];require(len(hits)==1,'Unique own edge '+name);return hits[0]
    at(calls('?_SetSystemMsg@@YAXPBDZZ'),'?RF455_ShowSystemMessageV@@YAXPBDPAD@Z')
    at(calls('?Render@CGP_LogIn@@MAEJXZ'),'?Draw@RF455LoginMessages@@QBEXXZ')
    at(calls('?SetTypedHover455@CBoardManager@@QAEPAVCBoardObject@@PAV2@@Z'),'?RF455_CancelNuclearForHover@@YAXXZ')
    cancel=calls('?RF455_CancelNuclearForHover@@YAXXZ');require(at(cancel,'?Clear@RF455NuclearAiming@@QAEXXZ')<at(cancel,'?RF455_ShowSystemMessage@@YAXPBDZZ'),'Own clear before localized output')
    centers=re.findall(r'^\s+0001:[0-9a-fA-F]+\s+(\?center@\?A\S+)\s+[0-9a-fA-F]+\s+f\s+RFClient455Facade:client455_message_dispatch.obj',mapping,re.M);require(len(centers)==1,'Unique source center adapter')
    formatted=calls('?RF455_ShowSystemMessageV@@YAXPBDPAD@Z');require(at(formatted,centers[0])<at(formatted,'?RF455_DispatchMessage@@YAXABURF455MessageContext@@PBDEE@Z'),'Own center before common');at(calls(centers[0]),'?Add@RF455CenterMessages@@QAEXPBDK@Z')
    require('?InsertText455@CGUIChatWindow@@' in mapping and '?RF455_BeginNuclearSelection@@' not in mapping,'Real insert now retained; CE7 UI producer still absent')
    native=checked_native('client455-message-dispatch-native',link_hash);require(native['script_sha256']==sha(WS/'scripts/probe_client455_message_dispatch.py') and native['source']['sha256']==sha(WS/'scripts/native/client455_message_dispatch_probe.cpp') and native['builder_sha256']==sha(WS/'scripts/client455_own_probe.py') and native['reference_sha256']==sha(WS/'inventory/client455-message-dispatch-reference.json'),'Native provenance')
    for row in [native['source'],native['console'],native['persisted_settings']]+native['inputs']:check(row)
    result=native['native'];require(result['checks']==83 and result['GPU_frames']==5 and result['pixels']==[1184,4375,1916,4401,0] and 0<result['cancelled_effects_drain']<300,'Selected native83/GPU domain')
    for key in ['actual_MainApp_context','ordinary_formatted_entry','actual_Login_member','actual_four_chat_panes','Tutorial_kernel_only','signed_counter','live_Avatar_typed_item_hover_cancel','real_BSP_effect6_Miles','real_C1A_CE7_dispatch','repeat_CE7_retains_effect']:require(result[key],'Native '+key)
    for key in ['CE7_game_action_registration','full_Login_auth_flow','full_Tutorial','full_client']:require(not result[key],'Unjustified acceptance '+key)
    center=checked_native('client455-center-messages-native',link_hash);hover=checked_native('client455-board-hover-native',link_hash);status=checked_native('client455-player-status-native',link_hash);require(center['native']['checks']==69 and status['native']['checks']==62,'Selected regressions')
    for name,report,count in [('message-dispatch',native,5),('center-messages',center,4),('board-hover',hover,6)]:
        review=load(f'client455-{name}-visual-review');require(review['reviewed'] and review['reviewed_frames']==count and review['frames']==report['frames'] and review['native_sha256']==sha(WS/f'inventory/client455-{name}-native.json'),'Viewed '+name);check(review['sheet'])
        for row in report['frames']:check(row);check(row['preview'])
    baselines=[]
    for name,report,count in [('board-hover',hover,6),('center-messages',center,4)]:
        path=WS/f'artifacts/client455-progress/client455-{name}-native-before111.json';before={Path(row['file']).name:row for row in json.loads(path.read_text())['frames']};require(len(before)==len(report['frames'])==count,'Regression frame coverage')
        for row in report['frames']:check(before[Path(row['file']).name]);require(row['sha256']==before[Path(row['file']).name]['sha256'],'Regression pixels changed')
        baselines.append(record(path))
    early,ui=load('client455-startup-native'),load('client455-ui-startup-native');require(early['normal_link_sha256']==ui['normal_link_sha256']==link_hash and early['sound_return']==1 and not early['debugger_exit'] and not ui['debugger_exit'] and ui['completed_existing_client_create'] and any(row['name']=='after_client_create' and row['eax']==1 for row in ui['markers']) and all(row['first_chance']==1 for row in ui['exceptions']),'Exact own Create1');check(early['events']);check(ui['events'])
    engine=load('client455-startup-engine-build');require(sha(WS/engine['library'])==engine['library_sha256']=='546a7529b51139e856b1a108fcad7849c14b2d00563b7abbfdcc8db10026fa5a','Engine unchanged');check(engine['baseline_library'])
    previous_path=WS/'artifacts/client455-progress/client455-chat-checkpoint-before111.json';previous=json.loads(previous_path.read_text());historical={key:value for key,value in previous['historical_not_rerun'].items() if key!='player-status-native'}
    historical['chat-native-109']=record(WS/'artifacts/client455-progress/client455-chat-native-before111.json');historical['chat-review-109']=record(WS/'artifacts/client455-progress/client455-chat-visual-review-before111.json')
    for row in historical.values():check(row)
    fresh=['message-dispatch-reference','message-dispatch-native','message-dispatch-visual-review','center-messages-native','center-messages-visual-review','board-hover-native','board-hover-visual-review','player-status-native','normal-preparation','normal-build','normal-consumers','normal-link','own-entry','startup-audit','startup-native','ui-startup-native']
    report=dict(status='PARTIAL',scope=native['scope'],script_sha256=sha(Path(__file__)),sources=sources,generated_providers=providers,normal_link_sha256=link_hash,normal_executable=link['executable'],own_decoded_edges=decoded,native_checks=83,center_regression_checks=69,status_regression_checks=62,viewed_GPU_frames=15,byte_equal_prior_center_hover_frames=10,baselines=baselines,actual_MainGame_C1A_dispatch=True,live_pending1_hover_cancel=True,ordinary_InsertText455_retained=True,CE7_core_in_full_object_lab=True,CE7_game_action_registration=False,full_Login_auth_flow=False,actual_Tutorial=False,full_chat_UI=False,previous109_checkpoint=record(previous_path),previous109_runtime_gate='HISTORICAL',historical_not_rerun=historical,fresh_evidence={name:record(WS/f'inventory/client455-{name}.json') for name in fresh},derived_engine_unchanged=engine['library_sha256'],unchanged_bulk_suites_rerun=False,other32_GUI_frames_rerun=False,gaps=['CE7 game-action registration/callback missing;helper stripped from ordinary PE until next112 caller restoration','Actual Tutorial/fourstage factory,full Login/auth/secondaryUI/stage teardown and remaining legacy chat/ID overload callers still open','Selected providers checked before mutation outside unsafe domain;formatted cap1024/privateABI/CRTstartup/OOM/reentrancy/concurrency/unsafe buffers not fully accepted','All prior client-acceptance gaps remain mandatory'],input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-message-dispatch-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n');print('PARTIAL:ordinary formatter/Login/real4pane/C1A livehover83/center69/status62/15viewedGPU;CE7registration/Tutorial/fullstages/M9OPEN')


if __name__=='__main__':main()
