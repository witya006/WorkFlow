"""Verify the authoritative 455 player HP route and its actual HUD consumer."""

import argparse
import json
import struct
from pathlib import Path

from build_client455_x87_math import read_va
from checkpoint_client455_creature_attacks import live_combat
from checkpoint_client455_party_window import path, read, save
from checkpoint_client455_rvp_effects import check, require, sha
from client455_normal_link_evidence import validate_normal_link
from client455_reference_regions import verify_regions
from client455_ui_checkpoint import record
from compare_client_binaries import WS


PRIVATE = WS / 'artifacts/client455-progress/avatar-health208'
REFERENCE = PRIVATE / 'reference.json'
LIVE = PRIVATE / 'live.json'
CALLS = {0x5a6046: 0x5a7370, 0x5a738e: 0x41b540, 0x41b5ac: 0x41b610,
         0x41b5b5: 0x41b500, 0x41b5c3: 0x66a6c0, 0x4472d3: 0x447900,
         0x447913: 0x407330}


def verify_reference():
    proof = verify_regions(REFERENCE)
    raw = json.loads(REFERENCE.read_text())
    require(raw['closed']['success'] and raw['closed']['saved'], 'Owned IDA session closed')
    for pin in proof['references']:
        binary = (WS / pin['file']).read_bytes()
        for site, target in CALLS.items():
            require(read_va(binary, site, 5) == b'\xe8' + struct.pack('<i', target - site - 5),
                    f'455 player HP call at {site:#x}')
        require(read_va(binary, 0x44790c, 2) == b'\x6a\x0f', 'Frame health omits the local avatar type')
    save('avatar-health-reference', dict(
        **proof, raw=record(REFERENCE), group=11, opcode=14, payload_bytes=4, hp_offset=0,
        avatar_current_hp_offset=24048, avatar_max_hp_offset=24044,
        call_rvas={hex(site - 0x400000): hex(target - 0x400000) for site, target in CALLS.items()},
        local_avatar_type=15, mounted_display_uses_unit=True, impact_applies_avatar_hp=False))
    return proof


def verify_hud(report_file, link_sha):
    report = json.loads(report_file.read_text())
    expected = dict(hp=[160000, 90000, 70000, 0], impact_damage=70000, hp_after_impact=160000,
                    invalid_lengths=2, mounted_player_hp_retained=True)
    require(report['normal_link_sha256'] == link_sha and report['natural_exit'] == 0 and
            report['native']['avatar_health'] == expected, 'Exact client objects apply the authoritative HP')
    for row in [report['exe'], report['output'], *report['sources'], *report['inputs']]:
        check(row)
    frame = next(frame for frame in report['frames'] if frame['file'].endswith('/hud-avatar-health.bgra'))
    check(frame)
    check(frame['preview'])
    return dict(**expected, frame=frame['preview'], report=record(report_file))


def main():
    parser = argparse.ArgumentParser()
    stage = parser.add_mutually_exclusive_group(required=True)
    stage.add_argument('--reference-only', action='store_true')
    stage.add_argument('--hud-report', type=Path)
    args = parser.parse_args()
    proof = verify_reference()
    if args.reference_only:
        print({key: proof[key] for key in ('full_functions', 'full_instructions', 'positive_cfg_blocks')})
        return
    link = read('normal-link')
    link_sha = sha(path('normal-link'))
    require(validate_normal_link(link) == 'PASS', 'Exact current client build')
    hud = verify_hud(args.hud_report.resolve(), link_sha)
    live = live_combat(link, LIVE)
    require(live['ordinary']['ordinary_attack_verified'], 'Ordinary outgoing combat regression')
    report = json.loads(LIVE.read_text())
    debug = [json.loads(line) for line in (WS / report['events']['file']).read_text().splitlines()]
    prefix = 'RF455 Protocol:avatar-health:'
    updates = [list(map(int, row['value'][len(prefix):].split(':'))) for row in debug
               if row['kind'] == 'debug_string' and row['value'].startswith(prefix)]
    names = ('normal-link', 'normal-preparation', 'normal-build', 'normal-consumers', 'own-entry',
             'startup-audit', 'startup-taiwan-native', 'live-launcher-native', 'avatar-health-reference')
    sources = ('client455_avatar_health_port.py', 'prepare_client455_normal.py',
               'probe_client455_hud.py', 'native/client455_hud_probe.cpp')
    save('avatar-health-checkpoint', dict(
        status='PARTIAL_LIVE_AVATAR_HEALTH' if updates else 'PARTIAL_COMPONENT_AVATAR_HEALTH',
        scope='Authoritative current player HP, mounted display owner and normal combat regression.',
        normal_executable=link['executable'], normal_link_sha256=link_sha,
        runtime_login_report=record(LIVE), live=live, live_avatar_health_updates=updates, hud=hud,
        script=record(Path(__file__)), sources=[record(WS / 'scripts' / name) for name in sources],
        fresh_evidence={name: record(path(name)) for name in names}, M6='OPEN', M9='OPEN'))
    print(json.dumps(dict(hud=hud, ordinary=live['ordinary'], live_avatar_health_updates=updates)))


if __name__ == '__main__':
    main()
