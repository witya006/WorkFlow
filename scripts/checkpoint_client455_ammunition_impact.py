"""Verify the 455 ammunition reply and its own-client combat observations."""

import argparse
import json
import re
import struct
from pathlib import Path

from build_client455_x87_math import read_va
from checkpoint_client455_party_window import path, read, save
from checkpoint_client455_rvp_effects import check, require, sha
from client455_normal_link_evidence import validate_normal_link
from client455_reference_regions import verify_regions
from client455_ui_checkpoint import record
from compare_client_binaries import WS
from rpk455 import Rpk


PRIVATE = WS / 'artifacts/client455-progress/ammo204'
REFERENCE = PRIVATE / 'reference.json'
LIVE = PRIVATE / 'live.json'
CALLS = {
    0x5a4642: 0x5a5910, 0x5a5937: 0x47bfe0, 0x5a593d: 0x420ec0,
    0x5a5959: 0x429c40, 0x5a596c: 0x4711f0, 0x4712c3: 0x6ae080,
    0x7e0580: 0x46c200, 0x7e068d: 0x46c200,
}


def verify_reference():
    proof = verify_regions(REFERENCE)
    evidence = json.loads(REFERENCE.read_text())
    require(evidence['closed']['success'] and evidence['closed']['saved'], 'Owned IDA session closed')
    for pin in proof['references']:
        binary = (WS / pin['file']).read_bytes()
        for site, target in CALLS.items():
            require(read_va(binary, site, 5) == b'\xe8' + struct.pack('<i', target - site - 5),
                    f'455 ammunition and effects call at {site:#x}')

    root = Path(json.loads((WS / 'config/paths.json').read_text())['client_455'])
    archive = root / 'Effect/EffectEntity6.rpk'
    magic = root / 'Effect/MagicSptList.spt'
    font = root / 'Effect/effectfont.dds'
    script = b'weapon\\i_act\\invk\\arw\\becor_bow_stnd_1.spt'
    entry = re.findall(rb'^0xefff0063\s+(\S+)', magic.read_bytes(), re.I | re.M)
    require(len(entry) == 1 and entry[0].lower().lstrip(b'\\') == script,
            'Stock effect key for arrow row 99')
    projectile = Rpk(archive.read_bytes()).read(script)
    require(b'entity_id' in projectile.lower(), 'Bow projectile RPK member')
    save('ammunition-impact-reference', dict(
        **proof, raw=record(REFERENCE), scope='455 ammunition state update and equipment owners in effects.',
        call_rvas={hex(site - 0x400000): hex(target - 0x400000) for site, target in CALLS.items()},
        ammunition_reply=dict(category=5, opcode=21, bytes=4, serial_offset=0, remaining_offset=2,
                              payload_value_offset=96, gauge_filter=16),
        equipment_effect_material_offset=208, projectile_key='0xefff0063',
        projectile_member=script.decode('ascii'),
        original_assets=[dict(file=p.as_posix(), sha256=sha(p)) for p in (archive, magic, font)]))
    return proof


def verify_live(link):
    live = json.loads(LIVE.read_text())
    require(live['normal_link_sha256'] == sha(path('normal-link')) and live['executable'] == link['executable'],
            'Exact own ammunition update build')
    check(dict(file=live['staged_executable'], sha256=link['executable']['sha256']))
    check(live['events'])
    rows = [json.loads(line) for line in (WS / live['events']['file']).read_text().splitlines()]
    require(live['debugger_exit'] == 0 and live['summary']['exit_observed'] and
            live['live_server']['private_handoff_removed'], 'Observed own exit and private handoff cleanup')
    require(not any(row['kind'] == 'exception' and not row.get('first_chance') for row in rows),
            'No unhandled exceptions in the combat observation')
    prefix = 'RF455 Protocol:'
    messages = [row['value'].removeprefix(prefix) for row in rows
                if row['kind'] == 'debug_string' and row['value'].startswith(prefix)]

    def events(name):
        return [tuple(map(int, value.split(':')[1:])) for value in messages if value.startswith(name + ':')]

    equipped = events('equipped-ammunition')
    amounts = events('combat-ammunition-left')
    sent = messages.count('tx:5:1:8')
    results = events('normal-attack-result')
    require(amounts and equipped and sent >= len(amounts), 'Own shots update the equipped owner')
    require(all(serial == amounts[0][0] and old == new + 1 for serial, old, new in amounts) and
            all(a[2] == b[1] for a, b in zip(amounts, amounts[1:])), 'One authoritative arrow per shot')
    require(len(results) >= len(amounts), 'Server results accompany ammunition updates')
    impacts = events('combat-impact')
    captures = events('combat-impact-frame')
    frames = live['combat_impact_frames']
    require(frames and len(captures) == len(frames), 'At least one real impact frame identified')
    for frame, (index, damage, status) in zip(frames, captures):
        check(frame)
        require(frame['file'].endswith(f'/world-impact-{index}.png') and status == 0 and
                any(impact[1] == damage for impact in impacts), 'Real post-impact framebuffer capture')
    first_capture = next(i for i, value in enumerate(messages) if value.startswith('combat-impact-frame:'))
    later_keys = sum(value.startswith('combat-key:') for value in messages[first_capture + 1:])
    monster_health_messages = sum(value.startswith(('rx:13:27:', 'rx:13:29:')) for value in messages)
    return dict(shots_sent=sent, ammunition=[dict(serial=s, before=a, after=b) for s, a, b in amounts],
                results=[dict(targets=t, resolved=r, first_damage=d) for t, r, d in results],
                impacts=[dict(target=s, damage=d, health_basis_points=h) for s, d, h in impacts],
                frames=frames, later_attack_keys=later_keys, monster_health_messages=monster_health_messages)


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
    names = ('normal-link', 'normal-preparation', 'normal-build', 'normal-consumers', 'own-entry',
             'startup-audit', 'startup-taiwan-native', 'live-launcher-native',
             'ammunition-impact-reference', 'live-resource-inputs')
    sources = ('scripts/client455_armed_attack_port.py', 'scripts/client455_initial_download_port.py',
               'scripts/prepare_client455_live_resources.py', 'scripts/probe_client455_device_startup.py',
               'scripts/native/client455_initial_download.inc', 'scripts/native/client455_item_payloads.h',
               'scripts/native/client455_item_payloads.cpp', 'scripts/native/client455_normal_attack_dispatch.inc',
               'scripts/native/client455_weapon_effect_owner.inc', 'scripts/native/client455_protocol_observation.h',
               'scripts/native/client455_camera_mouse_observation.inc',
               'scripts/native/client455_live_world_observation.inc', 'scripts/native/own_client_startup_debugger.cpp')
    save('ammunition-impact-checkpoint', dict(
        status='PARTIAL_LIVE_AMMUNITION_UPDATE',
        scope='Ordinary attacks apply server-authoritative equipped arrow counts on NeutralB.',
        normal_executable=link['executable'], normal_link_sha256=sha(path('normal-link')),
        runtime_login_report=record(LIVE), observations=observed, script=record(Path(__file__)),
        first_attempt=record(PRIVATE / 'first-live.json'), first_impact=record(PRIVATE / 'first-impact-live.json'),
        sources=[record(WS / name) for name in sources],
        fresh_evidence={name: record(path(name)) for name in names}, M6='OPEN', M9='OPEN'))
    print(json.dumps(observed))


if __name__ == '__main__':
    main()
