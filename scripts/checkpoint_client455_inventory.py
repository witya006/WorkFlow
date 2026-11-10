"""Record actual inventory views and live advance to the removed legacy Belt guard."""
import json,struct
from pathlib import Path
from compare_client_binaries import WS
from build_client455_x87_math import read_va
from checkpoint_client455_rvp_effects import sha,check,require
from client455_normal_link_evidence import validate_normal_link
from client455_ui_checkpoint import record,own_symbols
from inspect_client455_failure import inspect

def load(name):return json.loads((WS/'inventory'/f'client455-{name}.json').read_text())
def main():
    link=load('normal-link');require(validate_normal_link(link)=='PASS','Current own PE');digest=sha(WS/'inventory/client455-normal-link.json')
    ref,native,visual,live=[load(name) for name in ['inventory-reference','inventory-native','inventory-visual','character-selection-live-taiwan-native']]
    require(ref['full_functions']==52 and ref['full_instructions']==4375,'Complete52function proof')
    for item in [ref['raw'],ref['script']]+ref['sources']+ref['helpers']:check(item)
    require(all(x['normal_link_sha256']==digest for x in [native,visual,live]),'Exact current runtime reports')
    require(native['status']=='PASS' and native['natural_exit']==0 and native['native']['status']=='PASS' and native['native']['equipment_slots']==16 and native['native']['pack_slots']==20 and native['native']['races']==3 and native['native']['actual_observer_and_message_routes']==6,'Actual ordinary view methods androutes')
    for item in native['sources']+native['inputs']+[native['script']]:check(item)
    require(visual['status']=='REVIEWED_PARTIAL' and visual['frames']==native['frames'] and visual['native_report']['sha256']==sha(WS/'inventory/client455-inventory-native.json') and len(native['frames'])==4,'Four exact reviewed frames')
    for item in native['frames']:check(item);check(item['preview'])
    require(live['first_login_frame_captured'] and live['login_render_returned_after_capture'] and live['live_server']['private_handoff_removed'],'Actual pre-Enter frame andcleanup')
    for key in ['events','captured_frame','capture_metadata']:check(live[key])
    require(any(x.get('own_child_validated') and x.get('sent') for x in live['selection_input']),'Addressed own Enter')
    for value in ['RF455 Protocol:tx:1:14:1','RF455 Protocol:rx:1:15:22','RF455 Protocol:select-result:0:0:0']:require(value in live['protocol_observations'],'Actual live selection '+value)
    failure=inspect(link,live);require(not failure['fault_rva_is_own'] and failure['exception']['code']=='0xe06d7363','System-raised C++ exception distinguished from own causal code')
    guard=next(c for c in failure['candidates'] if c['symbol'].startswith('?RF455_RejectRemovedLegacyBelt@@'))
    caller=next(c for c in failure['candidates'] if c['symbol'].startswith('?Create@CGP_MainGame@@'))
    require(guard['is_code'] and caller['is_code'],'Actual own guard/caller candidates')
    raw=(WS/link['executable']['file']).read_bytes();ret=int(caller['rva'],16);call=read_va(raw,0x400000+ret-5,5);target=ret+struct.unpack('<i',call[1:])[0]
    symbols=own_symbols(link);guard_start=next(a for a,n in symbols if n.startswith('?RF455_RejectRemovedLegacyBelt@@'))
    require(call[0]==0xe8 and target==guard_start,'Own direct call to removed-Belt guard')
    create=next(a for a,n in symbols if n.startswith('?Create@CGP_MainGame@@'));ui=next(a for a,n in symbols if n.startswith('?Create_UI@CGP_MainGame@@'));ui_ret=create+0x41;ui_call=read_va(raw,0x400000+ui_ret-5,5)
    require(ui_call[0]==0xe8 and ui_ret+struct.unpack('<i',ui_call[1:])[0]==ui and ui_ret<ret,'Prior actual Create_UI call')
    table=next(a for a,n in symbols if n=='??_7CGUIInventoryWindow@@6BCGUIContainer@@@');init=struct.unpack('<I',read_va(raw,0x400000+table+0x6c,4))[0]-0x400000
    require(any(a==init and n.startswith('?Init@CGUIInventoryWindow@@') for a,n in symbols),'Ordinary inventory Init vtable route')
    source=WS/'work/client455-port/normal/source/gameprogress/cgp_maingame.cpp';body=source.read_bytes();require(body.index(b'_GetInventoryBoard()->InitWindow')<body.index(b'_GetBeltBoard()->Create')<body.index(b'_GetEquipBoard()->InitWindow'),'Actual stage order:inventory then removedBelt beforeequipment')
    failure.update(kind='REMOVED_LEGACY_BELT_GUARD_AFTER_INVENTORY',own_guard_rva=guard['rva'],verified_call=dict(return_rva=hex(ret),instruction_rva=hex(ret-5),bytes=call.hex(),callee_rva=hex(target)),verified_prior_UI_call=dict(return_rva=hex(ui_ret),callee_rva=hex(ui)),inventory_vtable=dict(rva=hex(table),slot_offset='0x6c',init_rva=hex(init)),cause='Old0.7Create_Board stillrequests removedBelt after inventory andLinker initialization;restore actual455stage graph,do not bypass the guard',whole_client_run_succeeded=False)
    selected={
        'CGUIInventoryWindow':[(0x6766a0,'Init'),(0x676ac0,'SetSprite'),(0x676b40,'Open'),(0x676ba0,'Close'),(0x676c10,'SetEquipWindow'),(0x676cf0,'AddPack'),(0x677120,'SetPackState'),(0x677200,'OpenDockingPack'),(0x677320,'SetOpenOnlyOnePack'),(0x677990,'SetOwnDalant'),(0x677a50,'SetOwnGold'),(0x677b10,'MouseEvent'),(0x677ce0,'PickingObjectEvent')],
        'CGUIInventoryBoard':[(0x672c90,'Init'),(0x673140,'SetSprite'),(0x673730,'SetTradeItem'),(0x673830,'SetUselessSocket'),(0x6738c0,'SetUselessItem')],
        'CGUIEquipWindow':[(0x6746a0,'Init'),(0x674cf0,'SetSprite'),(0x674e80,'Open'),(0x674ed0,'Close'),(0x675210,'SetTradeItem'),(0x6752d0,'SetUselessSocket'),(0x675360,'SetEmpty')]}
    bindings=[]
    for klass,methods in selected.items():
        for address,name in methods:
            found=[hex(a) for a,n in symbols if n.startswith('?'+name+'@'+klass+'@@')]
            bindings.append(dict(rva=hex(address-0x400000),symbol=klass+'::'+name,source=record(WS/'scripts/native/client455_inventory.inc'),ordinary_symbol_rvas=found,standalone_symbol_retained=bool(found),retained_in_ordinary_executable=True if found else None,scope='Actual view geometry/owners/money/masks/window states tested;ordinary inventory Init returned;full payload/action/settings/lifecycle equivalence remains open',complete_equivalence=False))
    binding=dict(schema_version=1,reference_sha256=ref['references'][0]['sha256'],architecture='x86',image_base='0x400000',normal_executable=link['executable'],functions=bindings,generator=record(Path(__file__)))
    (WS/'inventory/client455-inventory-bindings.json').write_text(json.dumps(binding,indent=2)+'\n')
    names=['inventory-reference','inventory-native','inventory-visual','inventory-bindings','inventory-discovery','normal-preparation','normal-build','normal-consumers','normal-link','own-entry','startup-audit','startup-taiwan-native','live-launcher-native','character-selection-live-taiwan-native','live-server']
    gate=dict(status='PARTIAL_KNOWN_FAILURE',scope='Inventory/20slot packs/16slot equipment views integrated andcomponent-tested;ordinary inventory Init returned after live selection,next removed legacyBelt guard in oldstage graph;world not entered',script=record(Path(__file__)),helpers=[record(WS/'scripts/client455_ui_checkpoint.py'),record(WS/'scripts/inspect_client455_failure.py')],normal_link_sha256=digest,normal_executable=link['executable'],runtime_login_report=record(WS/'inventory/client455-character-selection-live-taiwan-native.json'),fresh_evidence={name:record(WS/'inventory'/f'client455-{name}.json') for name in names},prior_runtime=record(WS/'artifacts/client455-progress/before165/manifest.json'),post_selection_failure=failure,ordinary_inventory_connected=True,live_inventory_Init_returned=True,live_pack_Init_proved=False,live_equipment_Init_proved=False,live_advanced_past_prior_inventory_crash=True,live_selection_exchange_completed=True,main_game_ui_created=True,boards_created=False,world_entered=False,full_client=False,explicit_function_bindings=len(bindings),component_frames_visually_inspected=True,source_Create_Board=record(source),gaps=ref['gaps']+['OldMainGame boardcreation requests removed legacyBelt;actual455stage ownership/registration isnext required work'],private_handoff_removed=True,input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-inventory-checkpoint.json').write_text(json.dumps(gate,indent=2)+'\n')
    path=WS/'inventory/client-features.json';registry=json.loads(path.read_text());features=registry['features']
    for feature in features:
        if feature.get('runtime_gate_current'):feature['runtime_gate_current']=False
    new=dict(id='CLIENT455-INVENTORY-VIEWS-165',area='ui',status='partial',runtime_gate_current=True,evidence=['inventory/client455-inventory-checkpoint.json','inventory/client455-inventory-reference.json','inventory/client455-inventory-native.json'],description=gate['scope'],gaps=gate['gaps'])
    features[:]=[feature for feature in features if feature['id']!=new['id']]+[new];path.write_text(json.dumps(registry,indent=2,ensure_ascii=False)+'\n')
    print('PARTIAL_KNOWN_FAILURE:inventory/20slot packs/16slot equipment views PASS;liveinventoryInit returned,nextremovedBelt stageguard;world/M9OPEN')
if __name__=='__main__':main()
