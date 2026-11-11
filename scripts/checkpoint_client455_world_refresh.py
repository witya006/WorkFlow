"""Check 455 object visibility refresh against both references and an own world run."""

import collections
import json
import struct
from pathlib import Path

from build_client455_x87_math import read_va
from checkpoint_client455_party_window import path, read, save
from checkpoint_client455_rvp_effects import check, require, sha
from checkpoint_client455_world_observation import sample_values
from client455_reference_regions import verify_regions
from client455_ui_checkpoint import own_symbols, record
from compare_client_binaries import WS


PRIVATE = WS / 'artifacts/client455-progress/position187'
RAW = PRIVATE / 'reference.json'
LIVE = PRIVATE / 'live.json'
BASE = 0x400000
CALLS = {
    0x5c15d4: 0x5c4810, 0x5c4843: 0x51c130, 0x5c4856: 0x7cf050,
    0x5c488e: 0x51c3e0, 0x5c48a1: 0x7cf050, 0x5c48b5: 0x527ab0,
    0x5c48c8: 0x7cf050, 0x51c3f7: 0x51c130,
    0x5c0f3c: 0x5c07d0, 0x5c0809: 0x5c05c0, 0x5c0f49: 0x5c07a0,
    0x5c49ee: 0x5c4a00, 0x4130f2: 0x413140,
    0x497c2e: 0x413140, 0x833537: 0x413140,
}


def verify_reference():
    proof = verify_regions(RAW)
    session = json.loads(RAW.read_text())
    require(session['closed']['success'] and session['closed']['saved'], 'Owned reference session closed')
    for pin in proof['references']:
        binary = (WS / pin['file']).read_bytes()
        for site, target in CALLS.items():
            branch = read_va(binary, site, 5)
            require(branch[0] == 0xe8 and site + 5 + struct.unpack_from('<i', branch, 1)[0] == target,
                    f'Exact CALL at RVA {site - BASE:#x}')
        require(read_va(binary, 0x5c4a12, 6) == bytes.fromhex('88 88 60 5f 00 00'),
                'One-byte avatar state write')
    save('world-refresh-reference', dict(
        **proof, raw=record(RAW), refresh_dispatch_rva='0x1c4810', refresh_owner_rva='0x3cf050',
        actor_lookup_rva='0x11c130', parked_unit_lookup_rva='0x11c3e0', ground_lookup_rva='0x127ab0',
        scope='Refresh flag and clock, 4/5 interpolation call chain, and 4/34 avatar byte consumer evidence.',
        avatar_region_byte=dict(offset='0x5f60', writer_rva='0x1c4a00', predicate_rva='0x13140')))


def observe_live(link, digest):
    live = json.loads(LIVE.read_text())
    require(live['normal_link_sha256'] == digest and live['executable'] == link['executable']
            and sha(WS / live['staged_executable']) == link['executable']['sha256'], 'Exact own world PE')
    check(live['events'])
    events = [json.loads(line) for line in (WS / live['events']['file']).read_text().splitlines()]
    require(live['debugger_exit'] == 0 and live['summary']['exit_observed']
            and live['live_server']['private_handoff_removed']
            and not any(row['kind'] == 'exception' and not row.get('first_chance') for row in events),
            'Clean ordinary world run')
    prefix = 'RF455 Protocol:'
    debug = [row['value'] for row in events if row['kind'] == 'debug_string']
    counts = collections.Counter(tuple(value[len(prefix):].split(':')) for value in debug
                                 if value.startswith(prefix))
    refresh = collections.Counter()
    for row, count in counts.items():
        if row[0] == 'position-refresh':
            _, kind, actor, applied = row
            refresh[int(kind), int(actor), applied == '1'] = count
    monster_refreshes = refresh[0, 1, True]
    require(sum(refresh.values()) == counts['rx', '4', '10', '8'] and monster_refreshes > 0,
            'Every observed 4/10 was dispatched and monster refreshes reached actual actors')
    spawns = sum(count for row, count in counts.items() if row[0] == 'monster-spawn' and row[2] == '1')
    moves = counts['monster-move', '1', '0', '14']
    samples = [sample_values(value) for value in debug if value.startswith('RF455 WorldSample:')]
    require(spawns > 0 and moves > 0 and len(samples) == 6 and
            samples[0]['avatar_position'] != samples[-1]['avatar_position'] and
            samples[-2]['avatar_position'] == samples[-1]['avatar_position'], 'Selected prior walk/spawn/move regression')
    return dict(refresh_records=sum(refresh.values()), monster_refreshes_applied=monster_refreshes,
                refresh_results=[dict(kind=key[0], type=key[1], applied=key[2], count=count)
                                 for key, count in sorted(refresh.items())],
                monster_spawn_applied=spawns, monster_move_applied=moves,
                town_state_packets=counts['rx', '4', '34', '1'], own_walk_verified=True)


def main():
    verify_reference()
    link = read('normal-link')
    digest = sha(path('normal-link'))
    native = read('initial-download-native')
    require(native['normal_link_sha256'] == digest and native['status'] == 'PASS'
            and native['native']['world_refresh_bytes'] == 8
            and native['native']['refresh_owner_routes'] == 4, 'Exact ordinary owner and wire checks')
    for evidence in ('source', 'world_header', 'executable'):
        check(native[evidence])
    observed = observe_live(link, digest)
    own = {name: hex(rva) for rva, name in own_symbols(link)
           if name.startswith('?PositionMsg_ObjectRefresh455@CNetworkMgr@@')}
    require(len(own) == 1, 'Own object refresh handler is linked')
    names = ('normal-link', 'normal-preparation', 'normal-build', 'normal-consumers', 'own-entry',
             'startup-audit', 'startup-taiwan-native', 'live-launcher-native',
             'initial-download-native', 'world-refresh-reference')
    fresh = {name: record(path(name)) for name in names}
    fresh.update({'world-refresh-live': record(LIVE), 'world-refresh-raw': record(RAW)})
    sources = ('scripts/client455_world_update_port.py', 'scripts/native/client455_world_updates.h',
               'scripts/native/client455_world_position.inc', 'scripts/native/client455_initial_download_probe.cpp')
    save('world-refresh-checkpoint', dict(
        status='PARTIAL_LIVE_WORLD_REFRESH', scope='Ordinary NeutralB refreshes existing objects without changing coordinates.',
        normal_executable=link['executable'], normal_link_sha256=digest, own_symbols=own,
        fresh_evidence=fresh, runtime_login_report=record(LIVE), script=record(Path(__file__)),
        sources=[record(WS / source) for source in sources], **observed,
        town_state_consumers_ported=False, full_monster_motion_accepted=False, server_modified=False,
        M6='OPEN', M9='OPEN'))
    print(json.dumps(observed))


if __name__ == '__main__':
    main()
