"""Verify position wire records, the ordinary dispatch, and scoped live walking."""

import argparse
import hashlib
import json
import math
import struct
from pathlib import Path

from build_client455_x87_math import read_va
from checkpoint_client455_monster_force_damage import run_fixture
from checkpoint_client455_party_window import path, read, save
from checkpoint_client455_rvp_effects import check, require, sha
from checkpoint_client455_world_observation import sample_values
from client455_normal_link_evidence import validate_normal_link
from client455_own_probe import build_full_object_probe
from client455_reference_regions import verify_regions
from client455_ui_checkpoint import record
from compare_client_binaries import WS


REFERENCE = WS / 'artifacts/client455-progress/movement213/reference.json'
SEED_REFERENCE = REFERENCE.with_name('base-seed-reference.json')
COUNTER_REFERENCE = REFERENCE.with_name('counter-reference.json')
REJECTED_RUN = REFERENCE.with_name('first-success.json')
REJECTED_REENTRY = REFERENCE.with_name('failed-reentry.json')
SERVER_REJECTIONS = REFERENCE.with_name('server-rejections.json')
LIVE = WS / 'artifacts/client455-progress/client455-world-movement-live-taiwan-native.json'
FIRST_ATTEMPT = WS / 'work/m9/be020c26/world-movement-live-taiwan001/debug-events.jsonl'
REENTRY = WS / 'artifacts/client455-progress/client455-world-observation-live-taiwan-native.json'
CALLS = {
    0x5c1edf: 0x562e00, 0x5c1ef9: 0x5c13b0,
    0x5c2bae: 0x562e00, 0x5c2bbe: 0x5c13b0,
    0x5c3b7e: 0x562e00, 0x5c3b8e: 0x5c13b0,
    0x5c3c38: 0x5c0820, 0x5c3c6f: 0x530d40,
}


def verify_reference():
    proof = verify_regions(REFERENCE)
    raw = json.loads(REFERENCE.read_text(encoding='utf-8'))
    require(raw['closed']['success'] and raw['closed']['saved'], 'Owned IDA session closed')
    seed = json.loads(SEED_REFERENCE.read_text(encoding='utf-8'))
    require(seed['closed']['success'] and seed['closed']['saved'], 'Base packet IDA session closed')
    counter = json.loads(COUNTER_REFERENCE.read_text(encoding='utf-8'))
    require(counter['closed']['success'] and counter['closed']['saved'], 'Position counter IDA session closed')
    seed_regions = []
    for pin in proof['references']:
        binary = (WS / pin['file']).read_bytes()
        for site, target in CALLS.items():
            require(read_va(binary, site, 5) == b'\xe8' + struct.pack('<i', target - site - 5),
                    f'455 position call at {site:#x}')
        require(read_va(binary, 0x56a99f, 7) == b'\xc6\x80\x00\xa7\x06\x00\x01',
                'World entry enables local prediction')
        require(read_va(binary, 0x5c139f, 7) == b'\xc7\x40\x08\x01\x00\x00\x00',
                'Original position sequence starts at one')
        for site, expected in {
            0x56cea3: '8a8d72feffff8888fca60600',
            0x56ceb2: '668b8d73feffff668988fea60600',
        }.items():
            require(read_va(binary, site, len(bytes.fromhex(expected))).hex() == expected,
                    f'Base download seed assignment at {site:#x}')
        seed_bytes = read_va(binary, 0x56cea0, 32)
        seed_regions.append(dict(binary=pin['sha256'], rva='0x16cea0', bytes=32,
                                 sha256=hashlib.sha256(seed_bytes).hexdigest()))
    save('avatar-movement-reference', dict(
        **proof, raw=record(REFERENCE), seed_raw=record(SEED_REFERENCE), seed_regions=seed_regions,
        counter_raw=record(COUNTER_REFERENCE), initial_sequence=1, base_seed_offsets=[54, 55],
        move=[4, 1, 26], position_report=[4, 2, 16],
        stop=[4, 19, 16], move_broadcast=[4, 4, 17], stop_result=[4, 20, 10],
        move_lanes=dict(move_mode=0, coordinates=1, sequence=13, target_xz=17, flags=21, speed=22),
        original_calls={hex(site - 0x400000): hex(target - 0x400000) for site, target in CALLS.items()}))


