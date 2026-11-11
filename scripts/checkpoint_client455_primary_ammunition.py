"""Verify the 455 primary ammunition selector and ordinary attack observation."""

import argparse
import json
import struct
from pathlib import Path

from audit_client455_item_payloads import decode, item_tables, sequential, word
from build_client455_x87_math import read_va
from checkpoint_client455_party_window import path, read, save
from checkpoint_client455_rvp_effects import check, require, sha
from client455_normal_link_evidence import validate_normal_link
from client455_reference_regions import verify_regions
from client455_ui_checkpoint import record
from compare_client_binaries import WS


PRIVATE = WS / 'artifacts/client455-progress/ammunition203'
REFERENCE = PRIVATE / 'reference.json'
LIVE = PRIVATE / 'live.json'
DECODER = WS / 'work/client455-reference-inputs/normal-attack203-probe'
CALLS = {
    0x4167e2: 0x460dd0, 0x4168af: 0x460e70, 0x4168bb: 0x462d20,
    0x460ebf: 0x426e00, 0x460ed0: 0x426dd0, 0x460ed9: 0x4694f0,
    0x462cdd: 0x5fae60, 0x470da0: 0x40b200,
}


def row(table, index):
    size = table['stride']
    return table['data'][index * size:(index + 1) * size]


def verify_reference():
    proof = verify_regions(REFERENCE)
    evidence = json.loads(REFERENCE.read_text())
    require(evidence['closed']['success'] and evidence['closed']['saved'], 'Owned IDA session closed')
    for pin in proof['references']:
        binary = (WS / pin['file']).read_bytes()
        for site, target in CALLS.items():
            require(read_va(binary, site, 5) == b'\xe8' + struct.pack('<i', target - site - 5),
                    f'455 ammunition call at {site:#x}')

    root = Path(json.loads((WS / 'config/paths.json').read_text())['client_455']) / 'DataTable'
    item_file = root / 'Item.edf'
    force_file = root / 'SkillForce.edf'
    items, _, _ = item_tables(decode(item_file.read_bytes()))
    projectiles = sequential(decode(force_file.read_bytes()), 5)[3]
    arrow = row(items[11], 99)
    allowed = set(arrow[165:165 + arrow[164]])
    require(allowed == {0, 1, 2, 3} and arrow[232] == 0 and word(arrow, 216) == 0xffffffff,
            'Test arrows use the ordinary slots and type list')
    require(word(row(projectiles, 20), 0) == 20 and word(row(projectiles, 20), 4) == 21,
            'Special projectile has distinct code and effect index')
    bows = [row(items[6], i) for i in range(items[6]['count'])]
    bows = [entry for entry in bows if word(entry, 216) == 5]
    require(bows and all(allowed.intersection(entry[249:249 + word(entry, 256)]) for entry in bows),
            'All current bow records match the ordinary arrow list')
    save('primary-ammunition-reference', dict(
        **proof, raw=record(REFERENCE), scope='Primary 455 ammunition selection and request serial.',
        call_rvas={hex(site - 0x400000): hex(target - 0x400000) for site, target in CALLS.items()},
        primary_sockets=[12, 13], auxiliary_socket=14,
        weapon_types_offset=249, weapon_type_count_offset=256,
        ammunition_types_offset=165, ammunition_type_count_offset=164,
        special_weapon_id='0xa11107', special_projectile_index=20,
        test_ammunition_row=99, matching_bows=len(bows),
        data_files=[dict(file=p.as_posix(), sha256=sha(p)) for p in (item_file, force_file)]))
    return proof


