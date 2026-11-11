"""Verify 455 multi-target Force damage on the ordinary combat owners."""

import json
import struct
import subprocess
from pathlib import Path

from build_client455_x87_math import read_va
from checkpoint_client455_monster_force import resource_inputs
from checkpoint_client455_monster_force_result import verify_live
from checkpoint_client455_party_window import path, read, save
from checkpoint_client455_rvp_effects import require, sha
from client455_own_probe import build_full_object_probe
from client455_reference_regions import verify_regions
from client455_ui_checkpoint import own_symbols, record
from compare_client_binaries import WS, pe


PRIVATE = WS / 'artifacts/client455-progress/victims193'
REFERENCE = PRIVATE / 'reference.json'
LIVE = PRIVATE / 'live.json'


def verify_reference():
    proof = verify_regions(REFERENCE)
    raw = json.loads(REFERENCE.read_text())
    require(raw['closed']['success'] and raw['closed']['saved'], 'Owned IDA session closed')
    calls = {0x5a3a1f: 0x43e240, 0x5a3ce1: 0x43e210, 0x5a3d1f: 0x5a3f30, 0x5a3d4c: 0x447a90,
             0x5a3d5d: 0x447ac0, 0x4472c7: 0x447790, 0x4472d3: 0x447900, 0x4472df: 0x447a20}
    for pin in proof['references']:
        binary = (WS / pin['file']).read_bytes()
        for site, target in calls.items():
            require(read_va(binary, site, 5) == b'\xe8' + struct.pack('<i', target - site - 5),
                    'Confirmed combat call at ' + hex(site))
        require(read_va(binary, 0xaaa5c4, 4) == struct.pack('<I', 0x45a7e0), 'Monster attack distance slot')
        require(read_va(binary, 0xaaa3a0, 8) == struct.pack('<d', 0.10000000149011612), 'Impact jitter constant')
    save('monster-force-damage-reference', dict(
        **proof, raw=record(REFERENCE), scope='5/9 target queues, signed damage cases, and impact accounting.',
        calls={hex(site - 0x400000): hex(target - 0x400000) for site, target in calls.items()},
        target_damage_offset=5, critical_offset=12, attack_point_rva='0x1a3a70',
        damage_total_offset=352, pending_damage_offset=360, special_result_offset=365,
        impact_number_rva='0x47790', health_fraction_rva='0x47900',
        pending_damage_rva='0x47a20', monster_force_distance=1))


def run_fixture(exe, files, options, name):
    result = subprocess.run([str(exe), *(str(file) for file in files), *options], cwd=exe.parent,
                            capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW, timeout=30)
    console = exe.parent / (name + '.txt')
    console.write_bytes(result.stdout + result.stderr)
    require(result.returncode == 0, f'{name} component check (exit {result.returncode}): '
            + result.stderr.decode(errors='replace'))
    return json.loads(result.stdout), record(console)


def main():
    verify_reference()
    source = WS / 'scripts/native/client455_monster_force_result_probe.cpp'
    exe = build_full_object_probe('monster-force-damage', source)
    files, _, clips = resource_inputs(exe.parent)
    previous, previous_console = run_fixture(exe, files, [], 'force-dispatch')
    native, native_console = run_fixture(exe, files, ['--damage'], 'force-damage')
    require(previous == dict(status='PASS', selected_routes=2, rejected_cases=3,
                             missing_row_retained=True, real_animations=2), 'Previous Force route')
    require(native == dict(status='PASS', target_rows=6, resolved_targets=5, largest_damage=70000,
                           verified_impact_frames=2), 'Multi-target impact result')

    link = read('normal-link')
    live = verify_live(link, LIVE)
    names = ('normal-link', 'normal-preparation', 'normal-build', 'normal-consumers',
             'monster-force-damage-reference', 'skill-force-items-reference', 'live-resource-inputs',
             'own-entry', 'startup-audit', 'startup-taiwan-native', 'live-launcher-native')
    fresh = {name: record(path(name)) for name in names}
    fresh['monster-force-damage-live'] = record(LIVE)
    symbols = {name: hex(rva) for rva, name in own_symbols(link)
               if name.startswith(('?MonsterForceResult455@CNetMsgProcessor_Combat@@',
                                   '?SetForceDamage455@CAttackerInfo@@', '?ProcessDamage@CCombatState@@'))}
    require(len(symbols) == 3, 'Normal dispatcher and impact owners linked')
    sources = ('scripts/client455_monster_force_port.py', 'scripts/native/client455_monster_force_result.h',
               'scripts/native/client455_monster_force_dispatch.inc', 'scripts/native/client455_monster_force_damage.inc',
               'scripts/native/client455_skill_force_items.cpp', 'scripts/checkpoint_client455_monster_force_result.py')
    save('monster-force-damage-checkpoint', dict(
        status='PARTIAL_COMPONENT_MONSTER_FORCE_DAMAGE',
        scope='Ordinary 5/9 victim queues and numeric Force damage on impact.',
        normal_executable=link['executable'], normal_link_sha256=sha(path('normal-link')), fresh_evidence=fresh,
        runtime_login_report=record(LIVE), live_smoke=live, script=record(Path(__file__)),
        sources=[record(WS / name) for name in sources] + [record(source)],
        probe_executable={**record(exe), 'architecture': pe(exe.read_bytes())['architecture']},
        consoles=[previous_console, native_console], real_clips=clips, previous_dispatch=previous,
        native=native, own_symbols=symbols, live_force_activation=bool(live['observed_force_events']),
        health_fraction_restored=False, force_effects_restored=False, M6='OPEN', M9='OPEN'))
    print(json.dumps(native))


if __name__ == '__main__':
    main()
