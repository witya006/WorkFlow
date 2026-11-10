"""Record actual Recall source/native/live progress without accepting wholeAnimus orM9."""
import hashlib,json,re,struct
from pathlib import Path
from compare_client_binaries import WS
from build_client455_x87_math import read_va
from checkpoint_client455_rvp_effects import sha,check,require
from client455_normal_link_evidence import validate_normal_link

def record(path):return dict(file=path.relative_to(WS).as_posix(),sha256=sha(path))
def load(name):return json.loads((WS/'inventory'/f'client455-{name}.json').read_text())
def main():
    link=load('normal-link');require(validate_normal_link(link)=='PASS','Current normal PE');digest=sha(WS/'inventory/client455-normal-link.json')
    ref,native,visual,live=[load(name) for name in ['recall-reference','recall-native','recall-visual','character-selection-live-taiwan-native']]
    for item in [ref['raw'],ref['script']]+ref['sources']+[p['raw'] for p in ref['additional_references']]:check(item)
    require(ref['total_full_functions']==39 and ref['total_full_instructions']==3039,'Both-pin full Recall references')
    require(native['normal_link_sha256']==live['normal_link_sha256']==visual['normal_link_sha256']==digest,'Exact current runtime reports')
    require(native['status']=='PASS' and native['natural_exit']==0 and native['native']['status']=='PASS' and native['native']['rows']==8,'Actual ordinary window/row methods')
    for item in native['sources']+native['inputs']+[native['script']]:check(item)
    require(visual['status']=='REVIEWED_PARTIAL' and visual['frames']==native['frames'] and visual['native_report']['sha256']==sha(WS/'inventory/client455-recall-native.json') and len(native['frames'])==5,'Five exact inspected GPU frames')
    for item in native['frames']:check(item);check(item['preview'])
    require(live['first_login_frame_captured'] and live['login_render_returned_after_capture'] and live['live_server']['private_handoff_removed'],'Ordinary pre-Enter frame andhandoff cleanup')
    for key in ['events','captured_frame','capture_metadata']:check(live[key])
    require(any(x.get('own_child_validated') and x.get('sent') for x in live['selection_input']),'Addressed own Enter')
    for value in ['RF455 Protocol:tx:1:14:1','RF455 Protocol:rx:1:15:22','RF455 Protocol:select-result:0:0:0']:require(value in live['protocol_observations'],'Actual live selection '+value)
    fatal=[x for x in live['exceptions'] if not x.get('first_chance')];require(len(fatal)==1 and fatal[0]['code']=='0xc0000005','Next actual failure retained')
    symbols=[]
    for line in (WS/link['map']['file']).read_text().splitlines():
        m=re.match(r'^\s+[\da-fA-F]+:[\da-fA-F]+\s+(\S+)\s+([\da-fA-F]{8})\b',line)
        if m:symbols.append((int(m[2],16)-0x400000,m[1]))
    def resolve(address):
        start,name=max((a,n) for a,n in symbols if a<=address);return dict(rva=hex(address),symbol=name,offset=hex(address-start))
    events=[json.loads(line) for line in (WS/live['events']['file']).read_text().splitlines()]
    context=next(x for x in events if x['kind']=='fatal_context');require(context.get('readable_stack_words',0)>0 and context['own_stack_rva_candidates'],'Readable actual stack evidence')
    resolved=[resolve(int(fatal[0]['rva'],16))]+[dict(resolve(int(x['rva'],16)),stack_offset=x['stack_offset']) for x in context['own_stack_rva_candidates'][:18]]
    require(any('SetSprite@CGUIMobControl' in x['symbol'] for x in resolved) and any('Init@CGUIMobControl' in x['symbol'] for x in resolved),'Actual next MobControl failure')
    candidates=[x for x in resolved if 'Create_UI@CGP_MainGame' in x['symbol']];require(candidates,'Actual Create_UI caller candidate')
    tables=[(a,n) for a,n in symbols if n=='??_7CGUIMobControl@@6BCGUIContainer@@@'];require(len(tables)==1,'Own MobControl primary vtable')
    raw=(WS/link['executable']['file']).read_bytes();target=struct.unpack('<I',read_va(raw,0x400000+tables[0][0]+0x6c,4))[0]-0x400000
    require('Init@CGUIMobControl' in resolve(target)['symbol'] and resolve(target)['offset']=='0x0','Actual MobControl Init slot')
    calls=[]
    for row in candidates:
        ret=int(row['rva'],16);instruction=read_va(raw,0x400000+ret-3,3)
        if instruction==b'\xff\x50\x6c':calls.append(dict(return_rva=hex(ret),instruction_rva=hex(ret-3),bytes=instruction.hex(),vtable_rva=hex(tables[0][0]),slot_offset='0x6c',callee=resolve(target)))
    require(calls,'Actual caller instruction corroborated by vtable andfatal inner methods')
    source=WS/'work/client455-port/normal/source/gameprogress/cgp_maingame.cpp';body=source.read_bytes();require(body.index(b'm_uiSummonsSelectWindow.Init();')<body.index(b'm_uiSummonsControlWindow.Init();'),'Sequential Recall thenMobControl source')
    failure=dict(kind='UNHANDLED_AFTER_SUCCESSFUL_SELECTION',own_rva=fatal[0]['rva'],code=fatal[0]['code'],resolved_stack_candidates=resolved,stack_is_candidate_scan_not_unwind=True,verified_own_virtual_calls=calls,cause='Next oldCGUIMobControl::SetSprite/Init numeric sprite consumer;Recall Init returned on the sequential MainGame::Create_UI path',whole_client_run_succeeded=False)
    selected=[(0x6ae7b0,'CGUIRecallUnit','CGUIRecallUnit'),(0x6aee90,'CGUIRecallUnit','SetSprite'),(0x6aef80,'CGUIRecallUnit','SetUnitState'),(0x6af050,'CGUIRecallUnit','SetMobName'),(0x6af080,'CGUIRecallUnit','SetLevel'),(0x6af0e0,'CGUIRecallUnit','SetItem'),(0x6af140,'CGUIRecallUnit','SetHP'),(0x6af200,'CGUIRecallUnit','SetFP'),(0x6af2c0,'CGUIRecallUnit','SetExp'),(0x6af7f0,'CGUIRecallWindow','Init'),(0x6afc20,'CGUIRecallWindow','SetSprite'),(0x6afc90,'CGUIRecallWindow','SetBound'),(0x6afdf0,'CGUIRecallWindow','TakeInItem'),(0x6b0020,'CGUIRecallWindow','TakeOutItem'),(0x6b0340,'CGUIRecallWindow','UpdateScrollbar'),(0x6b0480,'CGUIRecallWindow','GetRecallUnitByIndex'),(0x6b0530,'CGUIRecallWindow','GetRecallUnitByItemID'),(0x6b05f0,'CGUIRecallWindow','GetRecallUnitByEventObj'),(0x6b0680,'CGUIRecallWindow','MouseEvent'),(0x6b08a0,'CGUIRecallWindow','ScrollEvent'),(0x6b0160,'CGUIRecallWindow','SetLevel'),(0x6b01b0,'CGUIRecallWindow','SetHP'),(0x6b0220,'CGUIRecallWindow','SetFP'),(0x6b0290,'CGUIRecallWindow','SetExp'),(0x6b02f0,'CGUIRecallWindow','SetItemState')]
    bindings=[]
    for address,klass,name in selected:
        prefix='??0'+klass+'@@' if klass==name else '?'+name+'@'+klass+'@@';found=[hex(a) for a,n in symbols if n.startswith(prefix)]
        bindings.append(dict(rva=hex(address-0x400000),symbol=klass+'::'+name,source=record(WS/'scripts/native/client455_recall_window.inc'),ordinary_symbol_rvas=found,standalone_symbol_retained=bool(found),retained_in_ordinary_executable=True if found else None,scope='Actual row methods tested with controlled records;ordinary windowInit returned;wholeAnimus/providers/edge domains not accepted',complete_equivalence=False))
    report=dict(schema_version=1,reference_sha256=ref['references'][0]['sha256'],architecture='x86',image_base='0x400000',normal_executable=link['executable'],functions=bindings)
    (WS/'inventory/client455-recall-bindings.json').write_text(json.dumps(report,indent=2)+'\n')
    names=['recall-reference','recall-native','recall-visual','recall-bindings','normal-preparation','normal-build','normal-consumers','normal-link','own-entry','startup-audit','startup-taiwan-native','live-launcher-native','character-selection-live-taiwan-native','live-server']
    gate=dict(status='PARTIAL_KNOWN_FAILURE',scope='Actual455Recall window/rows integrated;ordinary RecallInit returned after live selection,next oldMobControl fails;world not entered',script=record(Path(__file__)),normal_link_sha256=digest,normal_executable=link['executable'],runtime_login_report=record(WS/'inventory/client455-character-selection-live-taiwan-native.json'),fresh_evidence={name:record(WS/f'inventory/client455-{name}.json') for name in names},prior_runtime=record(WS/'artifacts/client455-progress/before162/manifest.json'),post_selection_failure=failure,ordinary_Recall_connected=True,live_advanced_past_prior_Recall_crash=True,live_selection_exchange_completed=True,main_game_ui_created=False,world_entered=False,full_client=False,explicit_function_bindings=len(bindings),component_frames_visually_inspected=True,source_Create_UI=record(source),gaps=ref['gaps']+['Next oldMobControl window,not yet accepted'],private_handoff_removed=True,input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-recall-checkpoint.json').write_text(json.dumps(gate,indent=2)+'\n')
    file=WS/'inventory/client-features.json';registry=json.loads(file.read_text())
    for entry in registry['features']:
        if entry.get('runtime_gate_current'):entry['runtime_gate_current']=False
    feature=dict(id='CLIENT455-RECALL-162',status='partial',runtime_gate_current=True,runtime_gate_last_verified=True,description=gate['scope'],implementation=['scripts/client455_recall_port.py','scripts/native/client455_recall_window.h','scripts/native/client455_recall_window.inc'],evidence=['inventory/client455-recall-checkpoint.json','inventory/client455-recall-reference.json'],world_entered=False,full_client=False,M6='OPEN',M9='OPEN')
    indices=[i for i,x in enumerate(registry['features']) if x['id']==feature['id']]
    if indices:registry['features'][indices[0]]=feature
    else:registry['features'].append(feature)
    file.write_text(json.dumps(registry,ensure_ascii=False,indent=2)+'\n');print('PARTIAL_KNOWN_FAILURE:Recall455/8controlledrows/5GPUframes/liveInit pass;nextMobControl failure;world/M9OPEN')
if __name__=='__main__':main()
