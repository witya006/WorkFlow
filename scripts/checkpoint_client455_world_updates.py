"""Bind selected world update routes, record shapes, and live owner results."""
import collections
import json
import math
import struct
from pathlib import Path

from build_client455_x87_math import read_va
from checkpoint_client455_party_window import path, read, save
from checkpoint_client455_rvp_effects import check, require, sha
from checkpoint_client455_world_observation import sample_values
from client455_reference_regions import verify_regions
from client455_ui_checkpoint import own_symbols, record
from compare_client_binaries import WS


PRIVATE = WS / 'artifacts/client455-progress'
RAW = PRIVATE / 'position185-reference.json'
BASE = 0x400000
POSITION_BRANCHES = {3: 0x5c1430, 5: 0x5c1452, 10: 0x5c15cd, 12: 0x5c1600,
                     17: 0x5c151e, 25: 0x5c1589, 34: 0x5c15de}
CALLS = {0x563285: 0x565410, 0x561057: 0x5c12a0, 0x5c1437: 0x5c2bf0,
         0x5c1459: 0x5c2cd0, 0x5c15d4: 0x5c4810, 0x5c1590: 0x5c4270, 0x5c15e5: 0x5c49d0}


def verify_reference():
    proof = verify_regions(RAW)
    raw = json.loads(RAW.read_text())
    require(raw['closed']['success'] and raw['closed']['saved'], 'Owned IDA session must close')
    for pin in proof['references']:
        binary = (WS / pin['file']).read_bytes()
        for site, target in CALLS.items():
            branch = read_va(binary, site, 5)
            require(branch[0] == 0xe8 and site + 5 + struct.unpack_from('<i', branch, 1)[0] == target,
                    'Confirmed dispatcher call ' + hex(site - BASE))
        require(read_va(binary, 0xad2d78, 4) == struct.pack('<I', 0x5c13e0), 'Position virtual receiver')
        for opcode, expected in POSITION_BRANCHES.items():
            index = read_va(binary, 0x5c1774 + opcode - 3, 1)[0]
            require(read_va(binary, 0x5c16d4 + index * 4, 4) == struct.pack('<I', expected),
                    'Position dispatcher branch ' + str(opcode))
        for site in (0x5c151e, 0x5c160d):
            jump = read_va(binary, site, 5)
            require(jump[0] == 0xe9 and site + 5 + struct.unpack_from('<i', jump, 1)[0] == 0x5c16c7,
                    'Position no-op reaches common accepted return')
        require(read_va(binary, 0x5c16c7, 2) == b'\xb0\x01', 'Accepted return value')
    return dict(**proof, raw=record(RAW), position_dispatch_rva='0x1c13e0',
                routes={'3/16': 'monster spawn', '4/3': 'local move error',
                        '4/5': 'monster move', '4/10': 'actor position refresh',
                        '4/12': 'accepted without world changes', '4/25': '64-bit player status',
                        '4/34': 'single-byte owner update'})


