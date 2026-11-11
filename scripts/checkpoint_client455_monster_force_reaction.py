"""Verify zero-damage 455 Force reactions through the normal effect queue."""

import json
import struct
from pathlib import Path

from build_client455_x87_math import read_va
from checkpoint_client455_monster_force import resource_inputs
from checkpoint_client455_monster_force_damage import run_fixture
from checkpoint_client455_monster_force_result import verify_live
from checkpoint_client455_party_window import path, read, save
from checkpoint_client455_rvp_effects import require, sha
from client455_own_probe import build_full_object_probe
from client455_reference_regions import verify_regions
from client455_ui_checkpoint import own_symbols, record
from compare_client_binaries import WS, pe


PRIVATE = WS / 'artifacts/client455-progress/hit195'
REFERENCE = PRIVATE / 'reference.json'
LIVE = PRIVATE / 'live.json'


def verify_reference():
    proof = verify_regions(REFERENCE)
    raw = json.loads(REFERENCE.read_text())
    require(raw['closed']['success'] and raw['closed']['saved'], 'Owned IDA session closed')
    calls = {0x5a3d1f: 0x5a3f30, 0x5a3d2b: 0x5a3f30, 0x447308: 0x4473d0,
             0x447334: 0x4473b0, 0x457bf6: 0x457f00, 0x457f54: 0x457fe0}
    slots = {0xaaa590: 0x457b50, 0xaaa5a4: 0x43ca70, 0xaaa660: 0x45a040}
    for pin in proof['references']:
        binary = (WS / pin['file']).read_bytes()
        for site, target in calls.items():
            require(read_va(binary, site, 5) == b'\xe8' + struct.pack('<i', target - site - 5),
                    'Confirmed effect call at ' + hex(site))
        for site, target in slots.items():
            require(read_va(binary, site, 4) == struct.pack('<I', target), 'Confirmed monster effect slot')
        require(read_va(binary, 0x447314, 5) == bytes.fromhex('6806000060') and
                read_va(binary, 0x44733d, 5) == bytes.fromhex('6805000060'), 'Distinct action constants')
    effect_types = raw['details']['0x45a040']['code']
    require('case 0x60000006u:' in effect_types and 'return 13;' in effect_types and
            'case 0x60000005u:' in effect_types and 'return 4;' in effect_types, 'Monster effect types')
    save('monster-force-reaction-reference', dict(
        **proof, raw=record(REFERENCE),
        scope='5/9 special-result flag and zero-damage Force reaction keys for a monster.',
        calls={hex(site - 0x400000): hex(target - 0x400000) for site, target in calls.items()},
        special=dict(damage_sentinel=-2, flag_offset=365, action='0x60000006', effect_type=13),
        ordinary_miss=dict(action='0x60000005', effect_type=4), effect_key_rva='0x57fe0'))


def verify_component():
    source = WS / 'scripts/native/client455_monster_force_result_probe.cpp'
    exe = build_full_object_probe('monster-force-reaction', source)
    files, _, clips = resource_inputs(exe.parent)
    reaction, console = run_fixture(exe, files, ['--reaction'], 'force-reaction')
    require(reaction == dict(status='PASS', reaction_types=[13, 4], checked_impacts=2,
                             numeric_damage=0, duplicated_reaction=False), 'Ordinary reaction queue')
    regression, regression_console = run_fixture(exe, files, ['--health'], 'monster-health')
    require(regression == read('monster-health-checkpoint')['native'], 'Health and positive damage regression')
    return source, dict(native=reaction, console=console, real_clips=clips,
                        regressions=dict(health=regression, console=regression_console),
                        probe_executable={**record(exe), 'architecture': pe(exe.read_bytes())['architecture']})


def main():
    verify_reference()
    source, component = verify_component()
    link = read('normal-link')
    live = verify_live(link, LIVE)
    names = ('normal-link', 'normal-preparation', 'normal-build', 'normal-consumers', 'monster-force-reaction-reference',
             'skill-force-items-reference', 'live-resource-inputs', 'own-entry', 'startup-audit',
             'startup-taiwan-native', 'live-launcher-native')
    fresh = {name: record(path(name)) for name in names}
    fresh['monster-force-reaction-live'] = record(LIVE)
    owners = ('?ProcessDamage@CCombatState@@', '?SetForceDamage455@CAttackerInfo@@',
              '?GetEffectTypeID@CMonster@@', '?SetEffectInfo@CBaseNpc@@')
    symbols = {name: hex(rva) for rva, name in own_symbols(link) if name.startswith(owners)}
    require(len(symbols) == len(owners), 'Normal impact and effect owners linked')
    sources = ('scripts/client455_monster_force_port.py', 'scripts/client455_monster_health_port.py',
               'scripts/native/client455_monster_force_damage.inc')
    save('monster-force-reaction-checkpoint', dict(
        **component, status='PARTIAL_COMPONENT_MONSTER_FORCE_REACTION',
        scope='Zero-damage 5/9 reaction queued on a monster impact. No rendered effect equivalence claim.',
        normal_executable=link['executable'], normal_link_sha256=sha(path('normal-link')), fresh_evidence=fresh,
        runtime_login_report=record(LIVE), live_smoke=live, script=record(Path(__file__)),
        sources=[record(WS / name) for name in sources] + [record(source)], own_symbols=symbols,
        live_force_received=bool(live['observed_force_events']), M6='OPEN', M9='OPEN'))
    print(json.dumps(component['native']))


if __name__ == '__main__':
    main()
