"""Verify the recovered equipment and inventory owners in the ordinary client."""

import argparse
import json
import struct
from pathlib import Path

from build_client455_x87_math import read_va
from checkpoint_client455_party_window import path, read, save
from checkpoint_client455_rvp_effects import check, require, sha
from client455_reference_regions import verify_regions
from client455_ui_checkpoint import record
from compare_client_binaries import WS


PRIVATE = WS / 'artifacts/client455-progress/download202'
REFERENCE = PRIVATE / 'reference.json'
LIVE = PRIVATE / 'live.json'
ITEM_MAP = bytes((1, 2, 3, 4, 5, 7, 6, 8, 9, 10, 11, 12, 14, 13, 0, 18, 15, 16, 17,
                  19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 46))


def verify_reference():
    proof = verify_regions(REFERENCE)
    raw = json.loads(REFERENCE.read_text())
    require(raw['closed']['success'] and raw['closed']['saved'], 'Owned IDA session closed')
    factory_calls = (0x56c0bd, 0x56c3aa, 0x56d1ec)
    for pin in proof['references']:
        binary = (WS / pin['file']).read_bytes()
        require(read_va(binary, 0xab3770, len(ITEM_MAP)) == ITEM_MAP, '455 wire item IDs')
        require(read_va(binary, 0xab37d4, 7) == bytes((10, 11, 8, 9, 12, 13, 14)),
                '455 accessory destination slots')
        for site in factory_calls:
            require(read_va(binary, site, 5) == b'\xe8' + struct.pack('<i', 0x4697b0 - site - 5),
                    f'Initial download calls the 455 factory at {site:#x}')
    save('downloaded-items-reference', dict(
        **proof, raw=record(REFERENCE), scope='455 normal item factory and initial item state setters.',
        item_map_rva='0x6b3770', item_map=list(ITEM_MAP), accessory_slots_rva='0x6b37d4',
        factory_call_rvas=[hex(site - 0x400000) for site in factory_calls],
        quantity_offset=92, durability_offset=96, animus_progress_offsets=[104, 108],
        modifier_offsets=[184, 188], timer_offsets=[21, 22, 88]))
    return proof


def verify_live(link):
    live = json.loads(LIVE.read_text())
    require(live['normal_link_sha256'] == sha(path('normal-link')) and live['executable'] == link['executable'],
            'Exact own initial item build')
    check(dict(file=live['staged_executable'], sha256=link['executable']['sha256']))
    check(live['events'])
    require(live['debugger_exit'] == 0 and live['summary']['exit_observed'] and
            live['live_server']['private_handoff_removed'], 'Observed exit and private handoff cleanup')
    rows = [json.loads(line) for line in (WS / live['events']['file']).read_text().splitlines()]
    require(not any(row['kind'] == 'exception' and not row.get('first_chance') for row in rows),
            'No unhandled exception in the own client')
    prefix = 'RF455 Protocol:'
    messages = [row['value'].removeprefix(prefix) for row in rows
                if row['kind'] == 'debug_string' and row['value'].startswith(prefix)]

    def event(name):
        return next(value for value in messages if value.startswith(name + ':'))

    base = event('base-applied')
    inventory = event('inventory-applied')
    _, _, created, equipped = base.split(':')
    _, bags, received, placed = inventory.split(':')
    require(int(created) == int(equipped) == 8 and int(placed) == int(received) == 21,
            'Eight live equipment slots and all 21 inventory rows')
    require('equipped-ammunition:99:315:0' in messages, 'Equipped ammunition from the base reply')
    sequence = ['rx:3:4:431', base, 'tx:3:5:0', 'rx:3:6:633', inventory, 'tx:3:9:0', event('position-mode')]
    require(list(map(messages.index, sequence)) == sorted(map(messages.index, sequence)),
            'Both ordinary handlers run before entry into the world')
    require('world-frame:0:0:0' in messages and 'combat-avatar-check:1:1:0' in messages,
            'First world frame and subsequent ordinary attack precheck')
    for frame in live['monster_frames']:
        check(frame)
    return dict(equipment_created=int(created), equipment_placed=int(equipped), bags=int(bags),
                inventory_rows=int(received), inventory_placed=int(placed),
                equipped_ammunition=[m for m in messages if m.startswith('equipped-ammunition:')],
                inventory_ammunition=[m for m in messages if m.startswith('inventory-ammunition:')],
                attacks_sent=messages.count('tx:5:1:8'),
                attack_results=sum(m.startswith('rx:5:7:') for m in messages))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--reference-only', action='store_true')
    args = parser.parse_args()
    proof = verify_reference()
    if args.reference_only:
        print({key: proof[key] for key in ('full_functions', 'full_instructions', 'positive_cfg_blocks')})
        return
    link = read('normal-link')
    observed = verify_live(link)
    ammunition = PRIVATE / 'primary-ammunition.json'
    ammunition_session = json.loads(ammunition.read_text())['closed']
    require(ammunition_session['success'] and ammunition_session['saved'], 'Primary ammunition IDA session closed')
    names = ('normal-link', 'normal-preparation', 'normal-build', 'normal-consumers',
             'downloaded-items-reference', 'own-entry', 'startup-audit', 'startup-taiwan-native',
             'live-launcher-native')
    sources = ('scripts/client455_initial_download_port.py', 'scripts/native/client455_initial_download.inc',
               'scripts/native/client455_download_board_add.inc', 'scripts/native/client455_item_payloads.h',
               'scripts/native/client455_item_payloads.cpp')
    save('downloaded-items-checkpoint', dict(
        status='PARTIAL_LIVE_INITIAL_ITEM_OWNERS',
        scope='The normal client applies equipment and inventory rows before entering NeutralB.',
        normal_executable=link['executable'], normal_link_sha256=sha(path('normal-link')),
        runtime_login_report=record(LIVE), observations=observed, script=record(Path(__file__)),
        first_attempt=record(PRIVATE / 'first-live.json'),
        primary_ammunition_static=dict(**record(ammunition), architecture='x86',
                                       validator_rva='0x16770', match_rva='0x60e70', auxiliary_rva='0x70e10'),
        sources=[record(WS / name) for name in sources],
        fresh_evidence={name: record(path(name)) for name in names},
        M6='OPEN', M9='OPEN'))
    print(json.dumps(observed))


if __name__ == '__main__':
    main()