def verify_live(link):
    live = json.loads(LIVE.read_text(encoding='utf-8'))
    require(live['normal_link_sha256'] == sha(path('normal-link')) and
            live['executable'] == link['executable'] and
            sha(WS / live['staged_executable']) == link['executable']['sha256'],
            'Exact linked own live executable')
    require(live['debugger_exit'] == 0 and live['summary']['exit_observed'] and
            live['live_server']['private_handoff_removed'] and
            not any(not row.get('first_chance') for row in live['exceptions']),
            'Normal live session ended without an unhandled exception')
    check(live['events'])
    protocol = live['protocol_observations']
    down = next(value for value in protocol if value.startswith('RF455 Protocol:walk-key-down:38:'))
    up = next(value for value in protocol if value.startswith('RF455 Protocol:walk-key-up:38:'))
    held_ms = int(up.split(':')[3]) - int(down.split(':')[3])
    require(held_ms >= 7500, 'Eight-second scoped walk')
    steps = protocol[protocol.index(down):]
    sent = {key: steps.count(f'RF455 Protocol:move-queued:4:{opcode}:{size}')
            for key, opcode, size in [('move', 1, 26), ('report', 2, 16), ('stop', 19, 16)]}
    require(all(sent.values()) and not any('walk-key-restore-failed' in value for value in steps),
            'All three position routes queued during ordinary input and stopping')
    samples = [sample_values(value) for value in live['world_observations']
               if value.startswith('RF455 WorldSample:')]
    require(len(samples) == 6 and all(sample['input_enabled'] for sample in samples),
            'Six ordinary world samples')
    displacement = math.dist(samples[0]['avatar_position'], samples[-1]['avatar_position'])
    require(displacement > 2 and samples[-1]['avatar_position'] == samples[-2]['avatar_position'] and
            samples[-1]['avatar_action'] == samples[0]['avatar_action'], 'Stable stopped position after walking')
    require(not any(value.startswith('RF455 Protocol:movement-zero-position:') for value in protocol)
            and all(sample['avatar_position'][0] or sample['avatar_position'][2] for sample in samples),
            'No coordinate reset observed')
    received = {key: sum(value.startswith(f'RF455 Protocol:rx:4:{opcode}:') for value in steps)
                for key, opcode in [('correction', 3), ('movement', 4), ('stop', 20)]}
    require(received['movement'] > 0 and 'RF455 Protocol:move-broadcast:4:1:17' in steps,
            'Local server returns an accepted movement for this avatar')
    require(received['stop'] > 0 and 'RF455 Protocol:move-stop-result:4:1:10' in steps,
            'Local server returns the stop for this avatar')
    initial = [json.loads(line) for line in FIRST_ATTEMPT.read_text(encoding='utf-8').splitlines()]
    initial_messages = [row['value'] for row in initial if row['kind'] == 'debug_string']
    initial_samples = [sample_values(value) for value in initial_messages
                       if value.startswith('RF455 WorldSample:')]
    require(len(initial_samples) == 6 and
            all(sample['avatar_position'] == initial_samples[0]['avatar_position'] for sample in initial_samples) and
            'RF455 Protocol:move-queued:4:1:26' in initial_messages,
            'Earlier build reproduced standing still despite a queued move')
    rejections = json.loads(SERVER_REJECTIONS.read_text(encoding='utf-8-sig'))
    require(rejections['message'] == 'movement counter replay/regression' and rejections['count'] > 0,
            'Server reported counter rejections before base seed support')
    return dict(report=record(LIVE), events=live['events'], held_ms=held_ms, displacement=displacement,
                sent=sent, received=received, samples=samples, zero_position_observed=False,
                first_attempt=record(FIRST_ATTEMPT), old_wire_run=record(REJECTED_RUN),
                old_wire_reentry=record(REJECTED_REENTRY), server_rejections=record(SERVER_REJECTIONS))


