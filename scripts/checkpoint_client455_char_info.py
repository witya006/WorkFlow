"""Keep actual CharInfo progress and the following Recall failure distinct from M9."""
import json,re,struct
from pathlib import Path
from compare_client_binaries import WS
from build_client455_x87_math import read_va
from checkpoint_client455_rvp_effects import sha,check,require
from client455_normal_link_evidence import validate_normal_link

def record(path):return dict(file=path.relative_to(WS).as_posix(),sha256=sha(path))
def load(name):return json.loads((WS/'inventory'/f'client455-{name}.json').read_text())

def main():
    link=load('normal-link');require(validate_normal_link(link)=='PASS','Current normal link');digest=sha(WS/'inventory/client455-normal-link.json')
    ref=load('char-info-reference');native=load('char-info-native');live=load('character-selection-live-taiwan-native')
    for item in [ref['raw'],ref['script']]+ref['sources']+[x['raw'] for x in ref['additional_references']]:check(item)
    require(ref['total_full_functions']==60 and ref['total_full_instructions']==6095,'Both-pin full references')
    require(native['normal_link_sha256']==live['normal_link_sha256']==digest,'Exact current runtime PE')
    require(native['status']=='PASS' and native['natural_exit']==0 and native['native']['status']=='PASS' and native['native']['value_owners']==23 and native['native']['races']==3,'Real ordinary window methods')
    for item in native['sources']+native['inputs']+[native['script']]:check(item)
    require(len(native['frames'])==6,'Six actual GPU frames')
    visual=load('char-info-visual')
    require(visual['status']=='REVIEWED_PARTIAL' and visual['normal_link_sha256']==digest and visual['native_report']['sha256']==sha(WS/'inventory/client455-char-info-native.json'),'Review of exact current images')
    require(visual['frames']==native['frames'],'All six exact reviewed frames')
    for item in native['frames']:
        check(item);check(item['preview'])
    require(live['first_login_frame_captured'] and live['login_render_returned_after_capture'] and live['live_server']['private_handoff_removed'],'Actual Login/render/cleanup')
    for key in ['events','captured_frame','capture_metadata']:check(live[key])
    require(any(x.get('own_child_validated') and x.get('sent') for x in live['selection_input']),'Addressed Enter')
    for value in ['RF455 Protocol:tx:1:14:1','RF455 Protocol:rx:1:15:22','RF455 Protocol:select-result:0:0:0']:require(value in live['protocol_observations'],'Actual selection '+value)
    fatal=[x for x in live['exceptions'] if not x.get('first_chance')];require(len(fatal)==1 and fatal[0]['code']=='0xc0000005','Keep next failure visible')
    symbols=[]
    for line in (WS/link['map']['file']).read_text().splitlines():
        m=re.match(r'^\s+[\da-fA-F]+:[\da-fA-F]+\s+(\S+)\s+([\da-fA-F]{8})\b',line)
        if m:symbols.append((int(m[2],16)-0x400000,m[1]))
    def resolve(address):
        start,name=max((a,n) for a,n in symbols if a<=address);return dict(rva=hex(address),symbol=name,offset=hex(address-start))
    events=[json.loads(line) for line in (WS/live['events']['file']).read_text().splitlines()]
    context=next(x for x in events if x['kind']=='fatal_context');addresses=[int(fatal[0]['rva'],16)]+[int(x['rva'],16) for x in context['own_stack_rva_candidates'][:5]]
    resolved=[resolve(a) for a in addresses];require(any('SetSprite@CGUIRecallWindow' in x['symbol'] for x in resolved) and any('Init@CGUIRecallWindow' in x['symbol'] for x in resolved),'Actual next Recall initialization failure')
    raw=(WS/link['executable']['file']).read_bytes();calls=[]
    for a in addresses[1:]:
        instruction=read_va(raw,0x400000+a-5,5)
        if instruction[0]==0xe8:
            target=a+struct.unpack_from('<i',instruction,1)[0];calls.append(dict(return_rva=hex(a),instruction_rva=hex(a-5),sha256=__import__('hashlib').sha256(instruction).hexdigest(),callee=resolve(target)))
        if 'Create_UI@CGP_MainGame' in resolve(a)['symbol']:
            short=read_va(raw,0x400000+a-3,3)
            if short==b'\xff\x50\x6c':
                tables=[(start,name) for start,name in symbols if name=='??_7CGUIRecallWindow@@6BCGUIContainer@@@']
                require(len(tables)==1,'Own Recall primary vtable')
                target=struct.unpack('<I',read_va(raw,0x400000+tables[0][0]+0x6c,4))[0]-0x400000
                calls.append(dict(return_rva=hex(a),instruction_rva=hex(a-3),instruction_bytes=short.hex(),vtable_rva=hex(tables[0][0]),slot_offset='0x6c',callee=resolve(target),kind='Virtual call corroborated by actual fatal Init stack and own vtable'))
    require(any('Init@CGUIRecallWindow' in x['callee']['symbol'] and x['callee']['offset']=='0x0' for x in calls),'Exact caller instruction/vtable')
    source=WS/'work/client455-port/normal/source/gameprogress/cgp_maingame.cpp';text=source.read_bytes()
    require(text.index(b'm_uiCharInfoWindow.Init();')<text.index(b'm_uiSummonsSelectWindow.Init();'),'Actual sequential source path')
    failure=dict(kind='UNHANDLED_AFTER_SUCCESSFUL_SELECTION',own_rva=fatal[0]['rva'],code=fatal[0]['code'],resolved_own_symbols=resolved,verified_own_calls=calls,cause='Next old CGUIRecallWindow::SetSprite/Init consumer;CharInfo Init has returned on the sequential MainGame::Create_UI path',whole_client_run_succeeded=False)
    rows=[];body=record(WS/'scripts/native/client455_char_info.inc')
    selected=[(0x665f70,'RF455CharInfoView','Init455'),(0x666580,'RF455CharInfoView','SetSprite455'),(0x666690,'RF455CharInfoView','SetBound455'),(0x6669a0,'RF455CharInfoView','SelectPage455'),(0x6667e0,'CGUICharInfoWindow','MouseEvent'),(0x661800,'RF455CharInfoView','InitMain455'),(0x6630c0,'RF455CharInfoView','SetMainSprite455'),(0x6629f0,'RF455CharInfoView','RefreshRace455'),(0x663bc0,'RF455CharInfoView','SetBattle455'),(0x663e40,'RF455CharInfoView','SetMake455'),(0x663d20,'RF455CharInfoView','SetBattleExp455'),(0x663fb0,'RF455CharInfoView','SetMakeExp455'),(0x6640d0,'RF455CharInfoView','SetResist455'),(0x663470,'CGUICharInfoWindow','SetFP'),(0x6634e0,'CGUICharInfoWindow','SetSP'),(0x6637f0,'CGUICharInfoWindow','SetExp'),(0x6633b0,'CGUICharInfoWindow','SetLevel'),(0x6635c0,'CGUICharInfoWindow','SetPvPPoint')]
    for address,klass,name in selected:
        matches=[(a,n) for a,n in symbols if n.startswith('?'+name+'@'+klass+'@@')]
        rows.append(dict(rva=hex(address-0x400000),symbol=klass+'::'+name,source=body,ordinary_symbol_rvas=[hex(a) for a,_ in matches],standalone_symbol_retained=bool(matches),retained_in_ordinary_executable=True if matches else None,ordinary_CharInfo_Init_returned=True,scope='Partial source binding;whole method domains and missing providers remain explicit',complete_equivalence=False))
    prior_bindings=load('tab-board-bindings')['functions'];transitions=[]
    for row in prior_bindings:
        name=row['symbol'].split('::')[-1];prefix='??0CGUITabBoard455@@' if name=='CGUITabBoard455' else '??1CGUITabBoard455@@' if name=='~CGUITabBoard455' else '?'+name+'@CGUITabBoard455@@'
        matches=[hex(a) for a,n in symbols if n.startswith(prefix)]
        transitions.append(dict(reference_rva=row['rva'],symbol=row['symbol'],previous_standalone_retained=False,current_standalone_symbol_rvas=matches,ordinary_owner_path_now_connected=True,note='Absence of a standalone symbol can mean inlining;not a new target function'))
    bindings=dict(schema_version=1,reference_sha256=ref['references'][0]['sha256'],architecture='x86',image_base='0x400000',normal_executable=link['executable'],functions=rows,prior_tab_board_state_transitions=transitions)
    (WS/'inventory/client455-char-info-bindings.json').write_text(json.dumps(bindings,indent=2)+'\n')
    names=['char-info-reference','char-info-native','char-info-visual','char-info-bindings','normal-preparation','normal-build','normal-consumers','normal-link','own-entry','startup-audit','startup-taiwan-native','live-launcher-native','character-selection-live-taiwan-native','live-server']
    gate=dict(status='PARTIAL_KNOWN_FAILURE',scope='Actual455CharInfo source integrated andInit returned after live selection;next oldRecallwindow fails;world not entered',script=record(Path(__file__)),normal_link_sha256=digest,normal_executable=link['executable'],runtime_login_report=record(WS/'inventory/client455-character-selection-live-taiwan-native.json'),fresh_evidence={name:record(WS/f'inventory/client455-{name}.json') for name in names},prior_runtime=record(WS/'artifacts/client455-progress/before161/manifest.json'),post_selection_failure=failure,ordinary_CharInfo_connected=True,live_advanced_past_prior_CharInfo_crash=True,live_selection_exchange_completed=True,main_game_ui_created=False,world_entered=False,full_client=False,explicit_function_bindings=len(rows),tab_board_prior_binding_transitions=transitions,component_frames_visually_inspected=True,final_frames_identical_to_inspected=True,source_Create_UI=record(source),gaps=ref['gaps']+['Next oldRecall/SummonsSelect window,not yet accepted'],private_handoff_removed=True,input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-char-info-checkpoint.json').write_text(json.dumps(gate,indent=2)+'\n')
    file=WS/'inventory/client-features.json';registry=json.loads(file.read_text())
    for row in registry['features']:
        if row.get('runtime_gate_current'):row['runtime_gate_current']=False
    feature=dict(id='CLIENT455-CHARINFO-161',status='partial',runtime_gate_current=True,runtime_gate_last_verified=True,description=gate['scope'],implementation=['scripts/client455_char_info_port.py','scripts/native/client455_char_info.h','scripts/native/client455_char_info.inc'],evidence=['inventory/client455-char-info-checkpoint.json','inventory/client455-char-info-reference.json'],world_entered=False,full_client=False,M6='OPEN',M9='OPEN')
    indices=[i for i,x in enumerate(registry['features']) if x['id']==feature['id']]
    if indices:registry['features'][indices[0]]=feature
    else:registry['features'].append(feature)
    file.write_text(json.dumps(registry,ensure_ascii=False,indent=2)+'\n')
    print('PARTIAL_KNOWN_FAILURE:CharInfo455/3pages/23owners/nativeGPU/liveInit passed;nextRecall failure;world/M9OPEN')

if __name__=='__main__':main()
