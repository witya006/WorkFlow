"""Record real MobControl/shared movement progress,not full455Animus orworld."""
import json
from pathlib import Path
from compare_client_binaries import WS
from checkpoint_client455_rvp_effects import sha,check,require
from client455_normal_link_evidence import validate_normal_link
from client455_ui_checkpoint import record,own_symbols,corroborate_next_window

def load(name):return json.loads((WS/'inventory'/f'client455-{name}.json').read_text(encoding='utf-8-sig'))
def main():
    link=load('normal-link');require(validate_normal_link(link)=='PASS','Current normal PE');digest=sha(WS/'inventory/client455-normal-link.json')
    ref,native,visual,live=[load(name) for name in ['mob-control-reference','mob-control-native','mob-control-visual','character-selection-live-taiwan-native']]
    for item in [ref['raw'],ref['script']]+ref['sources']+[p['raw'] for p in ref['additional_references']]:check(item)
    require(ref['total_full_functions']==34 and ref['total_full_instructions']==3119 and len(ref['country_dispatch'])==22,'Both-pin complete MobControl/dependency references')
    require(native['normal_link_sha256']==live['normal_link_sha256']==visual['normal_link_sha256']==digest,'Exact current runtime reports')
    require(native['status']=='PASS' and native['natural_exit']==0 and native['native']['status']=='PASS' and native['native']['actual_message_routes']==3 and native['native']['shared_movement'],'Actual ordinary methods,movement andmessages')
    for item in native['sources']+native['inputs']+[native['script']]:check(item)
    require(visual['status']=='REVIEWED_PARTIAL' and visual['frames']==native['frames'] and visual['native_report']['sha256']==sha(WS/'inventory/client455-mob-control-native.json') and len(native['frames'])==4,'Four exact inspected GPU frames')
    for item in native['frames']:check(item);check(item['preview'])
    failure,source=corroborate_next_window(link,live,'CGUIOptionWindow','m_uiSummonsControlWindow.Init();','m_uiOptionWindow.Init();')
    selected=[(0x6acfa0,'CGUIMobControl','CGUIMobControl'),(0x6ad1e0,'CGUIMobControl','~CGUIMobControl'),(0x6ad3c0,'CGUIMobControl','Init'),(0x6ada40,'CGUIMobControl','SetSprite'),(0x6adbd0,'CGUIMobControl','SetMobName'),(0x6adc60,'CGUIMobControl','SetLevel'),(0x6adcf0,'CGUIMobControl','SetHP'),(0x6addd0,'CGUIMobControl','SetFP'),(0x6adeb0,'CGUIMobControl','SetExp'),(0x6ae080,'CGUIMobControl','SetResource455'),(0x6ae310,'CGUIMobControl','MouseEvent'),(0x6ae560,'CGUIMobControl','IsCrossed'),(0x6ae5b0,'CGUIMobControl','OpenCmdBoard'),(0x6ae720,'CGUIMobControl','Update'),(0x7b4670,'CGUIMoveObjectMgr','AddMoveObject455'),(0x7b4760,'CGUIMoveObjectMgr','StartMoveAt455'),(0x7b4840,'CGUIMoveObjectMgr','RemoveObject'),(0x7b48e0,'CGUIMoveObjectMgr','RemoveAllObject'),(0x7b4960,'CGUIMoveObjectMgr','IsFinishedMove'),(0x7b49f0,'CGUIMoveObjectMgr','FrameMoveAt455'),(0x7b4d30,'CGUIMoveObjectMgr','GetMoveObject'),(0x7b4db0,'CGUIMoveObjectMgr','GetMoveFinishedObject')]
    symbols=own_symbols(link);bindings=[]
    for address,klass,name in selected:
        prefix=('??0'+klass+'@@') if name==klass else ('??1'+klass+'@@') if name=='~'+klass else '?'+name+'@'+klass+'@@';found=[hex(a) for a,n in symbols if n.startswith(prefix)]
        bindings.append(dict(rva=hex(address-0x400000),symbol=klass+'::'+name,source=record(WS/('scripts/native/client455_gui_move.inc' if klass=='CGUIMoveObjectMgr' else 'scripts/native/client455_mob_control.inc')),ordinary_symbol_rvas=found,standalone_symbol_retained=bool(found),retained_in_ordinary_executable=True if found else None,scope='Actual owners/movement/messages tested with controlled fields;ordinaryMobControlInit returned;wholeAnimus/providers/tooltip/edge domains not accepted',complete_equivalence=False))
    report=dict(schema_version=1,reference_sha256=ref['references'][0]['sha256'],architecture='x86',image_base='0x400000',normal_executable=link['executable'],functions=bindings,generator=record(Path(__file__)),helpers=[record(WS/'scripts/client455_ui_checkpoint.py')])
    (WS/'inventory/client455-mob-control-bindings.json').write_text(json.dumps(report,indent=2)+'\n')
    names=['mob-control-reference','mob-control-native','mob-control-visual','mob-control-bindings','normal-preparation','normal-build','normal-consumers','normal-link','own-entry','startup-audit','startup-taiwan-native','live-launcher-native','character-selection-live-taiwan-native','live-server']
    gate=dict(status='PARTIAL_KNOWN_FAILURE',scope='Actual455MobControl andshared GUI movement integrated;ordinaryMobControlInit returned after live selection,next oldOption fails;world not entered',script=record(Path(__file__)),helpers=report['helpers'],normal_link_sha256=digest,normal_executable=link['executable'],runtime_login_report=record(WS/'inventory/client455-character-selection-live-taiwan-native.json'),fresh_evidence={name:record(WS/'inventory'/f'client455-{name}.json') for name in names},prior_runtime=record(WS/'artifacts/client455-progress/before163/manifest.json'),post_selection_failure=failure,ordinary_MobControl_connected=True,live_advanced_past_prior_MobControl_crash=True,live_selection_exchange_completed=True,main_game_ui_created=False,world_entered=False,full_client=False,explicit_function_bindings=len(bindings),component_frames_visually_inspected=True,source_Create_UI=source,gaps=ref['gaps']+['Next oldOptionWindow,not yet accepted'],private_handoff_removed=True,input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-mob-control-checkpoint.json').write_text(json.dumps(gate,indent=2)+'\n')
    path=WS/'inventory/client-features.json';registry=json.loads(path.read_text());features=registry['features']
    for feature in features:
        if feature.get('runtime_gate_current'):feature['runtime_gate_current']=False
    new=dict(id='CLIENT455-MOB-CONTROL-163',area='ui',status='partial',runtime_gate_current=True,evidence=['inventory/client455-mob-control-checkpoint.json','inventory/client455-mob-control-reference.json','inventory/client455-mob-control-native.json'],description=gate['scope'],gaps=gate['gaps'])
    features[:]=[feature for feature in features if feature['id']!=new['id']]+[new];path.write_text(json.dumps(registry,indent=2,ensure_ascii=False)+'\n')
    print('PARTIAL_KNOWN_FAILURE:MobControl455/16children/3messages/4GPUframes/sharedmove/liveInit pass;nextOption failure;world/M9OPEN')
if __name__=='__main__':main()
