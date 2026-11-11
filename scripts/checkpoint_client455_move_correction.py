"""Verify the 455 movement correction and its native avatar consumer."""

import argparse
import json
import struct
from pathlib import Path

from build_client455_x87_math import read_va
from checkpoint_client455_monster_force_damage import run_fixture
from checkpoint_client455_party_window import path, read, save
from checkpoint_client455_rvp_effects import require, sha
from client455_normal_link_evidence import validate_normal_link
from client455_own_probe import build_full_object_probe
from client455_reference_regions import verify_regions
from client455_ui_checkpoint import record
from compare_client_binaries import WS


REFERENCE = WS / 'artifacts/client455-progress/move-correction210/reference.json'
CALLS = {0x5c1437: 0x5c2bf0, 0x5c2c08: 0x562b70, 0x5c2c18: 0x44a680, 0x5c2c57: 0x407380}
FLOAT_LOADS = {0x5c2c39: b'\xd9\x42\x01', 0x5c2c2f: b'\xd9\x41\x05', 0x5c2c25: b'\xd9\x40\x09'}


def verify_reference():
    proof = verify_regions(REFERENCE)
    raw = json.loads(REFERENCE.read_text())
    require(raw['closed']['success'] and raw['closed']['saved'], 'Owned IDA session closed')
    for pin in proof['references']:
        binary = (WS / pin['file']).read_bytes()
        for site, target in CALLS.items():
            require(read_va(binary, site, 5) == b'\xe8' + struct.pack('<i', target - site - 5),
                    f'455 movement call at {site:#x}')
        for site, code in FLOAT_LOADS.items():
            require(read_va(binary, site, len(code)) == code, f'455 unaligned coordinate read at {site:#x}')
        require(read_va(binary, 0x5c2c66, 3) == b'\x83\xf9\x0c' and
                read_va(binary, 0x5c2c71, 3) == b'\x83\xf9\x06', 'Original stop reasons')
    save('move-correction-reference', dict(
        **proof, raw=record(REFERENCE), group=4, opcode=3, payload_bytes=13,
        reason_offset=0, position_offsets=[1, 5, 9], stop_reasons=[6, 12], stop_profile=1,
        avatar_profile_offset=17796, pending_move_offsets=[435996, 436000],
        original_calls={hex(site - 0x400000): hex(target - 0x400000) for site, target in CALLS.items()}))
    return proof


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--reference-only', action='store_true')
    args = parser.parse_args()
    proof = verify_reference()
    if args.reference_only:
        print({key: proof[key] for key in ('full_functions', 'full_instructions', 'positive_cfg_blocks')})
        return
    link = read('normal-link')
    require(validate_normal_link(link) == 'PASS', 'Exact current client build')
    link_sha = sha(path('normal-link'))
    startup = read('startup-taiwan-native')
    require(startup['normal_link_sha256'] == link_sha and startup['debugger_exit'] == 0 and
            startup['summary']['after_sound_reached'] and startup['summary']['exit_observed'],
            'Current independent early Taiwan startup')
    source = WS / 'scripts/native/client455_move_correction_probe.cpp'
    exe = build_full_object_probe('move-correction', source)
    native, console = run_fixture(exe, [], [], 'move-correction')
    require(native == dict(status='PASS', position_bytes=13, invalid_cases=6, standing_updates=True,
                           moving_updates=True, previous_position_updated=True,
                           stop_profile=1, stop_reasons=[6, 12]), 'Movement correction native fixture')
    names = ('normal-link', 'normal-preparation', 'normal-build', 'normal-consumers',
             'own-entry', 'startup-audit', 'startup-taiwan-native', 'move-correction-reference')
    sources = ('client455_world_update_port.py', 'native/client455_world_position.inc',
               'native/client455_world_updates.h', 'native/client455_move_correction_probe.cpp')
    save('move-correction-checkpoint', dict(
        status='PARTIAL_COMPONENT_MOVE_CORRECTION',
        scope='Ordinary 455 world dispatcher applies a correction to standing or moving avatar coordinates.',
        normal_executable=link['executable'], normal_link_sha256=link_sha,
        component=native, component_executable=record(exe), component_console=console,
        script=record(Path(__file__)), sources=[record(WS / 'scripts' / name) for name in sources],
        fresh_evidence={name: record(path(name)) for name in names},
        gaps=['The 455 pending-move state belongs to the 26-byte outgoing move route and remains open.',
              'The live nonzero profile producers and an observed 4/3 are open.',
              'Malformed and nonfinite coordinates are rejected before state mutation.'],
        own_live_run=False, M6='OPEN', M9='OPEN'))
    print(json.dumps(dict(executable=link['executable']['sha256'], component=native)))


if __name__ == '__main__':
    main()
