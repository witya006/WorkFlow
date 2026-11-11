"""Verify the 455 target request, monster death and live client combat."""

import argparse
import json
import struct
from pathlib import Path

from build_client455_x87_math import read_va
from checkpoint_client455_party_window import path, read, save
from checkpoint_client455_rvp_effects import check, require, sha
from client455_normal_link_evidence import validate_normal_link
from client455_reference_regions import verify_regions
from client455_ui_checkpoint import record
from compare_client_binaries import WS


PRIVATE = WS / 'artifacts/client455-progress/target205'
REFERENCE = PRIVATE / 'reference.json'
LIVE = PRIVATE / 'live.json'
CALLS = {
    0x52ec1a: 0x58bf00, 0x52eca9: 0x58c090, 0x58bf40: 0x408920,
    0x58bf4b: 0x419f30, 0x58bf5f: 0x58a6c0, 0x58c0a7: 0x58a6c0,
    0x58a6dd: 0x57eac0, 0x56332f: 0x5664a0, 0x5664bf: 0x51c2f0,
    0x5664d9: 0x44a660, 0x45a672: 0x446ca0, 0x4472d3: 0x447900,
    0x411591: 0x58c300, 0x58c381: 0x58a6c0, 0x58c3a5: 0x411550, 0x44f3f3: 0x42e400,
}


def verify_reference():
    proof = verify_regions(REFERENCE)
    details = json.loads(REFERENCE.read_text())
    for key in ('closed', 'mode_closed'):
        require(details[key]['success'] and details[key]['saved'], 'Owned IDA session closed')
    for pin in proof['references']:
        binary = (WS / pin['file']).read_bytes()
        for site, target in CALLS.items():
            require(read_va(binary, site, 5) == b'\xe8' + struct.pack('<i', target - site - 5),
                    f'455 target/death route at {site:#x}')
        require(read_va(binary, 0xaaa67c, 4) == struct.pack('<I', 0x45a630), 'Monster death vtable slot')
        require(read_va(binary, 0xaa8f48, 4) == struct.pack('<I', 0x44f3e0), 'Player pose vtable slot')
    save('monster-target-reference', dict(
        **proof, raw=record(REFERENCE), scope='455 target info request/cancel, monster death and impact health.',
        call_rvas={hex(site - 0x400000): hex(target - 0x400000) for site, target in CALLS.items()},
        target_request=dict(category=13, opcode=26, bytes=8, kind=0, type=1, zone_index_offset=2, serial_offset=4),
        target_cancel=dict(category=13, opcode=28, bytes=1),
        mode_request=dict(category=13, opcode=21, bytes=2, mode_offset=0, pose_offset=1,
                          state_category=4, state_opcode=25, mode_bit=1, pose_bit=13),
        death=dict(category=3, opcode=24, bytes=7, zone_index_offset=0, serial_offset=2, reason_offset=6,
                   death_reason=0, owner_rva='0x5a630', vtable_slot_rva='0x6aa67c'),
        health_application_rva='0x47900'))
    return proof


