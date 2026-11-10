"""Partial live-login evidence,including the observed equipped-action failure."""
import json,re
from pathlib import Path
from compare_client_binaries import WS
from client455_normal_link_evidence import validate_normal_link
from client455_reference_regions import verify_regions
from checkpoint_client455_rvp_effects import check,load,require,sha


def record(path):return dict(file=Path(path).relative_to(WS).as_posix(),sha256=sha(path))


def main():
    link=load('client455-normal-link');require(validate_normal_link(link)=='PASS','Exact linked own PE')
    link_hash=sha(WS/'inventory/client455-normal-link.json');build=load('client455-normal-build')
    require(build['build_exit']==0 and build['objects']==182 and build['canonical_kernel_objects']==20,'Own build')
    account=load('client455-account-native');owner=load('client455-player-owner-native')
    for body in [account,owner]:
        require(body['normal_link_sha256']==link_hash and body['natural_exit']==0,'Fresh affected native runs')
        for key in ['exe','map','output']:check(body[key])
        for row in body['inputs']:check(row)
    compact=account['registered_character_native']
    require(compact['status']=='PASS' and compact['compact_reply_sizes']==[14,178,342,506],'All active-record boundaries')
    require(compact['truncated_active_records_rejected'] and compact['compact178_actual_encrypted_receiver'],'Real fragmented compact receiver')
    require(owner['native']['status']=='PASS' and owner['native']['upgrade_BYTE_only113'],'Real normal-item upgrade setter')
    saved_owner=json.loads((WS/'artifacts/client455-progress/before155/inventory/client455-player-owner-native.json').read_text())
    old_frames={Path(row['file']).name:row['sha256'] for row in saved_owner['frames']}
    for row in owner['frames']:
        check(row);require(old_frames[Path(row['file']).name]==row['sha256'],'Preserved assembled render frame')
    proof_file=WS/'artifacts/client455-progress/live155-upgrade-reference/session.json';proof=verify_regions(proof_file)
    require(proof['full_functions']==1 and proof['full_instructions']==16,'Full462170 proof on both pins')
    reference=load('client455-registered-characters-reference');check(reference['raw'])
    for pin in reference['references']:check(pin)
    raw=json.loads((WS/reference['raw']['file']).read_text())
    pages=next(value for key,value in raw['character_assemblies'].items() if int(key,16)==0x56ae40)
    lines=[line for page in pages for line in page['asm']['lines']]
    instructions={line['addr']:line['instruction'] for line in lines}
    require(instructions['56ae64']=='push 1FAh; Size' and instructions['56aeba']=='movzx eax, [ebp+var_203]','Target internal506copy andcount loop')
    login=load('client455-login-frame-taiwan-native');live=load('client455-login-frame-live-taiwan-native');auth=load('client455-live-launcher-native')
    for body in [login,live]:
        require(body['normal_link_sha256']==link_hash,'Fresh own runtime PE')
        check(body['events'])
    require(login['first_login_frame_captured'] and login['login_render_returned_after_capture'],'Ordinary Login renders')
    check(login['captured_frame']);check(login['capture_metadata'])
    require(not any(not row.get('first_chance') for row in login['exceptions']),'No ordinary Login unhandled exception')
    require(auth['accepted'] and auth['complete_login_key_received'] and auth['login_key_bytes']==16,'Actual launcher authentication')
    require(live['live_server']['private_handoff_removed'],'Private handoff removed')
    run=(WS/live['staged_executable']).parent
    require(not (run/'System/DefaultSet.tmp').exists(),'No retained live key file')
    events=[json.loads(line) for line in (WS/live['events']['file']).read_text().splitlines()]
    protocol=[row['value'] for row in events if row.get('kind')=='debug_string' and row.get('value','').startswith('RF455 Protocol:')]
    for value in ['RF455 Protocol:tx:1:1:58','RF455 Protocol:rx:1:2:12','RF455 Protocol:world-result:0:0:0','RF455 Protocol:tx:1:8:0','RF455 Protocol:rx:1:9:178','RF455 Protocol:rx:1:21:1']:
        require(value in protocol,'Live event '+value)
    fatal=next(row for row in events if row.get('kind')=='fatal_context')
    require(any(not row.get('first_chance') for row in live['exceptions']) and not live['login_frame_captured'],'Record live failure honestly')
    mapping=(WS/link['map']['file']).read_text();symbols=[]
    for line in mapping.splitlines():
        match=re.match(r'\s+[0-9A-Fa-f]+:[0-9A-Fa-f]+\s+(\S+)\s+([0-9A-Fa-f]{8})',line)
        if match:symbols.append((int(match[2],16)-0x400000,match[1]))
    symbols.sort();resolved=[]
    for row in fatal['own_stack_rva_candidates']:
        rva=int(row['rva'],16);prior=[item for item in symbols if item[0]<=rva]
        if prior:
            at,name=prior[-1];resolved.append(dict(**row,symbol=name,symbol_offset=rva-at))
    require(any(row['symbol'].startswith('?GetEquipItem@CPlayerProc@@') for row in resolved),'Observed next legacy equipment consumer')
    require(any(row['symbol'].startswith('?SetAction@CPlayer@@') for row in resolved),'Observed next action caller')
    files=['normal-build','normal-consumers','normal-link','normal-preparation','own-entry','account-native','player-owner-native','startup-audit','startup-taiwan-native','login-frame-taiwan-native','login-frame-live-taiwan-native','live-launcher-native','live-resource-inputs','live-server']
    sources=['scripts/prepare_client455_normal.py','scripts/native/client455_protocol_observation.h','scripts/native/client455_registered_characters.h','scripts/native/client455_registered_characters.inc','scripts/native/client455_registered_characters_probe.inc','scripts/native/client455_item_payloads.h','scripts/native/client455_item_payloads.cpp','scripts/native/client455_player_owner_probe.cpp','scripts/native/client455_world_entry.inc','scripts/probe_client455_live_launcher.py','scripts/probe_client455_device_startup.py','scripts/prepare_client455_live_resources.py','scripts/native/own_client_startup_debugger.cpp']
    report=dict(status='PARTIAL',scope='Own live launcher/game-entry exchange and compact registered reply repair;ordinary offline Login/assembled render pass;live selection fails in equipped action',
        script=record(Path(__file__)),sources=[record(WS/path) for path in sources],normal_link_sha256=link_hash,normal_executable=link['executable'],
        fresh_evidence={name:record(WS/f'inventory/client455-{name}.json') for name in files},
        proof=dict(raw=record(proof_file),**proof),registered_internal_copy_reference=record(WS/'inventory/client455-registered-characters-reference.json'),
        runtime_login_report=record(WS/'inventory/client455-login-frame-taiwan-native.json'),ordinary_Login_frame=login['captured_frame'],Login_visually_inspected=True,
        ordinary_Login=True,live_launcher_authentication_accepted=True,live_game_entry_accepted=True,live_registered_reply_bytes=178,
        compact_packet_adaptation='Zero-pad only absent unused slots after validating14+164*count;not a claim of original wire length orunsafe overread equivalence',
        protocol_observations=protocol,live_failure=dict(file=live['events']['file'],unhandled_exception=True,resolved_stack_candidates=resolved),
        native_compact_receiver=compact,upgrade_BYTE_only113=True,equal_assembled_render_frames=3,
        live_selection_completed=False,world_entered=False,full_player_appearance_or_selection=False,full_client=False,
        private_handoff_removed=True,password_saved=False,raw_packets_saved=False,
        gaps=['Migrate equipped SetAction combat-mode transition from legacy GetEquipItem to typed owner/animation/fade after target verification','Remaining bootstrap/UI/class/actor/animation andselection flow','Full world/control/gameplay/protocol/lifecycle andall client-acceptance requirements'],
        input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-live-login-checkpoint.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PARTIAL:live launcher andgame-entry accepted;compact receiver/upgrade andordinary Login pass;equipped SetAction still fails;M9 OPEN')


if __name__=='__main__':main()