def verify_live(link):
    live = json.loads(LIVE.read_text())
    require(live['normal_link_sha256'] == sha(path('normal-link')) and live['executable'] == link['executable'],
            'Exact own primary ammunition build')
    check(dict(file=live['staged_executable'], sha256=link['executable']['sha256']))
    check(live['events'])
    rows = [json.loads(line) for line in (WS / live['events']['file']).read_text().splitlines()]
    prefix = 'RF455 Protocol:'
    messages = [row['value'].removeprefix(prefix) for row in rows
                if row['kind'] == 'debug_string' and row['value'].startswith(prefix)]
    require(live['debugger_exit'] == 0 and live['summary']['exit_observed'] and
            live['live_server']['private_handoff_removed'], 'Observed own exit and private handoff cleanup')
    require('base-applied:0:8:8' in messages and 'inventory-applied:3:21:21' in messages and
            'equipped-ammunition:99:315:0' in messages, 'Ordinary base and inventory population')
    selected = [message.split(':')[1:] for message in messages if message.startswith('combat-ammunition:')]
    require(selected and all(slot in ('12', '13') and item == '99' for slot, item, _ in selected),
            'Live primary arrows selected from an ordinary slot')
    require('combat-avatar-check:2:1:0' in messages and 'combat-range-check:2:1:0' in messages,
            'Ordinary attack passes the avatar condition and distance gates')
    result = next(value for value in messages if value.startswith('normal-attack-result:1:1:'))
    sequence = ['combat-ammunition:12:99:7', 'combat-range-check:2:1:0',
                'tx:5:1:8', 'rx:5:7:25', result, 'rx:5:21:4']
    require(list(map(messages.index, sequence)) == sorted(map(messages.index, sequence)) and
            int(result.split(':')[-1]) > 0, 'Observed shot, authoritative hit and subsequent ammunition message')
    fatal = [row for row in rows if row['kind'] == 'exception' and not row.get('first_chance')]
    require(not fatal, 'The live result is consumed without an unhandled exception')
    for frame in live['monster_frames']:
        check(frame)
    return dict(
        ammunition=[dict(slot=int(slot), row=int(item), serial=int(serial)) for slot, item, serial in selected],
        range_checks=[value for value in messages if value.startswith('combat-range-check:')],
        attacks_sent=messages.count('tx:5:1:8'),
        attack_results=[value for value in messages if value.startswith('rx:5:7:')],
        resolved_attack_results=[value for value in messages if value.startswith('normal-attack-result:')],
        combat_replies=[value for value in messages if value.startswith('rx:5:')],
        unhandled_exceptions=fatal)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--reference-only', action='store_true')
    args = parser.parse_args()
    proof = verify_reference()
    if args.reference_only:
        print({key: proof[key] for key in ('full_functions', 'full_instructions', 'positive_cfg_blocks')})
        return
    link = read('normal-link')
    require(validate_normal_link(link) == 'PASS', 'Fresh verified normal build')
    observed = verify_live(link)
    result_log = DECODER / 'result.txt'
    require(result_log.read_text().startswith('PASS: 5/7'), 'Bounded native result decoder checks')
    names = ('normal-link', 'normal-preparation', 'normal-build', 'normal-consumers',
             'primary-ammunition-reference', 'own-entry', 'startup-audit', 'startup-taiwan-native',
             'live-launcher-native')
    sources = ('scripts/client455_armed_attack_port.py', 'scripts/native/client455_equipment_conditions.h',
               'scripts/native/client455_skill_force_items.cpp', 'scripts/native/client455_skill_force_items.h',
               'scripts/native/client455_initial_download.inc', 'scripts/native/client455_normal_attack_result.h',
               'scripts/native/client455_normal_attack_dispatch.inc',
               'scripts/native/client455_normal_attack_result_probe.cpp')
    save('primary-ammunition-checkpoint', dict(
        status='PARTIAL_LIVE_ORDINARY_ATTACK',
        scope='An ordinary attack on NeutralB selects equipped arrows, sends 5/1 and applies a live 5/7 result.',
        normal_executable=link['executable'], normal_link_sha256=sha(path('normal-link')),
        runtime_login_report=record(LIVE), observations=observed, script=record(Path(__file__)),
        first_attempt=record(PRIVATE / 'first-live.json'),
        decoder=dict(executable=record(DECODER / 'probe.exe'), result=record(result_log)),
        sources=[record(WS / name) for name in sources],
        fresh_evidence={name: record(path(name)) for name in names},
        M6='OPEN', M9='OPEN'))
    print(json.dumps(observed))


if __name__ == '__main__':
    main()
