"""Verify ordinary 455 hits against a surviving target and shared HP accounting."""

import argparse
import json
import struct
from pathlib import Path

from build_client455_x87_math import read_va
from checkpoint_client455_monster_force import resource_inputs
from checkpoint_client455_monster_force_damage import run_fixture
from checkpoint_client455_party_window import path, read, save
from checkpoint_client455_rvp_effects import check, require, sha
from client455_normal_link_evidence import validate_normal_link
from client455_own_probe import build_full_object_probe
from client455_reference_regions import verify_regions
from client455_ui_checkpoint import record
from compare_client_binaries import WS


PRIVATE = WS / 'artifacts/client455-progress/ordinary206'
REFERENCE = PRIVATE / 'reference.json'
COMPONENT = PRIVATE / 'component.json'
LIVE = PRIVATE / 'live.json'
CALLS = {
    0x5a4aad: 0x5a34c0, 0x5a3543: 0x5a3bd0, 0x5a3ce1: 0x43e210, 0x43e22f: 0x446350,
    0x5a3d4c: 0x447a90, 0x5a3d5d: 0x447ac0, 0x4472c7: 0x447790,
    0x4472d3: 0x447900, 0x4472df: 0x447a20, 0x447a82: 0x447af0,
}


def verify_reference():
    proof = verify_regions(REFERENCE)
    raw = json.loads(REFERENCE.read_text())
    require(raw['closed']['success'] and raw['closed']['saved'], 'Owned IDA session closed')
    for pin in proof['references']:
        binary = (WS / pin['file']).read_bytes()
        for site, target in CALLS.items():
            require(read_va(binary, site, 5) == b'\xe8' + struct.pack('<i', target - site - 5),
                    f'455 ordinary impact route at {site:#x}')
    save('ordinary-health-reference', dict(
        **proof, raw=record(REFERENCE), scope='Ordinary 5/7 shares the 455 attacker record and impact accounting.',
        call_rvas={hex(site - 0x400000): hex(target - 0x400000) for site, target in CALLS.items()},
        original_damage_offset=352, pending_damage_offset=360, frame_count_offset=364,
        intermediate_damage_jitter_percent=10, health_application_rva='0x47900'))
    return proof


def check_component(link):
    source = WS / 'scripts/native/client455_monster_force_result_probe.cpp'
    exe = build_full_object_probe('ordinary-health', source)
    files, _, clips = resource_inputs(exe.parent)
    ordinary, ordinary_log = run_fixture(exe, files, ['--ordinary-health'], 'ordinary-health')
    require(ordinary['same_target_attacks'] == 2 and ordinary['health_basis_points'] == [10000, 6500, 4200]
            and sum(ordinary['damage_frames'][:2]) == 100 and ordinary['damage_frames'][2:] == [40],
            'Ordinary health settles across two hits on the same actor')
    force, force_log = run_fixture(exe, files, ['--health'], 'force-health')
    require(force == dict(status='PASS', health_routes=[27, 29], initial_fraction=1, before_impact=0.8,
                          after_final_impact=0.5, after_recovery=0.95, verified_impact_frames=2,
                          short_update_rejected=True), 'Force health regression')
    result = dict(normal_link_sha256=sha(path('normal-link')), normal_executable=link['executable'],
                  ordinary=ordinary, force_regression=force, source=record(source), executable=record(exe),
                  consoles=[ordinary_log, force_log], real_clips=clips)
    COMPONENT.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(ordinary))


