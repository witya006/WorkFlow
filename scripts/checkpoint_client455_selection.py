"""Accept selected exchange/typed transfer while retaining the next fatal UI gap."""
import json,re
from pathlib import Path
from compare_client_binaries import WS
from client455_normal_link_evidence import validate_normal_link
from checkpoint_client455_rvp_effects import check,load,require,sha


def record(path):
    path=Path(path);return dict(file=path.relative_to(WS).as_posix(),sha256=sha(path))


def main():
    link=load('client455-normal-link');require(validate_normal_link(link)=='PASS','Current ownPE');link_hash=sha(WS/'inventory/client455-normal-link.json')
    ref=load('client455-selection-reference');check(ref['raw']);check(ref['default_copy_proof']['raw']);check(ref['script']);check(ref['prior_runtime'])
    for row in ref['sources']:check(row)
    native=load('client455-selection-native');owner=load('client455-player-owner-native');live=load('client455-character-selection-live-taiwan-native')
    for body in [native,owner,live]:require(body['normal_link_sha256']==link_hash,'Fresh own evidence')
    require(native['natural_exit']==0 and native['native']['status']=='PASS' and native['native']['actual_wallet_routes']==4,'Actual selection send/fragmented receiver/wallet routes')
    for key in ['exe','output','console']:check(native[key])
    for row in native['sources']:check(row)
    require(owner['natural_exit']==0 and owner['native']['status']=='PASS','Typed retained default/ordinary worn transfer')
    for key in ['exe','output','console','map']:check(owner[key])
    for row in owner['inputs']+owner['sources']+owner['frames']:check(row)
    previous=json.loads((WS/'artifacts/client455-progress/before158/inventory/client455-player-owner-native.json').read_text());old={Path(row['file']).name:row['sha256'] for row in previous['frames']}
    require(len(owner['frames'])==3 and all(old[Path(row['file']).name]==row['sha256'] for row in owner['frames']),'Three prior equipmentPNG unchanged')
    require(live['login_frame_captured'] and live['login_render_returned_after_capture'] and live['live_server']['private_handoff_removed'],'Actual own Login frame/return/private cleanup')
    for key in ['events','captured_frame','capture_metadata']:check(live[key])
    for row in live['inputs']:check(row)
    require(any(e.get('sent') and e.get('own_child_validated') for e in live['selection_input']),'Actual addressed Enter')
    for value in ['RF455 Protocol:tx:1:14:1','RF455 Protocol:rx:1:15:22','RF455 Protocol:select-result:0:0:0']:
        require(value in live['protocol_observations'],'Live selection '+value)
    fatal=[e for e in live['exceptions'] if not e.get('first_chance')];require(len(fatal)==1 and fatal[0]['rva']=='0x12c8af','Known next MainGame UI failure retained')
    events=[json.loads(line) for line in (WS/live['events']['file']).read_text().splitlines()]
    context=next(e for e in events if e['kind']=='fatal_context');stack={int(e['rva'],16) for e in context['own_stack_rva_candidates']}
    mapping=(WS/link['map']['file']).read_text();rows=[]
    for line in mapping.splitlines():
        found=re.match(r'^\s+[\da-fA-F]+:[\da-fA-F]+\s+(\S+)\s+([\da-fA-F]{8})\b',line)
        if found:rows.append((int(found[2],16)-0x400000,found[1]))
    resolved=[]
    for address in [0x12c8af,0x97421,0x823d8,0x81c2f,0x26709,0x26021]:
        start,name=max((a,n) for a,n in rows if a<=address);resolved.append(dict(rva=hex(address),symbol=name,offset=hex(address-start)))
    require(0x26709 in stack and any('Create_UI@CGP_MainGame' in row['symbol'] for row in resolved),'Actual MainGame::Create_UI in failure stack')
    bindings=[]
    for rva,symbol,source,scope in [
        ('0x16b920','CNetworkMgr::SystemMsg_SelCharRequest_zone','scripts/native/client455_selection.inc','Actual wire/native+live'),
        ('0x16b9d0','CNetworkMgr::SystemMsg_SelCharResult_zone','scripts/native/client455_selection.inc','Bounded22bytes/native+live;short unsafe domain not equivalent'),
        ('0x19f50','CAvatar::SetDefaultItem455','scripts/client455_selection_port.py','Part<6/non-null plus retained base transfer/native+ordinary'),
        ('0x6c130','RF455EquipmentObject::CopyRetainedState455','scripts/native/client455_equipment_object.cpp','Semantic base state/retain;raw vptr,padding,selfalias domains not equivalent')]:
        bindings.append(dict(rva=rva,symbol=symbol,source=record(WS/source),scope=scope,complete_equivalence=False))
    binding_report=dict(schema_version=1,reference_sha256=ref['references'][0]['sha256'],architecture='x86',image_base='0x400000',normal_executable=link['executable'],functions=bindings)
    (WS/'inventory/client455-selection-bindings.json').write_text(json.dumps(binding_report,indent=2)+'\n')
    failure=dict(kind='UNHANDLED_AFTER_SUCCESSFUL_SELECTION',own_rva='0x12c8af',code='0xc0000005',resolved_own_symbols=resolved,
                 cause='Legacy gauge-exp sprite consumer still uses0.7 SpriteImage/gaugeexp.spr andits atlas;file absent inoriginal455 andstagedlab',
                 whole_client_run_succeeded=False)
    report=dict(status='PARTIAL_KNOWN_FAILURE',scope='Live Enter/selection accepted andtyped Avatar gear transfer reaches existing MainGame UI creation;world notentered',
        script=record(__file__),normal_link_sha256=link_hash,normal_executable=link['executable'],ordinary_nation='Taiwan',
        runtime_login_report=record(WS/'inventory/client455-character-selection-live-taiwan-native.json'),
        fresh_evidence={name:record(WS/f'inventory/client455-{name}.json') for name in ['selection-reference','selection-bindings','selection-native','character-selection-live-taiwan-native','player-owner-native','normal-build','normal-consumers','normal-link','normal-preparation','own-entry','startup-audit','startup-taiwan-native','live-launcher-native','live-server']},
        prior_runtime=ref['prior_runtime'],post_selection_failure=failure,pre_selection_frame=live['captured_frame'],pre_selection_frame_visually_inspected=True,
        ordinary_Login=True,actual_Enter_delivered=True,live_character_selection_accepted=True,typed_Avatar_transfer_passed_next_boundary=True,
        existing_MainGame_Create_UI_reached=True,unhandled_exceptions_after_selection=1,live_selection_exchange_completed=True,live_selection_completed=False,full_selection_stage_accepted=False,
        world_entered=False,playable_world=False,equal_assembled_render_frames=3,explicit_function_bindings=4,
        gaps=ref['gaps']+['MainGame0.7UI sprite/layout/provider migration isnext concrete blocker;do not stage renamedfake gauge skin'],
        private_handoff_removed=True,input_exe_executed=False,server_modified=False,full_client=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-selection-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n')
    registry_file=WS/'inventory/client-features.json';registry=json.loads(registry_file.read_text())
    for row in registry['features']:
        if row.get('runtime_gate_current'):row['runtime_gate_current']=False
    feature=dict(id='CLIENT455-SELECTION-158',status='partial',runtime_gate_current=True,runtime_gate_last_verified=True,
        description=report['scope'],implementation=['scripts/client455_selection_port.py','scripts/native/client455_selection.inc','scripts/native/client455_equipment_object.cpp'],
        evidence=['inventory/client455-selection-reference.json','inventory/client455-selection-checkpoint.json','research/client455-selection.md'],
        verification='Actual addressed Enter,server1/15 success22,typed gear retained/default transfer;3priorPNG unchanged;next MainGame UI fatal explicitly open',
        post_selection_failure=failure,live_character_selection_accepted=True,existing_MainGame_Create_UI_reached=True,world_entered=False,full_client=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    matches=[i for i,row in enumerate(registry['features']) if row['id']==feature['id']]
    if matches:registry['features'][matches[0]]=feature
    else:registry['features'].append(feature)
    registry_file.write_text(json.dumps(registry,ensure_ascii=False,indent=2)+'\n')
    print('PARTIAL_KNOWN_FAILURE:live Enter+selection accepted;typed gear handoff reaches MainGame::Create_UI;legacy gauge sprite fatal remains;world/M9 OPEN')


if __name__=='__main__':main()
