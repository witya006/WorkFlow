"""Pin the avatar town state, ordinary attack check and observed 4/34 dispatch."""

import collections
import json
import struct
from pathlib import Path

from audit_client455_language import records
from build_client455_x87_math import read_va
from checkpoint_client455_party_window import path, read, save
from checkpoint_client455_rvp_effects import check, require, sha
from client455_reference_regions import verify_regions
from client455_ui_checkpoint import own_symbols, record
from compare_client_binaries import WS


PRIVATE = WS / 'artifacts/client455-progress/town188'
RAW = PRIVATE / 'reference.json'
LIVE = PRIVATE / 'live.json'
BASE = 0x400000
CALLS = {
    0x5c15e5: 0x5c49d0, 0x5c49ee: 0x5c4a00,
    0x412ea0: 0x4130d0, 0x4130f2: 0x413140, 0x41311d: 0x52fe60,
    0x52fe73: 0x52fea0, 0x52fe83: 0x52ea70, 0x52feb3: 0x52e180,
    0x413610: 0x413770, 0x4137b3: 0x4638f0, 0x4137bf: 0x463ab0,
    0x4137ea: 0x413140, 0x463901: 0x463960, 0x46390f: 0x463960,
    0x463ad8: 0x463780,
}
AVATAR_BYTES = {
    0x4024c3: 'c6 80 60 5f 00 00 ff',
    0x4038cd: '8a 91 60 5f 00 00',
    0x4038d3: '88 90 60 5f 00 00',
    0x5c4a12: '88 88 60 5f 00 00',
}


def verify_reference():
    proof = verify_regions(RAW)
    session = json.loads(RAW.read_text())
    require(session['closed']['success'] and session['closed']['saved'], 'Closed reference IDA session')
    for pin in proof['references']:
        binary = (WS / pin['file']).read_bytes()
        for site, target in CALLS.items():
            branch = read_va(binary, site, 5)
            require(branch[0] == 0xe8 and site + 5 + struct.unpack_from('<i', branch, 1)[0] == target,
                    f'Exact town check CALL at RVA {site - BASE:#x}')
        for site, expected in AVATAR_BYTES.items():
            expected_bytes = bytes.fromhex(expected)
            require(read_va(binary, site, len(expected_bytes)) == expected_bytes,
                    f'Exact avatar field access at RVA {site - BASE:#x}')

    language = next(row for row in read('language-reference')['files'] if row['folder'] == 'ru-ru')
    file = WS / language['decoded']
    require(sha(file) == language['decoded_sha256'], 'Pinned Russian language payload')
    rows, _ = records(file.read_bytes())
    messages = {i: rows[i][1].decode('cp1251').rstrip('\0') for i in (128, 129)}
    require(messages == {128: 'Вы не может атаковать в городе',
                         129: 'Вы не можете использовать Умения/Силы в городе'}, 'Exact denial messages')
    save('town-state-reference', dict(
        **proof, raw=record(RAW), avatar_offset='0x5f60', default=255,
        initializer_rva='0x24c3', copy_rvas=['0x38cd', '0x38d3'],
        setter_rva='0x1c4a00', normal_attack_rva='0x130d0',
        skill_force_rva='0x13770', language=record(file), messages=messages))


def observe_live(link, digest):
    live = json.loads(LIVE.read_text())
    require(live['normal_link_sha256'] == digest and live['executable'] == link['executable'] and
            sha(WS / live['staged_executable']) == link['executable']['sha256'], 'Exact own world PE')
    check(live['events'])
    events = [json.loads(line) for line in (WS / live['events']['file']).read_text().splitlines()]
    require(live['debugger_exit'] == 0 and live['summary']['exit_observed']
            and live['live_server']['private_handoff_removed']
            and not any(row['kind'] == 'exception' and not row.get('first_chance') for row in events),
            'Clean ordinary world run')
    prefix = 'RF455 Protocol:'
    messages = collections.Counter(tuple(row['value'][len(prefix):].split(':')) for row in events
                                   if row['kind'] == 'debug_string' and row['value'].startswith(prefix))
    town = []
    for row, count in messages.items():
        if row[0] == 'town-state':
            _, value, outside, size = row
            require(size == '1' and 0 <= int(value) <= 255 and (outside == '1') == (int(value) == 255),
                    'Live avatar town byte and corresponding attack sentinel')
            town.append(dict(value=int(value), outside=outside == '1', count=count))
    require(sum(row['count'] for row in town) == messages['rx', '4', '34', '1'] > 0,
            'Live 4/34 reaches the avatar')
    refreshes = sum(count for row, count in messages.items() if row[0] == 'position-refresh' and row[3] == '1')
    require(refreshes > 0 and messages['monster-move', '1', '0', '14'] > 0
            and messages['move-queued', '4', '1', '12'] > 0
            and messages['move-queued', '4', '12', '6'] > 0, 'Selected world and walk regression')
    frame = next(row for row in live['world_frames'] if row['file'].endswith('/world-post-position-settled.png'))
    check(frame)
    require(frame['sha256'] == 'c8410c0b654a447101e48e29e5b46b3fac56711d49fb49455e338b269f8e2579',
            'Exact visually reviewed frame with a monster beside the avatar')
    return dict(town_state_updates=town, refreshes=refreshes, monster_moves=messages['monster-move', '1', '0', '14'],
                visible_monster_frame=frame)


