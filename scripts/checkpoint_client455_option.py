"""Record options455 and completed MainGame UI creation;inventory/world remain open."""
import json,struct
from pathlib import Path
from compare_client_binaries import WS
from build_client455_x87_math import read_va
from checkpoint_client455_rvp_effects import sha,check,require
from client455_normal_link_evidence import validate_normal_link
from client455_ui_checkpoint import record,own_symbols

def load(name):return json.loads((WS/'inventory'/f'client455-{name}.json').read_text())

def main():
    link=load('normal-link');require(validate_normal_link(link)=='PASS','Current linked PE');digest=sha(WS/'inventory/client455-normal-link.json')
    ref,native,visual,live,status=[load(name) for name in ['option-reference','option-native','option-visual','character-selection-live-taiwan-native','player-status-native']]
    for item in [ref['raw'],ref['script']]+ref['sources']+ref['helpers']+[p['raw'] for p in ref['additional_references']]:check(item)
    require(ref['total_full_functions']==53 and ref['total_full_instructions']==5879 and len(ref['country_dispatch'])==44,'Both pins and complete graphs')
    require(all(p['normal_link_sha256']==digest for p in [native,visual,live,status]),'Exact current runtime evidence')
    require(native['status']=='PASS' and native['natural_exit']==0 and native['native']['actual_local_message_routes'] and native['native']['GPU_frames']==4,'Ordinary options widget/message/GPU probe')
    for item in native['sources']+native['inputs']+[native['script'],status['source']]:check(item)
    require(status['natural_exit']==0 and status['native']['status']=='PASS' and status['native']['unknown_state_refusal'] and status['native']['pending_zero_allows_hover_clear'] and status['native']['nuclear_refusal_before_mutation'],'Status/hover startup regression')
    require(visual['status']=='REVIEWED_PARTIAL' and visual['frames']==native['frames'] and visual['native_report']['sha256']==sha(WS/'inventory/client455-option-native.json') and len(native['frames'])==4,'Exact four viewed frames')
    for item in native['frames']:check(item);check(item['preview'])
    require(live['first_login_frame_captured'] and live['login_render_returned_after_capture'] and live['live_server']['private_handoff_removed'],'Pre-Enter frame and cleanup')
    for key in ['events','captured_frame','capture_metadata']:check(live[key])
    require(any(x.get('own_child_validated') and x.get('sent') for x in live['selection_input']),'Own HWND selection input')
    for value in ['RF455 Protocol:tx:1:14:1','RF455 Protocol:rx:1:15:22','RF455 Protocol:select-result:0:0:0']:require(value in live['protocol_observations'],'Live selection '+value)
    fatal=[x for x in live['exceptions'] if not x.get('first_chance')];require(len(fatal)==1 and fatal[0]['code']=='0xc0000005' and 'RF_Online.bin' in fatal[0]['module'],'Current own inventory failure')
    symbols=own_symbols(link);raw=(WS/link['executable']['file']).read_bytes()
    def resolve(address):
        start,name=max((a,n) for a,n in symbols if a<=address);return dict(rva=hex(address),symbol=name,offset=hex(address-start))
    events=[json.loads(line) for line in (WS/live['events']['file']).read_text().splitlines()]
    context=next(x for x in events if x['kind']=='fatal_context');require(context.get('readable_stack_words',0)>0,'Actual readable stack')
    resolved=[resolve(int(fatal[0]['rva'],16))]+[dict(resolve(int(x['rva'],16)),stack_offset=x['stack_offset']) for x in context['own_stack_rva_candidates'][:20]]
    for fragment in ['SetSprite@CGUIInventoryWindow','Init@CGUIInventoryWindow','InitWindow@CBaseBoard','InitWindow@CInventoryBoard','Create@CGP_MainGame']:require(any(fragment in x['symbol'] for x in resolved),'Corroborated inventory chain '+fragment)
    table=next(a for a,n in symbols if n=='??_7CGUIInventoryWindow@@6BCGUIContainer@@@')
    init=struct.unpack('<I',read_va(raw,0x400000+table+0x6c,4))[0]-0x400000
    require(resolve(init)['symbol'].startswith('?Init@CGUIInventoryWindow@@') and resolve(init)['offset']=='0x0','Actual inventory Init virtual slot')
    caller=next(x for x in resolved if 'InitWindow@CBaseBoard' in x['symbol']);ret=int(caller['rva'],16)
    require(read_va(raw,0x400000+ret-3,3)==bytes.fromhex('ff506c'),'Actual InitWindow virtual call')
    ui_return=0x26951;code=read_va(raw,0x400000+ui_return-5,5)
    ui=ui_return+struct.unpack('<i',code[1:])[0]
    require(code[0]==0xe8 and resolve(ui)['symbol'].startswith('?Create_UI@CGP_MainGame@@') and resolve(ui)['offset']=='0x0','Own direct Create_UI call')
    current=next(int(x['rva'],16) for x in resolved if 'Create@CGP_MainGame' in x['symbol'])
    require(ui_return<current and read_va(raw,0x400000+current-3,3)==bytes.fromhex('ff5208'),'Create advanced beyond its UI call to board initialization')
    source=WS/'work/client455-port/normal/source/gameprogress/cgp_maingame.cpp';body=source.read_bytes()
    require(body.index(b'Create_UI();')<body.index(b'Create_Board();') and body.index(b'm_uiOptionWindow.Init();')<body.index(b'm_uiChatWindow.InitializeChat455();'),'Sequential UI then board source')
    selected=[(0x710c80,'CGUIOptionWindow'),(0x711080,'~CGUIOptionWindow'),(0x7113c0,'Init'),(0x713060,'SetSprite'),(0x713440,'SetSoundOption'),(0x7134b0,'GetSoundOption'),(0x713530,'SetGraphicOption'),(0x7135d0,'GetGraphicOption'),(0x713610,'SwitchOn'),(0x713690,'IsSwitchOn'),(0x713700,'SelectCamera'),(0x7137c0,'SelectEax455'),(0x713860,'SelectSpecial455'),(0x713900,'MouseEvent'),(0x713eb0,'ScrollEvent'),(0x714210,'Update'),(0x714290,'SetTargetingMode455'),(0x714380,'SetTargetingFilters455'),(0x7143d0,'SetTargetingFilter455'),(0x714480,'GetTargetingMode455'),(0x7144a0,'IsTargetingFilter455')]
    bindings=[]
    for address,name in selected:
        prefix='??0CGUIOptionWindow@@' if name=='CGUIOptionWindow' else '??1CGUIOptionWindow@@' if name=='~CGUIOptionWindow' else '?'+name+'@CGUIOptionWindow@@'
        found=[hex(a) for a,n in symbols if n.startswith(prefix)]
        bindings.append(dict(rva=hex(address-0x400000),symbol='CGUIOptionWindow::'+name,source=record(WS/'scripts/native/client455_option_window.inc'),ordinary_symbol_rvas=found,standalone_symbol_retained=bool(found),retained_in_ordinary_executable=True if found else None,scope='Actual options owner/controls/messages with controlled fields;ordinary UI creation returned;full settings/providers/edge domains open',complete_equivalence=False))
    binding=dict(schema_version=1,reference_sha256=ref['references'][0]['sha256'],architecture='x86',image_base='0x400000',normal_executable=link['executable'],functions=bindings,generator=record(Path(__file__)))
    (WS/'inventory/client455-option-bindings.json').write_text(json.dumps(binding,indent=2)+'\n')
    names=['option-reference','option-native','option-visual','option-bindings','player-status-native','normal-preparation','normal-build','normal-consumers','normal-link','own-entry','startup-audit','startup-taiwan-native','live-launcher-native','character-selection-live-taiwan-native','live-server']
    failure=dict(kind='UNHANDLED_IN_INVENTORY_AFTER_UI_CREATION',own_rva=fatal[0]['rva'],code=fatal[0]['code'],resolved_stack_candidates=resolved,stack_is_candidate_scan_not_unwind=True,verified_own_virtual_call=dict(return_rva=hex(ret),instruction_rva=hex(ret-3),bytes='ff506c',vtable_rva=hex(table),slot_offset='0x6c',callee=resolve(init)),verified_prior_Create_UI_call=dict(return_rva=hex(ui_return),instruction_rva=hex(ui_return-5),callee=resolve(ui)),cause='Old inventory SetSprite/Init during board initialization;ordinary MainGame Create_UI including chat returned',whole_client_run_succeeded=False)
    gate=dict(status='PARTIAL_KNOWN_FAILURE',scope='Options455 controls/messages integrated;ordinary MainGame UI creation returned after accepted live selection;next old inventory initialization fails,world not entered',script=record(Path(__file__)),helpers=[record(WS/'scripts/client455_ui_checkpoint.py')],normal_link_sha256=digest,normal_executable=link['executable'],runtime_login_report=record(WS/'inventory/client455-character-selection-live-taiwan-native.json'),fresh_evidence={name:record(WS/'inventory'/f'client455-{name}.json') for name in names},prior_runtime=record(WS/'artifacts/client455-progress/before164/manifest.json'),post_selection_failure=failure,ordinary_options_connected=True,live_advanced_past_prior_option_crash=True,live_selection_exchange_completed=True,main_game_ui_created=True,full_455_ui_accepted=False,world_entered=False,full_client=False,explicit_function_bindings=len(bindings),component_frames_visually_inspected=True,source_Create_UI=record(source),gaps=ref['gaps']+['Next old CGUIInventoryWindow initialization;world/gameplay not reached'],private_handoff_removed=True,input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-option-checkpoint.json').write_text(json.dumps(gate,indent=2)+'\n')
    path=WS/'inventory/client-features.json';registry=json.loads(path.read_text());features=registry['features']
    for feature in features:
        if feature.get('runtime_gate_current'):feature['runtime_gate_current']=False
    new=dict(id='CLIENT455-OPTIONS-164',area='ui',status='partial',runtime_gate_current=True,evidence=['inventory/client455-option-checkpoint.json','inventory/client455-option-reference.json','inventory/client455-option-native.json'],description=gate['scope'],gaps=gate['gaps'])
    features[:]=[feature for feature in features if feature['id']!=new['id']]+[new];path.write_text(json.dumps(registry,indent=2,ensure_ascii=False)+'\n')
    print('PARTIAL_KNOWN_FAILURE:options455/4GPUframes/messages/status regression/mainUI creation returned;next inventory;world/M9 OPEN')

if __name__=='__main__':main()
