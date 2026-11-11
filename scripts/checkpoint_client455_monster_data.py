"""Verify the selected 455 monster table consumers and their ordinary world run."""

import collections
import json
import struct
from pathlib import Path

from build_client455_x87_math import read_va
from checkpoint_client455_party_window import path, read, save
from checkpoint_client455_rvp_effects import check, require, sha
from checkpoint_client455_world_observation import sample_values
from client455_reference_regions import verify_regions
from client455_ui_checkpoint import record
from compare_client_binaries import WS


PRIVATE = WS / 'artifacts/client455-progress'
RAW = PRIVATE / 'monster-data186/reference.json'
LIVE = PRIVATE / 'monster-data186/live.json'
BASE = 0x400000
CALLS = {
    0x56544c: 0x51bf00, 0x51bfc3: 0x51bfe0, 0x51c03a: 0x5fa540,
    0x5fa577: 0x5fa700, 0x5fa713: 0x5fa670, 0x5fa686: 0x5f0dc0,
}
SOURCES = ('scripts/client455_character_tables_port.py', 'scripts/native/client455_character_tables_probe.cpp',
           'scripts/native/client455_world_monster_spawn.inc')


def verify_reference():
    proof = verify_regions(RAW)
    raw = json.loads(RAW.read_text())
    require(raw['closed']['success'] and raw['closed']['saved'], 'Closed the owned IDA session')
    for pin in proof['references']:
        binary = (WS / pin['file']).read_bytes()
        for site, target in CALLS.items():
            branch = read_va(binary, site, 5)
            require(branch[0] == 0xe8 and site + 5 + struct.unpack_from('<i', branch, 1)[0] == target,
                    f'Exact monster lookup CALL at RVA {site - BASE:#x}')
        require(read_va(binary, 0xaaa664, 4) == struct.pack('<I', 0x45a470), 'Monster attribute vtable slot')
    save('monster-data-reference', dict(
        **proof, raw=record(RAW), row_order_lookup_rva='0x1f0dc0', attribute_initializer_rva='0x5a470',
        offsets={'mesh_key': 4, 'name': 8, 'attack_range': 56, 'walk_speed': 60,
                 'run_speed': 61, 'width': 62, 'scale': 64}))


def verify_native(link_digest):
    native = read('character-tables-native')
    require(native['normal_link_sha256'] == link_digest, 'Current full-object probe')
    check(native['source'])
    check(native['script'])
    require(len(native['runs']) == 5 and
            all(not run['natural_exit'] and run['native']['status'] == 'PASS' for run in native['runs']),
            'All ordinary table/actor cases passed')


def observe_live(link, link_digest):
    live = json.loads(LIVE.read_text())
    require(live['normal_link_sha256'] == link_digest and live['executable'] == link['executable']
            and sha(WS / live['staged_executable']) == link['executable']['sha256'], 'Exact world PE')
    check(live['events'])
    events = [json.loads(line) for line in (WS / live['events']['file']).read_text().splitlines()]
    exceptions = [row for row in events if row['kind'] == 'exception' and not row.get('first_chance')]
    require(live['debugger_exit'] == 0 and live['summary']['exit_observed'] and not exceptions
            and live['live_server']['private_handoff_removed'], 'Clean own-client world run')
    prefix = 'RF455 Protocol:'
    debug = [row['value'] for row in events if row['kind'] == 'debug_string']
    messages = [value[len(prefix):].split(':') for value in debug if value.startswith(prefix)]
    counts = collections.Counter(tuple(row) for row in messages)
    spawns = [row for row in messages if row[0] == 'monster-spawn']
    moves = [row for row in messages if row[0] == 'monster-move']
    meshes = collections.Counter(tuple(int(value) for value in row[1:])
                                 for row in messages if row[0] == 'monster-mesh')
    applied = sum(row[2] == '1' for row in spawns)
    moved = sum(row[1] == '1' for row in moves)
    require(len(spawns) == counts['rx', '3', '16', '17'] and applied > 0
            and len(moves) == counts['rx', '4', '5', '14'] and moved > 0
            and sum(meshes.values()) == applied, 'Actual monster spawn and movement')
    samples = [sample_values(value) for value in debug if value.startswith('RF455 WorldSample:')]
    require(len(samples) == 6 and samples[0]['avatar_position'] != samples[-1]['avatar_position']
            and samples[-2]['avatar_position'] == samples[-1]['avatar_position']
            and counts['move-queued', '4', '1', '12'] > 0 and counts['move-queued', '4', '12', '6'] > 0,
            'Scoped avatar movement and stopping still work')
    for frame in live['world_frames']:
        check(frame)
    return dict(spawn_records=len(spawns), spawn_applied=applied, move_records=len(moves), move_applied=moved,
                observed_meshes=[dict(record=key[0], mesh=key[1], width=key[2], count=count)
                                 for key, count in sorted(meshes.items())],
                avatar_status_applied=counts['player-status-update', '1', '1', '12'],
                noops=counts['position-noop', '4', '12', '16'],
                refresh_packets_unported=counts['rx', '4', '10', '8'],
                single_byte_updates_unported=counts['rx', '4', '34', '1'],
                scoped_avatar_walk_and_stop_verified=True, world_frames=live['world_frames'])


def main():
    verify_reference()
    link = read('normal-link')
    digest = sha(path('normal-link'))
    verify_native(digest)
    observed = observe_live(link, digest)
    names = ('normal-link', 'normal-preparation', 'normal-build', 'normal-consumers', 'own-entry', 'startup-audit',
             'startup-taiwan-native', 'live-launcher-native', 'character-tables-native', 'monster-data-reference',
             'live-resource-inputs', 'initial-download-native')
    fresh = {name: record(path(name)) for name in names}
    fresh['monster-data-live'] = record(LIVE)
    fresh['monster-data-raw'] = record(RAW)
    save('monster-data-checkpoint', dict(
        status='PARTIAL_LIVE_MONSTER_DATA', normal_executable=link['executable'], normal_link_sha256=digest,
        scope='Ordinary NeutralB creates monsters using Character.edf rows and applies selected movement updates.',
        fresh_evidence=fresh, runtime_login_report=record(LIVE), script=record(Path(__file__)),
        sources=[record(WS / name) for name in SOURCES], **observed,
        full_monster_rendering_accepted=False, full_monster_combat_accepted=False,
        server_modified=False, M6='OPEN', M9='OPEN'))
    print(json.dumps(observed))


if __name__ == '__main__':
    main()