def verify_reentry(link, movement):
    report = json.loads(REENTRY.read_text(encoding='utf-8'))
    require(report['normal_link_sha256'] == sha(path('normal-link')) and
            report['executable'] == link['executable'] and
            sha(WS / report['staged_executable']) == link['executable']['sha256'] and
            report['debugger_exit'] == 0 and report['live_server']['private_handoff_removed'] and
            not any(not row.get('first_chance') for row in report['exceptions']),
            'Same own build starts another live session')
    check(report['events'])
    events = [json.loads(line) for line in (WS / report['events']['file']).read_text(encoding='utf-8').splitlines()]
    messages = [row['value'] for row in events if row['kind'] == 'debug_string']
    first_sample = next(value for value in messages if value.startswith('RF455 WorldSample:0:'))
    earlier = messages[:messages.index(first_sample)]
    require('RF455 Protocol:position-mode:0:0:0' in earlier and
            not any(value.startswith('RF455 Protocol:tx:4:1:') for value in earlier),
            'Accepted position before any movement in the follow-up')
    sample = sample_values(first_sample)
    before, after = [entry['avatar_position'] for entry in
                     (movement['samples'][0], movement['samples'][-1])]
    position = sample['avatar_position']
    horizontal_error = math.hypot(position[0] - after[0], position[2] - after[2])
    previous_error = math.hypot(position[0] - before[0], position[2] - before[2])
    walk_events = [json.loads(line) for line in (WS / movement['events']['file']).read_text(
        encoding='utf-8').splitlines()]
    walk_messages = [row['value'] for row in walk_events if row['kind'] == 'debug_string']
    last_sample = next(index for index, value in enumerate(walk_messages)
                       if value.startswith('RF455 WorldSample:5:'))
    later_moves = walk_messages[last_sample + 1:].count('RF455 Protocol:move-broadcast:4:1:17')
    exact_stop_position = horizontal_error < 2
    require(previous_error > 10 and (exact_stop_position or later_moves > 0),
            'The next login receives a changed position after confirmed movement')
    return dict(report=record(REENTRY), events=report['events'], position=position,
                distance_from_start=previous_error, distance_from_stop_sample=horizontal_error,
                exact_stop_sample_match=exact_stop_position, accepted_moves_after_last_sample=later_moves)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--with-live', action='store_true')
    parser.add_argument('--with-reentry', action='store_true')
    args = parser.parse_args()
    if args.with_reentry and not args.with_live:
        parser.error('--with-reentry requires --with-live')
    verify_reference()
    link = read('normal-link')
    require(validate_normal_link(link) == 'PASS', 'Exact current normal link')
    link_sha = sha(path('normal-link'))
    startup = read('startup-taiwan-native')
    require(startup['normal_link_sha256'] == link_sha and startup['debugger_exit'] == 0 and
            startup['summary']['after_sound_reached'] and startup['summary']['exit_observed'],
            'Exact current early Taiwan startup')
    if args.with_live:
        base = read('initial-download-native')
        require(base['normal_link_sha256'] == link_sha and base['status'] == 'PASS',
                'Current base download decoder, including the position parameters')
    source = WS / 'scripts/native/client455_avatar_movement_probe.cpp'
    exe = build_full_object_probe('avatar-movement', source)
    native, console = run_fixture(exe, [], [], 'avatar-movement')
    require(native == dict(status='PASS', move_bytes=26, position_bytes=16, stop_bytes=16,
                           stop_result_bytes=10, move_result_bytes=17, exact_transport_bytes=True,
                           pending_correction=True, local_stop_threshold=10), 'Movement component evidence')
    live = verify_live(link) if args.with_live else None
    if args.with_reentry:
        live['reentry'] = verify_reentry(link, live)
    names = ('normal-link', 'normal-preparation', 'normal-build', 'normal-consumers',
             'own-entry', 'startup-audit', 'startup-taiwan-native', 'avatar-movement-reference')
    if args.with_live:
        names += ('initial-download-native',)
    sources = ('client455_avatar_movement_port.py', 'native/client455_avatar_movement.h',
               'native/client455_avatar_movement.inc', 'native/client455_avatar_movement_probe.cpp',
               'native/client455_world_entry.inc', 'native/client455_world_position.inc',
               'native/client455_initial_download.inc', 'native/client455_initial_download.h',
               'native/client455_initial_download_probe.cpp', 'probe_client455_initial_download.py',
               'native/client455_live_world_observation.inc', 'native/client455_protocol_observation.h',
               'native/client455_walk_observation.inc', 'native/own_client_startup_debugger.cpp',
               'probe_client455_device_startup.py', 'probe_client455_live_launcher.py')
    save('avatar-movement-checkpoint', dict(
        status='PARTIAL_LIVE_AVATAR_MOVEMENT' if live else 'PARTIAL_COMPONENT_AVATAR_MOVEMENT',
        scope='455 outbound movement, periodic position and stop; bounded movement and stop receive routes.',
        normal_executable=link['executable'], normal_link_sha256=link_sha,
        component=native, component_executable=record(exe), component_console=console, live=live,
        script=record(Path(__file__)), sources=[record(WS / 'scripts' / name) for name in sources],
        fresh_evidence={name: record(path(name)) for name in names},
        gaps=['The exact reported intermittent reset has not been reproduced.',
              'Mouse and special-mode movement, remote actor speed and full tutorial routing remain open.'],
        own_live_run=live is not None, M6='OPEN', M9='OPEN'))
    print(json.dumps(dict(executable=link['executable']['sha256'], component=native,
                          live={key: live[key] for key in ('held_ms', 'displacement', 'sent', 'received')} if live else None,
                          reentry=live.get('reentry') if live else None)))


if __name__ == '__main__':
    main()
