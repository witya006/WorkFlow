"""Keep the next real CharInfo failure visible after the restored upper HUD."""
import json,re
from pathlib import Path
from compare_client_binaries import WS
from checkpoint_client455_rvp_effects import sha,check,require
from client455_normal_link_evidence import validate_normal_link
def record(path):
    path=Path(path);return dict(file=path.relative_to(WS).as_posix(),sha256=sha(path))
def load(name):return json.loads((WS/'inventory'/f'{name}.json').read_text())
def main():
    link=load('client455-normal-link');require(validate_normal_link(link)=='PASS','Current link');digest=sha(WS/'inventory/client455-normal-link.json')
    ref=load('client455-hud-reference');check(ref['raw']);check(ref['callbacks']['raw'])
    for row in ref['sources']:check(row)
    native=load('client455-hud-native');live=load('client455-character-selection-live-taiwan-native')
    require(native['normal_link_sha256']==live['normal_link_sha256']==digest,'Current runtime reports')
    require(native['natural_exit']==0 and native['native']['status']=='PASS' and native['native']['actual_HUD_children']==17,'Actual component')
    for row in native['sources']+native['inputs']:check(row)
    require(len(native['frames'])==3,'Three GPU frames')
    for row in native['frames']:check(row);check(row['preview'])
    images={Path(row['file']).stem:(WS/row['file']).read_bytes() for row in native['frames']}
    require(images['hud-changed']==images['hud-reloaded']!=images['hud-initial'],'State visible/reload stable')
    require(live['login_frame_captured'] and live['login_render_returned_after_capture'] and live['live_server']['private_handoff_removed'],'Ordinary Login/cleanup')
    for key in ['events','captured_frame','capture_metadata']:check(live[key])
    require(any(x.get('sent') and x.get('own_child_validated') for x in live['selection_input']),'Addressed own Enter')
    for value in ['RF455 Protocol:tx:1:14:1','RF455 Protocol:rx:1:15:22','RF455 Protocol:select-result:0:0:0']:
        require(value in live['protocol_observations'],'Selection '+value)
    fatal=[e for e in live['exceptions'] if not e.get('first_chance')];require(len(fatal)==1 and fatal[0]['rva']=='0x12c53f','Next actual failure')
    symbols=[]
    for line in (WS/link['map']['file']).read_text().splitlines():
        match=re.match(r'^\s+[\da-fA-F]+:[\da-fA-F]+\s+(\S+)\s+([\da-fA-F]{8})\b',line)
        if match:symbols.append((int(match[2],16)-0x400000,match[1]))
    resolved=[]
    for address in [0x12c53f,0x97288,0x74366,0x73301,0x26729,0x26021]:
        start,name=max((a,n) for a,n in symbols if a<=address);resolved.append(dict(rva=hex(address),symbol=name,offset=hex(address-start)))
    require(any('SetSprite@CGUICharInfoWindow' in x['symbol'] for x in resolved),'Actual next window')
    events=[json.loads(line) for line in (WS/live['events']['file']).read_text().splitlines()]
    context=next(x for x in events if x['kind']=='fatal_context');stack={int(x['rva'],16) for x in context['own_stack_rva_candidates']}
    require({0x74366,0x73301,0x26729}<=stack,'Actual CharInfo initialization stack')
    failure=dict(kind='UNHANDLED_AFTER_SUCCESSFUL_SELECTION',own_rva='0x12c53f',code='0xc0000005',resolved_own_symbols=resolved,
        cause='Old CharInfo SetSprite still requests0.7 inventory action6/7;target CharInfo skin/layout consumer not ported',whole_client_run_succeeded=False)
    names=['hud-reference','hud-bindings','hud-native','character-selection-live-taiwan-native','normal-build','normal-consumers','normal-link','normal-preparation','own-entry','startup-audit','startup-taiwan-native','live-launcher-native','live-server']
    report=dict(status='PARTIAL_KNOWN_FAILURE',scope='Actual455upper gauge panel integrated;real selection proceeds to next old CharInfo Init failure;world not entered',
        script=record(__file__),normal_link_sha256=digest,normal_executable=link['executable'],ordinary_nation='Taiwan',runtime_login_report=record(WS/'inventory/client455-character-selection-live-taiwan-native.json'),
        fresh_evidence={name:record(WS/f'inventory/client455-{name}.json') for name in names},prior_runtime=ref['prior_runtime'],post_selection_failure=failure,
        component_frame_visually_inspected=True,hud_component_passed=True,live_advanced_past_prior_HUD_crash=True,
        live_selection_exchange_completed=True,live_selection_completed=False,full_selection_stage_accepted=False,
        existing_MainGame_Create_UI_reached=True,main_game_ui_created=False,world_entered=False,playable_world=False,explicit_function_bindings=5,
        gaps=ref['gaps']+['Next actual CharInfo SetSprite/Init old inventory namespace;fullwindow target47 needs restoration'],
        private_handoff_removed=True,input_exe_executed=False,server_modified=False,full_client=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-hud-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n')
    file=WS/'inventory/client-features.json';registry=json.loads(file.read_text())
    for entry in registry['features']:
        if entry.get('runtime_gate_current'):entry['runtime_gate_current']=False
    feature=dict(id='CLIENT455-HUD-159',status='partial',runtime_gate_current=True,runtime_gate_last_verified=True,description=report['scope'],
        implementation=['scripts/client455_hud_port.py','scripts/native/client455_hud.inc'],evidence=['inventory/client455-hud-reference.json','inventory/client455-hud-checkpoint.json'],
        verification='Actual target skins/17children/zero-max andthreshold semantics/GPU reload;live next CharInfo failure retained',post_selection_failure=failure,world_entered=False,full_client=False,M6='OPEN',M9='OPEN')
    matches=[i for i,x in enumerate(registry['features']) if x['id']==feature['id']]
    if matches:registry['features'][matches[0]]=feature
    else:registry['features'].append(feature)
    file.write_text(json.dumps(registry,ensure_ascii=False,indent=2)+'\n')
    print('PARTIAL_KNOWN_FAILURE:455HUD/GPU/reload pass;live next CharInfo Init failure;world/M9 OPEN')
if __name__=='__main__':main()