def observe_live(link, report_file=LIVE, *, require_ordinary_attack=True):
    live = json.loads(report_file.read_text())
    require(live['normal_link_sha256'] == sha(path('normal-link')) and live['executable'] == link['executable'],
            'Exact own combat build')
    check(dict(file=live['staged_executable'], sha256=link['executable']['sha256']))
    check(live['events'])
    rows = [json.loads(line) for line in (WS / live['events']['file']).read_text().splitlines()]
    require(live['debugger_exit'] == 0 and live['summary']['exit_observed'] and
            live['live_server']['private_handoff_removed'] and
            not any(row['kind'] == 'exception' and not row.get('first_chance') for row in rows),
            'Ordinary client exited and removed the temporary launcher data')
    prefix = 'RF455 Protocol:'
    messages = [row['value'].removeprefix(prefix) for row in rows
                if row['kind'] == 'debug_string' and row['value'].startswith(prefix)]

    def events(name):
        return [tuple(map(int, value.split(':')[1:])) for value in messages if value.startswith(name + ':')]

    impacts = events('combat-impact')
    health = events('monster-health-target')
    server_hp = {}
    matching_impacts = []
    for message in messages:
        kind, _, fields = message.partition(':')
        if kind == 'monster-health-target':
            serial, opcode, hp = map(int, fields.split(':'))
            if opcode == 29:
                server_hp[serial] = hp
        elif kind == 'combat-impact':
            serial, damage, hp = map(int, fields.split(':'))
            if damage > 0 and server_hp.get(serial) == hp:
                matching_impacts.append((serial, hp))
    repeated = []
    for i, (serial, hp) in enumerate(matching_impacts):
        if not 0 < hp < 10000:
            continue
        for target, later_hp in matching_impacts[i + 1:]:
            if target == serial and later_hp < hp:
                repeated.append(dict(serial=serial, first_hp=hp, second_hp=later_hp))
                break
    frames = live['combat_impact_frames']
    captures = events('combat-impact-frame')
    require(len(frames) == len(captures), 'Every captured impact frame is recorded')
    for frame, (index, damage, status) in zip(frames, captures):
        check(frame)
        require(frame['file'].endswith(f'/world-impact-{index}.png') and status == 0 and
                any(row[1] == damage for row in impacts), 'Captured post-impact framebuffer')
    shots = messages.count('tx:5:1:8')
    ammunition = events('combat-ammunition-left')
    ordinary_attack_verified = bool(shots and matching_impacts and
                                    any(before == after + 1 for _, before, after in ammunition))
    require(not require_ordinary_attack or ordinary_attack_verified,
            'Live ordinary impact agrees with server HP and arrow consumption')
    require(not repeated or (shots >= 2 and len(ammunition) >= 2 and len(frames) == 2),
            'Repeated live hits have two captured frames and ammunition replies')
    return dict(record=live.get('combat_monster_record'), approach_ms=live.get('combat_approach_ms', 0),
                shots=shots, impacts=impacts, target_health=health,
                target_picks=events('combat-click'), deaths=events('monster-death'),
                ammunition=ammunition, repeated_surviving_target=repeated, frames=frames,
                ordinary_attack_verified=ordinary_attack_verified)


def main():
    parser = argparse.ArgumentParser()
    stage = parser.add_mutually_exclusive_group()
    stage.add_argument('--reference-only', action='store_true')
    stage.add_argument('--component-only', action='store_true')
    args = parser.parse_args()
    proof = verify_reference()
    if args.reference_only:
        print({key: proof[key] for key in ('full_functions', 'full_instructions', 'positive_cfg_blocks')})
        return
    link = read('normal-link')
    require(validate_normal_link(link) == 'PASS', 'Exact current client build')
    if args.component_only:
        check_component(link)
        return
    component = json.loads(COMPONENT.read_text())
    require(component['normal_link_sha256'] == sha(path('normal-link')), 'Current component regression')
    for item in [component['source'], component['executable'], *component['consoles']]:
        check(item)
    observed = observe_live(link)
    repeated = bool(observed['repeated_surviving_target'])
    names = ('normal-link', 'normal-preparation', 'normal-build', 'normal-consumers', 'own-entry',
             'startup-audit', 'startup-taiwan-native', 'live-launcher-native', 'ordinary-health-reference')
    sources = ('client455_monster_force_port.py', 'client455_monster_health_port.py', 'client455_initial_download_port.py',
               'client455_world_update_port.py', 'probe_client455_live_launcher.py', 'probe_client455_device_startup.py',
               'native/client455_monster_force_damage.inc', 'native/client455_monster_health.inc',
               'native/client455_normal_attack_dispatch.inc', 'native/client455_monster_force_dispatch.inc',
               'native/client455_monster_force_result_probe.cpp', 'native/client455_protocol_observation.h',
               'native/client455_camera_mouse_observation.inc', 'native/client455_walk_observation.inc',
               'native/client455_live_world_observation.inc', 'native/own_client_startup_debugger.cpp')
    save('ordinary-health-checkpoint', dict(
        status='PARTIAL_LIVE_ORDINARY_HEALTH' if repeated else 'PARTIAL_COMPONENT_ORDINARY_HEALTH',
        scope='Ordinary 5/7 damage and server-authoritative monster HP on the actual combat owners.',
        normal_executable=link['executable'], normal_link_sha256=sha(path('normal-link')),
        runtime_login_report=record(LIVE), observations=observed, component=record(COMPONENT),
        earlier_runs=[record(PRIVATE / name) for name in ('first-live.json', 'second-live.json', 'short-approach-live.json')],
        script=record(Path(__file__)), sources=[record(WS / 'scripts' / name) for name in sources],
        fresh_evidence={name: record(path(name)) for name in names}, M6='OPEN', M9='OPEN'))
    print(json.dumps(observed))


if __name__ == '__main__':
    main()
