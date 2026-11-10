"""Selected actor-lighting acceptance and per-original-function source bindings."""
import json,re
from pathlib import Path
from compare_client_binaries import WS
from client455_normal_link_evidence import validate_normal_link
from checkpoint_client455_rvp_effects import check,load,require,sha


def record(path):
    path=Path(path)
    return dict(file=path.relative_to(WS).as_posix(),sha256=sha(path))


def main():
    ref=load('client455-actor-lighting-reference');check(ref['raw']);check(ref['script']);check(ref['prior_runtime'])
    for row in ref['sources']:check(row)
    link=load('client455-normal-link');require(validate_normal_link(link)=='PASS','Current own PE')
    link_hash=sha(WS/'inventory/client455-normal-link.json')
    native=load('client455-player-owner-native');n=native['native']
    require(native['normal_link_sha256']==link_hash and native['natural_exit']==0 and n['status']=='PASS','Fresh native owner')
    require(n['actual_lobby_actor_lighting'] and n['actor_lighting_cases']==12 and n['actor_material_reaches_equipment_and_GPU'],'Actual map/material/gear/GPU route')
    for key in ['exe','map','output','console','actor_lighting']:check(native[key])
    for row in native['inputs']+native['sources']+native['frames']:check(row)
    trace=[json.loads(line) for line in (WS/native['actor_lighting']['file']).read_text().splitlines()]
    require({(row['sample'],row['mode']) for row in trace}=={(sample,mode) for sample in range(3) for mode in range(4)} and len(trace)==12,'Complete selected native matrix')
    for row in trace:require(row['selected_color']==(0xffa0a0ff if row['mode']>=2 else 0x7f204080 if row['mode']==1 else row['map_color']),'Priority/color selection')
    old=json.loads((WS/'artifacts/client455-progress/before157/inventory/client455-player-owner-native.json').read_text())
    expected={Path(row['file']).name:row['sha256'] for row in old['frames']}
    require(len(native['frames'])==3 and all(expected[Path(row['file']).name]==row['sha256'] for row in native['frames']),'Three controlled regressions unchanged')
    normal=load('client455-login-frame-taiwan-native');live=load('client455-login-frame-live-taiwan-native');auth=load('client455-live-launcher-native')
    for body in [normal,live]:
        require(body['normal_link_sha256']==link_hash and body['login_frame_captured'] and body['login_render_returned_after_capture'],'Fresh Login frame and next return')
        require(not any(not e.get('first_chance') for e in body['exceptions']),'No unhandled exception')
        for key in ['events','captured_frame','capture_metadata']:check(body[key])
        for row in body['inputs']:check(row)
    require(auth['accepted'] and auth['complete_login_key_received'] and live['live_server']['private_handoff_removed'],'Real auth and private cleanup')
    require(not ((WS/live['staged_executable']).parent/'System/DefaultSet.tmp').exists(),'No retained key handoff')
    for message in ['RF455 Protocol:rx:1:2:12','RF455 Protocol:world-result:0:0:0','RF455 Protocol:rx:1:9:178']:
        require(message in live['protocol_observations'],'Live registered character '+message)
    mapping=(WS/link['map']['file']).read_text(errors='replace')
    functions=[]
    for rva,symbol,source,port_scope,runtime_scope in [
        ('0x3ce7a0','CResObject::SetLightColorFromMap','scripts/native/client455_actor_lighting.inc','PARTIAL_DEFINED_COLOR_DOMAIN','Native actual BSP plus ordinary live selection;no all-branches original comparison'),
        ('0x4d230','CPlayer::SetLightColorFromMap','work/client455-port/normal/source/character/player/cplayer.cpp','EXISTING_WRAPPER_VERIFIED','Native actual actor/processor material propagation andordinary live selection'),
        ('0x3cea00','CResObject::SetBlink455','scripts/native/client455_actor_lighting.inc','METHOD_BODY_AVAILABLE_CALLERS_OPEN','Native explicit method only;ordinary player state producers not ported')]:
        name,owner=symbol.split('::');pattern=r'\?'+re.escape(owner)+'@'+re.escape(name)+r'@@\S+\s+[0-9a-fA-F]{8}'
        retained=bool(re.search(pattern,mapping))
        if rva!='0x3cea00':require(retained,'Ordinary virtual lighting retained '+symbol)
        functions.append(dict(rva=rva,symbol=symbol,source=record(WS/source),source_scope=port_scope,
                              retained_in_ordinary_executable=retained,runtime_scope=runtime_scope,
                              complete_equivalence=False,reference=record(WS/'inventory/client455-actor-lighting-reference.json')))
    bindings=dict(schema_version=1,scope='First explicit source bindings;historical function population remains unclassified',
                  reference_sha256=ref['references'][0]['sha256'],architecture='x86',image_base='0x400000',
                  normal_executable=link['executable'],native_evidence=record(WS/'inventory/client455-player-owner-native.json'),
                  ordinary_evidence=record(WS/'inventory/client455-login-frame-live-taiwan-native.json'),functions=functions)
    (WS/'inventory/client455-actor-lighting-bindings.json').write_text(json.dumps(bindings,indent=2)+'\n')
    registry_file=WS/'inventory/client-features.json';registry=json.loads(registry_file.read_text())
    for feature in registry['features']:
        if feature.get('runtime_gate_current'):feature['runtime_gate_current']=False
    entry=dict(id='CLIENT455-ACTOR-LIGHTING-157',status='partial',runtime_gate_current=True,runtime_gate_last_verified=True,
               description='Actual map actor material/directional light restored;live selection character is visibly no longer nearlyblack',
               implementation=['scripts/client455_actor_lighting_port.py','scripts/native/client455_actor_lighting.inc'],
               evidence=['inventory/client455-actor-lighting-reference.json','inventory/client455-actor-lighting-bindings.json','inventory/client455-actor-lighting-checkpoint.json','research/client455-actor-lighting.md'],
               verification='Real lobby12cases/gear/GPU and3priorPNG pass;live frame370/8000ms returnswithout unhandled exception;visual comparison inspected',
               live_game_entry_accepted=True,actual_character_visible=True,character_no_longer_nearly_black=True,
               original_full_frame_equivalence=False,live_selection_completed=False,world_entered=False,full_client=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    matches=[i for i,f in enumerate(registry['features']) if f['id']==entry['id']]
    if matches:registry['features'][matches[0]]=entry
    else:registry['features'].append(entry)
    registry_file.write_text(json.dumps(registry,ensure_ascii=False,indent=2)+'\n')
    previous=json.loads((WS/'artifacts/client455-progress/before157/inventory/client455-login-frame-live-taiwan-native.json').read_text())
    report=dict(status='PARTIAL',scope='Actual actor map lighting restored;live selection character is no longer nearly black;full stage andworld remain open',
        script=record(__file__),normal_link_sha256=link_hash,normal_executable=link['executable'],
        fresh_evidence={name:record(WS/f'inventory/client455-{name}.json') for name in ['actor-lighting-reference','actor-lighting-bindings','player-owner-native','normal-build','normal-consumers','normal-link','normal-preparation','own-entry','startup-audit','startup-taiwan-native','login-frame-taiwan-native','login-frame-live-taiwan-native','live-launcher-native','live-server']},
        runtime_login_report=record(WS/'inventory/client455-login-frame-live-taiwan-native.json'),
        prior_runtime=ref['prior_runtime'],native=n,ordinary_Login=True,live_game_entry_accepted=True,
        live_selection_frame=live['captured_frame'],previous_dark_frame=previous['captured_frame'],live_capture=live['capture_result'],
        comparison_visually_inspected=True,character_no_longer_nearly_black=True,selected455_actor_light_route=True,
        original_full_frame_equivalence=False,equal_assembled_render_frames=3,explicit_function_bindings=len(functions),
        live_selection_completed=False,world_entered=False,private_handoff_removed=True,
        gaps=ref['gaps']+['Full455Login/UI/select-enter-world andordinary game world remain unaccepted','Visual improvement isnot original full-frame equivalence'],
        full_client=False,input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-actor-lighting-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PARTIAL:actual lobby actor light/gear/GPU PASS;live frame visually improved;3explicit source bindings;selection/world/M9 OPEN')


if __name__=='__main__':main()
