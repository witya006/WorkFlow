"""Check ordinary incoming creature attacks through the 455 combat dispatcher."""

import argparse
import json
import struct
from pathlib import Path

from build_client455_x87_math import read_va
from checkpoint_client455_monster_force import resource_inputs
from checkpoint_client455_monster_force_damage import run_fixture
from checkpoint_client455_ordinary_health import observe_live
from checkpoint_client455_party_window import path, read, save
from checkpoint_client455_rvp_effects import check, require, sha
from client455_normal_link_evidence import validate_normal_link
from client455_own_probe import build_full_object_probe
from client455_reference_regions import verify_regions
from client455_ui_checkpoint import record
from compare_client_binaries import WS


PRIVATE = WS / 'artifacts/client455-progress/creatures207'
REFERENCE = PRIVATE / 'reference.json'
COMPONENT = PRIVATE / 'component.json'
LIVE_RUNS = (PRIVATE / 'initial-live.json', PRIVATE / 'live.json')
ROUTES = ((13, 1, 0x5a45ce, 0x5a5510), (14, 3, 0x5a45df, 0x5a55a0), (15, 4, 0x5a45f0, 0x5a5630))


def verify_reference():
    proof = verify_regions(REFERENCE)
    raw = json.loads(REFERENCE.read_text())
    require(raw['closed']['success'] and raw['closed']['saved'], 'Owned IDA session closed')
    for pin in proof['references']:
        binary = (WS / pin['file']).read_bytes()
        for _, _, dispatch, handler in ROUTES:
            calls = {dispatch: handler, handler + 0x1b: 0x5a3470, handler + 0x41: 0x5a4190,
                     handler + 0x61: 0x5a41f0, handler + 0x76: 0x5a34c0}
            for site, target in calls.items():
                require(read_va(binary, site, 5) == b'\xe8' + struct.pack('<i', target - site - 5),
                        f'455 creature attack call at {site:#x}')
    save('creature-attacks-reference', dict(
        **proof, raw=record(REFERENCE), group=5, payload_bytes=15,
        payload_offsets=dict(attacker=0, attack_part=4, critical=5, target_type=6, target=7, damage=11),
        routes=[dict(opcode=opcode, attacker_type=actor, dispatch_rva=hex(dispatch - 0x400000),
                     handler_rva=hex(handler - 0x400000)) for opcode, actor, dispatch, handler in ROUTES],
        shared_queue_rva='0x1a34c0', clears_local_request=False))
    return proof


def check_component(link):
    source = WS / 'scripts/native/client455_monster_force_result_probe.cpp'
    exe = build_full_object_probe('creature-attacks', source)
    inputs, _, creature_clips = resource_inputs(exe.parent, animation_keys=(0x1090, 0x10d0))
    creature, creature_log = run_fixture(exe, inputs, ['--creature-attacks'], 'creature-attacks')
    require(creature == dict(status='PASS', routes=[13, 14, 15], malformed_lengths=6, wing_animation=4240,
                             damage=70000, local_request_preserved=True), 'Creature attack dispatcher')
    inputs, _, force_clips = resource_inputs(exe.parent)
    ordinary, ordinary_log = run_fixture(exe, inputs, ['--ordinary-health'], 'ordinary-health')
    require(ordinary['same_target_attacks'] == 2 and ordinary['health_basis_points'] == [10000, 6500, 4200]
            and sum(ordinary['damage_frames'][:2]) == 100 and ordinary['damage_frames'][2:] == [40],
            'Ordinary attack HP regression')
    force, force_log = run_fixture(exe, inputs, ['--health'], 'force-health')
    require(force == dict(status='PASS', health_routes=[27, 29], initial_fraction=1, before_impact=0.8,
                          after_final_impact=0.5, after_recovery=0.95, verified_impact_frames=2,
                          short_update_rejected=True), 'Force HP regression')
    report = dict(normal_link_sha256=sha(path('normal-link')), normal_executable=link['executable'],
                  creature=creature, ordinary=ordinary, force=force, source=record(source),
                  executable=record(exe), consoles=[creature_log, ordinary_log, force_log],
                  real_clips=[*creature_clips, *force_clips])
    COMPONENT.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(creature))


def live_combat(link, report):
    live = json.loads(report.read_text())
    ordinary = observe_live(link, report_file=report, require_ordinary_attack=False)
    rows = [json.loads(line) for line in (WS / live['events']['file']).read_text().splitlines()]
    debug = [row['value'] for row in rows if row['kind'] == 'debug_string']
    require(debug.index('RF455 Protocol:map-bsp:0:1:0') < debug.index('RF455 Protocol:position-mode:0:0:0')
            < debug.index('RF455 WorldCapture:2:0:640x500'), 'Live NeutralB renders after position acceptance')
    require(len(live['world_frames']) == 2, 'Two real world frames')
    for frame in live['world_frames']:
        check(frame)
    prefix = 'RF455 Protocol:creature-attack-result:'
    incoming = [list(map(int, value[len(prefix):].split(':'))) for value in debug if value.startswith(prefix)]
    return dict(report=record(report), ordinary=ordinary, world_frames=live['world_frames'],
                incoming_resolved=[row for row in incoming if row[1]])


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
    observed = [live_combat(link, report) for report in LIVE_RUNS]
    incoming_seen = any(run['incoming_resolved'] for run in observed)
    names = ('normal-link', 'normal-preparation', 'normal-build', 'normal-consumers', 'own-entry',
             'startup-audit', 'startup-taiwan-native', 'live-launcher-native', 'creature-attacks-reference')
    sources = ('client455_armed_attack_port.py', 'native/client455_normal_attack_dispatch.inc',
               'native/client455_normal_attack_result.h', 'native/client455_monster_force_result_probe.cpp')
    save('creature-attacks-checkpoint', dict(
        status='PARTIAL_LIVE_CREATURE_ATTACKS' if incoming_seen else 'PARTIAL_COMPONENT_CREATURE_ATTACKS',
        scope='Incoming ordinary attacks from monsters, animus and guard towers.',
        normal_executable=link['executable'], normal_link_sha256=sha(path('normal-link')),
        runtime_login_report=record(LIVE_RUNS[-1]), observations=observed, component=record(COMPONENT),
        script=record(Path(__file__)), sources=[record(WS / 'scripts' / name) for name in sources],
        fresh_evidence={name: record(path(name)) for name in names}, M6='OPEN', M9='OPEN'))
    print(json.dumps(observed))


if __name__ == '__main__':
    main()
