"""Verify the ordinary monster pick and the first live attack failure."""

import json
import struct
from pathlib import Path

from build_client455_x87_math import read_va
from checkpoint_client455_party_window import path, read, save
from checkpoint_client455_rvp_effects import check, require, sha
from client455_reference_regions import verify_regions
from client455_ui_checkpoint import own_symbols, record
from compare_client_binaries import WS


PRIVATE = WS / 'artifacts/client455-progress/combat200'
REFERENCE = PRIVATE / 'reference.json'
LIVE = PRIVATE / 'live.json'
LINK_MAP = PRIVATE / 'normal.map'


def verify_reference():
    proof = verify_regions(REFERENCE)
    raw = json.loads(REFERENCE.read_text())
    require(raw['closed']['success'] and raw['closed']['saved'], 'Owned IDA session closed')
    calls = {
        0x5a49d7: 0x5a44d0, 0x5a4557: 0x5a4a10, 0x5a467a: 0x5a54e0,
        0x5a45ce: 0x5a5510, 0x5a45df: 0x5a55a0, 0x5a45f0: 0x5a5630, 0x5a466c: 0x5a5a00,
        0x5a4a83: 0x5a42d0, 0x5a4aad: 0x5a34c0,
    }
    for pin in proof['references']:
        binary = (WS / pin['file']).read_bytes()
        require(read_va(binary, 0xad223c, 4) == struct.pack('<I', 0x5a4500), 'Combat dispatcher vtable')
        for site, target in calls.items():
            require(read_va(binary, site, 5) == b'\xe8' + struct.pack('<i', target - site - 5),
                    'Combat call site ' + hex(site))
        require(read_va(binary, 0x5a49cc, 2) == b'\x6a\x08' and
                read_va(binary, 0x5a49d2, 2) == b'\x6a\x01', 'Ordinary attack sends opcode 1 and eight bytes')
    result = raw['details']['0x5a4a10']['code']
    targets = raw['details']['0x5a42d0']['code']
    require('v7 + 11' in result and 'v7 + 10' in result and '14 * i + 5' in targets,
            'Ordinary result uses an 11-byte prefix and 14-byte target records')
    save('live-combat-reference', dict(
        **proof, raw=record(REFERENCE), scope='Ordinary 455 attack request and combat dispatcher routes.',
        calls={hex(site - 0x400000): hex(target - 0x400000) for site, target in calls.items()},
        ordinary_request=dict(category=5, opcode=1, payload_bytes=8),
        ordinary_result=dict(category=5, opcode=7, prefix_bytes=11, target_stride=14,
                             target_count_offset=10, target_damage_offset=5),
        adjacent_routes={'5/6': 'clear request latch', '5/13': 'monster attack', '5/14': 'animus attack',
                         '5/15': 'guard attack', '5/16': 'returns without dispatching'}))


def verify_live(link):
    live = json.loads(LIVE.read_text())
    require(live['normal_link_sha256'] == sha(path('normal-link')) and live['executable'] == link['executable'],
            'Exact own combat build')
    check(dict(file=live['staged_executable'], sha256=link['executable']['sha256']))
    check(dict(file=LINK_MAP.relative_to(WS).as_posix(), sha256=link['map']['sha256']))
    check(live['events'])
    require(live['debugger_exit'] == 0 and live['summary']['exit_observed']
            and live['live_server']['private_handoff_removed'], 'Observed own exit and handoff cleanup')
    events = [json.loads(line) for line in (WS / live['events']['file']).read_text().splitlines()]
    messages = [row['value'] for row in events if row['kind'] == 'debug_string']
    spawns = [value for value in messages if value.startswith('RF455 Protocol:monster-spawn:')]
    require(spawns and all(value.endswith(':1:17') for value in spawns), 'Server monsters created')
    clicks = [value.split(':')[-3:] for value in messages if value.startswith('RF455 Protocol:combat-click:')]
    picks = [value.split(':')[-3:] for value in messages if value.startswith('RF455 Protocol:combat-pick:')]
    serial = clicks[0][1] if clicks else None
    require(len(clicks) == 3 and [step for step, _, _ in clicks] == ['1', '2', '3']
            and all(target == serial for _, target, _ in clicks)
            and picks == [['1', serial, '0']] * 3, 'Three mouse picks resolve the same server monster')
    require(messages.index(f'RF455 Protocol:combat-click:2:{serial}:{clicks[1][2]}')
            < messages.index('RF455 Protocol:tx:5:14:1')
            < messages.index(f'RF455 Protocol:combat-click:3:{serial}:{clicks[2][2]}'),
            'Legacy combat-mode send between click 2 and click 3')
    require(not any(value.startswith(('RF455 Protocol:tx:5:1:', 'RF455 Protocol:rx:5:'))
                    for value in messages), 'No ordinary attack request or category 5 response')
    fatal = [row for row in events if row['kind'] == 'exception' and not row.get('first_chance')]
    require(len(fatal) == 1 and fatal[0]['code'] == '0xe06d7363', 'One unhandled C++ exception')
    stack = next(row for row in events if row['kind'] == 'fatal_context')
    symbols = own_symbols(dict(map=record(LINK_MAP)))
    expected = ('?GetNormalItem@CPlayerProc@@', '?NormalAttack@CAvatar@@',
                '?Attack@CAvatar@@', '?ProcessMousePicking_Character_Attack@CGP_MainGame@@')
    owners = []
    for row in stack['own_stack_rva_candidates']:
        rva = int(row['rva'], 16)
        start, name = max((start, name) for start, name in symbols if start <= rva)
        if name.startswith(expected):
            owners.append(dict(symbol=name, rva=row['rva'], offset=hex(rva - start)))
    require(len(owners) == len(expected) and
            all(row['symbol'].startswith(prefix) for row, prefix in zip(owners, expected)), 'Combat exception stack')
    frames = live['monster_frames']
    require(len(frames) == 3, 'Three rendered monster frames')
    for frame in frames:
        check(frame)
    draws = [value.split(':') for value in messages if value.startswith('RF455 MonsterFrame:')]
    require(len(draws) == len(frames) and all(draw[3] == serial and draw[7] == '0' for draw in draws),
            'All captures contain the picked monster and successful device readbacks')
    animations = [int(draw[5]) for draw in draws]
    require(animations == [0, 0, 16], 'Rendered transition from standing to walking')
    return dict(monster=int(serial), spawns=len(spawns), click_ms=[int(ms) for _, _, ms in clicks],
                monster_frames=frames, monster_animation_ids=animations, mode_request_sent=True, ordinary_attack_sent=False,
                fatal_code=fatal[0]['code'], stack_owners=owners)


def main():
    verify_reference()
    link = read('normal-link')
    live = verify_live(link)
    names = ('normal-link', 'normal-preparation', 'normal-build', 'normal-consumers', 'live-combat-reference',
             'own-entry', 'startup-audit', 'startup-taiwan-native', 'live-launcher-native')
    save('live-combat-checkpoint', dict(
        status='PARTIAL_LIVE_ATTACK_BLOCKED', scope='Live mouse target selection and first ordinary attack failure.',
        normal_executable=link['executable'], normal_link_sha256=sha(path('normal-link')),
        runtime_login_report=record(LIVE), first_attempt=record(PRIVATE / 'first-live.json'),
        saved_link_map=record(LINK_MAP),
        observations=live, script=record(Path(__file__)), fresh_evidence={name: record(path(name)) for name in names},
        M6='OPEN', M9='OPEN'))
    print(json.dumps({key: value for key, value in live.items() if key != 'monster_frames'}))


if __name__ == '__main__':
    main()