def main():
    live_path = PRIVATE / 'client455-world-walk-live-taiwan-native.json'
    live = json.loads(live_path.read_text())
    link = read('normal-link')
    digest = sha(path('normal-link'))
    require(digest == live['normal_link_sha256'] and live['executable'] == link['executable']
            and sha(WS / live['staged_executable']) == link['executable']['sha256'], 'Exact own PE')
    native = read('initial-download-native')
    require(native['normal_link_sha256'] == digest and native['status'] == 'PASS'
            and all(native['native'][name] == size for name, size in
                    [('world_spawn_bytes', 17), ('world_move_bytes', 14), ('world_status_bytes', 12)])
            and native['native']['bad_sizes_rejected'], 'Own wire boundary fixtures')
    check(live['events'])
    events = [json.loads(line) for line in (WS / live['events']['file']).read_text().splitlines()]
    messages = [event['value'] for event in events if event['kind'] == 'debug_string']
    records = [m.removeprefix('RF455 Protocol:') for m in messages if m.startswith('RF455 Protocol:')]
    counts = collections.Counter(records)
    key_down = next(i for i, m in enumerate(records) if m.startswith('walk-key-down:'))
    statuses = [i for i, m in enumerate(records) if m == 'player-status-update:1:1:12']
    require(len(statuses) == counts['rx:4:25:12'] > 0 and max(statuses) < key_down,
            'Actual own avatar status was handled before the first walk input')
    spawn = [m for m in records if m.startswith('monster-spawn:')]
    moves = [m for m in records if m.startswith('monster-move:')]
    require(len(spawn) == counts['rx:3:16:17'] > 0 and len(moves) == counts['rx:4:5:14'] > 0,
            'All observed monster records reached the selected handlers')
    require(counts['position-noop:4:12:16'] == counts['rx:4:12:16'] > 0, 'Ordinary position no-op dispatch')
    samples = [sample_values(m) for m in messages if m.startswith('RF455 WorldSample:')]
    require(len(samples) == 6 and samples[-2]['avatar_position'] == samples[-1]['avatar_position']
            and math.dist(samples[0]['avatar_position'], samples[-1]['avatar_position']) > 2
            and counts['move-queued:4:1:12'] > 0 and counts['move-queued:4:12:6'] > 0,
            'Movement and stopping regression')
    require(live['debugger_exit'] == 0 and live['summary']['exit_observed']
            and any(row['kind'] == 'selection_observation_end' for row in events)
            and not any(row['kind'] == 'exception' and not row.get('first_chance') for row in events)
            and live['live_server']['private_handoff_removed'], 'Own run ended cleanly')
    save('world-updates-reference', verify_reference())
    names = ('normal-link', 'normal-preparation', 'normal-build', 'normal-consumers', 'own-entry', 'startup-audit',
             'startup-taiwan-native', 'live-launcher-native', 'initial-download-native', 'world-updates-reference')
    fresh = {name: record(path(name)) for name in names}
    fresh['world-updates-live'] = record(live_path)
    fresh['world-updates-raw'] = record(RAW)
    symbols = ('?InitMsg_MonsterSpawn455@CNetworkMgr@@', '?PositionMsg_MonsterMove455@CNetworkMgr@@',
               '?PositionMsg_PlayerStatus455@CNetworkMgr@@')
    mapped = {name: hex(rva) for rva, name in own_symbols(link) if name.startswith(symbols)}
    require(len(mapped) == len(symbols), 'Selected own world handlers must be linked')
    spawn_applied = sum(m.split(':')[2] == '1' for m in spawn)
    move_applied = sum(m.split(':')[1] == '1' for m in moves)
    save('world-updates-checkpoint', dict(
        status='PARTIAL_LIVE_WORLD_UPDATE_DISPATCH', normal_executable=link['executable'], normal_link_sha256=digest,
        scope='Ordinary NeutralB applies its avatar status, accepts the position no-op, and decodes monster spawn and movement.',
        fresh_evidence=fresh, runtime_login_report=record(live_path), script=record(Path(__file__)),
        sources=[record(WS / 'scripts' / name) for name in
                 ('client455_world_update_port.py', 'native/client455_world_updates.h',
                  'native/client455_world_monster_spawn.inc', 'native/client455_world_position.inc')],
        own_symbols=mapped, monster_spawn_records=len(spawn), monster_spawn_applied=spawn_applied,
        monster_move_records=len(moves), monster_move_applied=move_applied,
        avatar_status_updates_before_input=len(statuses), accepted_noop=counts['position-noop:4:12:16'],
        refresh_packets_unported=counts['rx:4:10:8'], single_byte_updates_unported=counts['rx:4:34:1'],
        own_move_error_packets=sum(n for m, n in counts.items() if m.startswith('rx:4:3:')),
        matched_server_movement_ack=False, own_avatar_walk_and_stop_verified=True,
        server_modified=False, M6='OPEN', M9='OPEN'))
    print(f'PARTIAL: monster spawn {spawn_applied}/{len(spawn)}, move {move_applied}/{len(moves)}, '
          f'avatar status {len(statuses)}, position no-op {counts["position-noop:4:12:16"]}')


if __name__ == '__main__':
    main()