def verify_live(link):
    live = json.loads(LIVE.read_text())
    require(live['normal_link_sha256'] == sha(path('normal-link')) and live['executable'] == link['executable'],
            'Exact own target build')
    check(dict(file=live['staged_executable'], sha256=link['executable']['sha256']))
    check(live['events'])
    rows = [json.loads(line) for line in (WS / live['events']['file']).read_text().splitlines()]
    require(live['debugger_exit'] == 0 and live['summary']['exit_observed'] and
            live['live_server']['private_handoff_removed'] and
            not any(row['kind'] == 'exception' and not row.get('first_chance') for row in rows),
            'Observed own exit without a fatal exception and private handoff cleanup')
    prefix = 'RF455 Protocol:'
    messages = [row['value'].removeprefix(prefix) for row in rows
                if row['kind'] == 'debug_string' and row['value'].startswith(prefix)]

    def events(name):
        return [tuple(map(int, value.split(':')[1:])) for value in messages if value.startswith(name + ':')]

    requests = messages.count('tx:13:26:8')
    clicks = events('combat-click')
    shots = messages.count('tx:5:1:8')
    deaths = events('monster-death')
    impacts = events('combat-impact')
    updates = events('combat-ammunition-left')
    captured = events('combat-impact-frame')
    frames = live['combat_impact_frames']
    require(requests and shots >= 2 and len(deaths) >= 2 and len(impacts) >= 2,
            'Repeated attacks, deaths and impacts observed in one session')
    require(requests <= len(clicks), 'Ordinary target requests are not repeated on every frame')
    require('tx:13:21:2' in messages and 'tx:5:14:1' not in messages and
            any(mode == 1 and not pending for mode, _, pending in events('combat-monster-choice')),
            '455 mode request followed by settled combat mode')
    health = events('monster-health-target')
    require(any(opcode == 27 and value > 0 for _, opcode, value in health), 'Received the selected target HP')
    killed = {serial for serial, reason, found in deaths if reason == 0 and found}
    landed = {serial for serial, damage, hp in impacts if serial in killed and damage > 0 and hp == 0}
    require(len(landed) >= 2 and all((serial, 29, 0) in health for serial in landed),
            'Both server-confirmed kills reach zero health at their attack impact')
    require(len(frames) == len(captured) == 2, 'Both rendered impact frames identified')
    for frame, (index, _, status) in zip(frames, captured):
        check(frame)
        require(frame['file'].endswith(f'/world-impact-{index}.png') and status == 0, 'Framebuffer capture succeeded')
    require(updates and all(before == after + 1 for _, before, after in updates), 'Server ammunition updates applied')
    require(len(updates) == shots and messages.count('rx:5:7:25') == shots and
            all(previous[2] == following[1] for previous, following in zip(updates, updates[1:])),
            'Every sent bow shot received a result and consumed one arrow')
    return dict(target_requests=requests, target_cancels=messages.count('tx:13:28:1'), shots=shots,
                deaths=deaths, impacts=impacts, ammunition=updates, retargets=events('combat-target-ended'),
                combat_mode_requests=messages.count('tx:13:21:2'), legacy_mode_requests=messages.count('tx:5:14:1'),
                target_health=health, target_errors=events('target-info-rejected'),
                target_replies=sum(msg.startswith('rx:13:27:') for msg in messages),
                health_updates=sum(msg.startswith('rx:13:29:') for msg in messages), frames=frames)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--reference-only', action='store_true')
    args = parser.parse_args()
    proof = verify_reference()
    if args.reference_only:
        print({key: proof[key] for key in ('full_functions', 'full_instructions', 'positive_cfg_blocks')})
        return
    link = read('normal-link')
    require(validate_normal_link(link) == 'PASS', 'Fresh verified own build')
    observed = verify_live(link)
    evidence = ('normal-link', 'normal-preparation', 'normal-build', 'normal-consumers', 'own-entry',
                'startup-audit', 'startup-taiwan-native', 'live-launcher-native', 'monster-target-reference')
    sources = ('client455_target_windows_port.py', 'client455_monster_health_port.py',
               'client455_armed_attack_port.py', 'client455_player_status_port.py', 'client455_player_owner_port.py',
               'client455_initial_download_port.py', 'client455_camera_input_port.py', 'client455_world_update_port.py',
               'native/client455_camera_mouse_observation.inc', 'native/own_client_startup_debugger.cpp',
               'native/client455_live_world_observation.inc',
               'native/client455_world_updates.h',
               'native/client455_world_monster_spawn.inc', 'native/client455_monster_health.inc',
               'native/client455_monster_health_dispatch.inc')
    save('monster-target-checkpoint', dict(
        status='PARTIAL_LIVE_MONSTER_DEATH', scope='Ordinary target request and monster death on NeutralB.',
        normal_executable=link['executable'], normal_link_sha256=sha(path('normal-link')),
        runtime_login_report=record(LIVE), observations=observed, script=record(Path(__file__)),
        prior_death_observation=record(PRIVATE / 'death-live.json'), prior_mode_observation=record(PRIVATE / 'mode-live.json'),
        sources=[record(WS / 'scripts' / name) for name in sources],
        fresh_evidence={name: record(path(name)) for name in evidence}, M6='OPEN', M9='OPEN'))
    print(json.dumps(observed))


if __name__ == '__main__':
    main()