def verify_own_field(link):
    owners = ('?PositionMsg_TownState455@CNetworkMgr@@', '?NormalAttack@CAvatar@@')
    own = {name: rva for rva, name in own_symbols(link) if name.startswith(owners)}
    require(len(own) == len(owners), 'Own town update and normal attack symbols')
    writer, attack = [next(rva for name, rva in own.items() if name.startswith(owner)) for owner in owners]
    binary = (WS / link['executable']['file']).read_bytes()
    # MSVC inlines CheckTownAttack455 into NormalAttack in this Release build.
    write_rva, read_rva = writer + 0x1b, attack + 0xfb
    write_code = read_va(binary, BASE + write_rva, 6)
    attack_code = read_va(binary, BASE + read_rva, 23)
    require(write_code[:2] == b'\x88\x88' and attack_code[:2] == b'\x80\xbf'
            and write_code[2:] == attack_code[2:6], 'Own receiver and attack use the same avatar field')
    require(attack_code[6:8] == b'\xff\x74' and attack_code[9:11] == b'\x83\xbe'
            and attack_code[15:17] == b'\x01\x74'
            and 9 + struct.unpack_from('<b', attack_code, 8)[0] == 18 + struct.unpack_from('<b', attack_code, 17)[0]
            and attack_code[18:] == b'\x68\x80\x00\x00\x00', 'Own inlined town rule and message index')
    return dict(symbols={name: hex(rva) for name, rva in own.items()},
                avatar_offset=hex(struct.unpack_from('<I', write_code, 2)[0]),
                write_rva=hex(write_rva), attack_read_rva=hex(read_rva))


def main():
    verify_reference()
    link = read('normal-link')
    digest = sha(path('normal-link'))
    native = read('initial-download-native')
    require(native['normal_link_sha256'] == digest and native['status'] == 'PASS'
            and native['native']['town_state_gate'], 'Current native avatar consumer probe')
    for evidence in ('source', 'executable'):
        check(native[evidence])
    observed = observe_live(link, digest)
    own = verify_own_field(link)
    names = ('normal-link', 'normal-preparation', 'normal-build', 'normal-consumers', 'own-entry',
             'startup-audit', 'startup-taiwan-native', 'live-launcher-native',
             'initial-download-native', 'town-state-reference')
    fresh = {name: record(path(name)) for name in names}
    fresh.update({'town-state-live': record(LIVE), 'town-state-raw': record(RAW)})
    sources = ('scripts/client455_world_update_port.py', 'scripts/native/client455_world_position.inc',
               'scripts/native/client455_initial_download_probe.cpp')
    save('town-state-checkpoint', dict(
        status='PARTIAL_LIVE_TOWN_STATE', scope='Ordinary live 4/34 updates the avatar. The native probe checks normal attacks.',
        normal_executable=link['executable'], normal_link_sha256=digest, own_field=own,
        fresh_evidence=fresh, runtime_login_report=record(LIVE), script=record(Path(__file__)),
        sources=[record(WS / source) for source in sources], **observed,
        live_attack_denial_verified=False, skill_force_town_checks_ported=False,
        server_modified=False, M6='OPEN', M9='OPEN'))
    print(json.dumps(observed))


if __name__ == '__main__':
    main()
