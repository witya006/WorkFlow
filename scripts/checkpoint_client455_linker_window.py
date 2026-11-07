"""Validate banked window runtime without claiming complete Linker/game behavior."""
import hashlib,json,re
from pathlib import Path
from audit_client455_item_payloads import record
from build_client455_x87_math import read_va
from checkpoint_client455_rvp_effects import check,load,require,sha
from checkpoint_client455_item_icon_metadata import checked_native
from client455_normal_link_evidence import validate_normal_link
from compare_client_binaries import WS,pe

def frame_hashes(report):return {Path(r['file']).name:r['sha256'] for r in report['frames']}

def main():
    ref=load('client455-linker-window-reference');require(ref['script_sha256']==sha(WS/'scripts/audit_client455_linker_window.py') and len(ref['assembly'])==36 and ref['actual_instructions']==3509 and ref['decoded_integer_geometry']==[481,46,44,24] and ref['decoded_glyph_indexes']==list(range(10,19)),'Static coverage/provenance')
    for row in ref['raw_evidence']+ref['inputs']+ref['fixtures']:check(row)
    pins=json.loads((WS/'config/client-target.json').read_text())
    for folder,key,pin in zip(['current','reference-backup'],['behavior_reference','secondary_reference'],ref['references']):
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';raw=path.read_bytes();require(sha(path)==pin['sha256']==pins[key]['sha256'] and pe(raw)['architecture']=='x86' and len(pin['ranges'])==51,'Reference identity')
        for row in pin['ranges']+pin['external_assembly_windows']:require(hashlib.sha256(read_va(raw,0x400000+int(row['rva'],16),row['bytes'])).hexdigest()==row['sha256'],'Static range drift')
    require(ref['references'][0]['ranges']==ref['references'][1]['ranges'],'Pin mismatch')
    session=WS/'artifacts/client455-progress/linker-window097-session.json';state=json.loads(session.read_text());require(state['closed']['success'] and state['closed']['saved'] and state['after']['count']==0,'IDA cleanup')
    message_session=WS/'artifacts/client455-progress/linker-window097-message-assembly.json';message_state=json.loads(message_session.read_text());require(message_state['closed']['success'] and message_state['closed']['saved'] and message_state['after']['count']==0 and ref['active_bank_signed_branch']['opcode']=='7d','Signed message evidence/session cleanup')
    link=load('client455-normal-link');require(validate_normal_link(link)=='PASS' and link['client_objects']==182 and not link['unique_unresolved'],'Normal link');link_hash=sha(WS/'inventory/client455-normal-link.json');prep=load('client455-normal-preparation')
    require(prep['script_sha256']==sha(WS/'scripts/prepare_client455_normal.py') and prep['linker_window_port_sha256']==sha(WS/'scripts/client455_linker_window_port.py'),'Migration provenance')
    sources=[record(WS/'scripts/native'/name) for name in ['client455_linker_window.h','client455_linker_window.cpp','client455_image_text.h','client455_image_text.cpp','client455_linker_owners.h','client455_linker_owners.cpp']]
    for row in sources:require(prep['record_inputs'][Path(row['file']).name]==row['sha256'],'Prepared source drift')
    check(dict(file=prep['manifest'],sha256=prep['manifest_sha256']));manifest=json.loads((WS/prep['manifest']).read_text());selected=[]
    for suffix in ['source/gameobject/board/common/clinkboard.h','source/gameobject/board/common/clinkboard.cpp','generated/client455_linker_window.cpp','generated/client455_image_text.cpp']:
        rows=[r for r in manifest if r['file'].lower().endswith('/'+suffix)];require(len(rows)==1,'Prepared window missing '+suffix)
        for row in rows:check(row);check(dict(file=row['input'],sha256=row['input_sha256']))
        selected+=rows
    header=(WS/next(r['file'] for r in selected if r['file'].lower().endswith('/clinkboard.h'))).read_bytes();require(b'CGUILinkWindow455\t\tm_uiLinkWindow;' in header,'Legacy window still ordinary member')
    normal_map=(WS/link['map']['file']).read_text()
    for symbol,provider in [('Init@CGUILinkWindow455','client455_linker_window.obj'),('MouseEvent@CGUILinkWindow455','client455_linker_window.obj'),('Layout455@CGUILinkWindow455','client455_linker_window.obj'),('Draw@CGUIImageText455','client455_image_text.obj'),('registerIcon@RF455IconLinks','client455_icon_links.obj')]:require(re.search(re.escape(symbol)+r'[^\r\n]*RFClient455Facade:'+re.escape(provider),normal_map),'Normal provider missing '+symbol)
    run=checked_native('client455-linker-window-native',link_hash);require(run['script_sha256']==sha(WS/'scripts/probe_client455_linker_window.py') and run['builder_sha256']==sha(WS/'scripts/client455_own_probe.py') and run['reference_sha256']==sha(WS/'inventory/client455-linker-window-reference.json') and run['architecture']=='x86','Native provenance');check(run['source']);check(run['console'])
    for row in run['inputs']:check(row)
    actual={r['file'].split('/linker-window-')[-1].split('/',1)[-1]:r['sha256'] for r in run['inputs']}
    for row in ref['inputs']+ref['fixtures']:
        relative=row.get('runtime_relative','SpriteImage/Common/'+Path(row['file']).name if Path(row['file']).suffix=='.spr' else Path(row['file']).name);require(actual.get(relative)==row['sha256'],'Runtime path/oracle mismatch '+relative)
    result=run['native'];require((result['layout_cases'],result['actual_icon_geometry'],result['bank_cycle_cases'],result['event_cases'],result['glyph_cases'],result['actual_owned_icons'],result['real_originals'],result['GPU_frames'])==(21,1050,320,48,1792,50,16,8),'Native domain coverage')
    for key in ['actual_Window_Init_Draw_MouseEvent','actual_PostMessage','Use_callback_recording','actual_board_bank_notification','all_owners_released','sprite_allocator_balanced','typed_timer_explicit_refusal']:require(result[key],'Actual contract missing '+key)
    require(not result['actual_gameplay_item_actions'] and not result['full_Linker'] and not result['full_client'],'Unjustified game completion')
    review=load('client455-linker-window-visual-review');require(review['native_sha256']==sha(WS/'inventory/client455-linker-window-native.json') and review['script_sha256']==sha(WS/'scripts/review_client455_linker_window.py') and review['reviewed'] and review['reviewed_frames']==8 and review['frames']==run['frames'],'Visual provenance');check(review['sheet'])
    for row in review['frames']:check(row);check(row['preview'])
    require(len(set(frame_hashes(run).values()))==8,'No visible control/clip differences')
    inherited=[]
    for name,old_path,review_name in [('client455-linker-owners-native','linker-owners096-before097.json','client455-linker-owners-visual-review'),('client455-item-icon-metadata-native','item-metadata094-before095.json','client455-item-icon-metadata-visual-review')]:
        current=checked_native(name,link_hash);baseline=WS/'artifacts/client455-progress'/old_path;old=json.loads(baseline.read_text());old_review=load(review_name)
        require(old_review['native_sha256']==sha(baseline) and old_review['reviewed'] and old_review['reviewed_frames']==3 and old['frames']==old_review['frames'],'Previous visual baseline');check(old_review['sheet'])
        require(frame_hashes(current)==frame_hashes(old) and len(current['frames'])==3 and current['native']==old['native'],'Owner/metadata regression')
        require(current['source']['sha256']==old['source']['sha256'] and current['script_sha256']==old['script_sha256'],'Regression driver/source drift')
        for row in current['frames']:check(row);check(row['preview'])
        inherited.append(dict(current=name,baseline=record(baseline),visual=record(WS/f'inventory/{review_name}.json'),raw_frames_byte_equal=True))
    checked_native('client455-hotbar-native',link_hash);checked_native('client455-account-native',link_hash);storage=load('client455-storage-native');require(storage['normal_link_sha256']==link_hash and len(storage['runs'])==3 and all(not r['natural_exit'] and r['native']['registered']==17 for r in storage['runs']),'Storage regression')
    for case in storage['runs']:
        for key in ['exe','fixture','console']:check(case[key])
    early=load('client455-startup-native');ui=load('client455-ui-startup-native');require(early['normal_link_sha256']==ui['normal_link_sha256']==link_hash and not early['debugger_exit'] and not ui['debugger_exit'] and early['sound_return']==1 and ui['completed_existing_client_create'] and any(r['name']=='after_client_create' and r['eax']==1 for r in ui['markers']) and all(r['first_chance']==1 for r in ui['exceptions']),'Exact PE Create');check(early['events']);check(ui['events'])
    engine=load('client455-startup-engine-build');require(sha(WS/engine['library'])==engine['library_sha256']=='9caa283a6bf8a2fa1c9a05251b6cad451296bb03bda8a1860c22a872e88fe769','Engine drift')
    fresh_names=['client455-normal-preparation','client455-normal-build','client455-normal-consumers','client455-own-entry','client455-startup-audit','client455-startup-native','client455-ui-startup-native','client455-hotbar-native','client455-storage-native','client455-account-native','client455-item-icon-metadata-native','client455-linker-owners-native','client455-linker-window-visual-review']
    report=dict(status='PARTIAL',scope=ref['scope'],script_sha256=sha(Path(__file__)),reference_sha256=sha(WS/'inventory/client455-linker-window-reference.json'),native_sha256=sha(WS/'inventory/client455-linker-window-native.json'),sources=sources,generated_providers=selected,session=record(session),normal_link_sha256=link_hash,normal_executable=link['executable'],fresh_evidence={name:sha(WS/f'inventory/{name}.json') for name in fresh_names},selected_ranges=51,assembly_instructions=3509,layout_cases=21,actual_icon_geometry=1050,cycle_cases=320,event_cases=48,glyph_cases=1792,viewed_GPU_frames=8,ordinary_window_binding=True,gameplay_use_callback_recording=True,actual_gameplay_item_actions=False,inherited_visual_evidence=inherited,
        previous096gate='historical runtime after source/link/reports changed;static ownership proofs retained',unchanged_world_audio_159k_093atlas_092icon_2013owner_1447SF_095manual_suites_rerun=False,gaps=ref['gaps'],input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-linker-window-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n');print('PARTIAL:actualbankedwindow/layout21/cycle320/events48/glyph1792/8viewedGPU/6oldframes-equal/exactPECreate1;fullactions-timers-livecallbacks-Macro-game-M9OPEN')
if __name__=='__main__':main()
