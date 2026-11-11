"""Verify the 455 monster critical reaction using the ordinary client objects."""

import json
import struct
from pathlib import Path

from build_client455_x87_math import read_va
from checkpoint_client455_force_damage_render import stage_force_inputs
from checkpoint_client455_monster_force import resource_inputs
from checkpoint_client455_monster_force_damage import run_fixture
from checkpoint_client455_monster_force_result import verify_live
from checkpoint_client455_party_window import path, read, save
from checkpoint_client455_rvp_effects import require, sha
from client455_own_probe import build_full_object_probe
from client455_reference_regions import verify_regions
from client455_ui_checkpoint import own_symbols, record
from compare_client_binaries import WS


PRIVATE = WS / 'artifacts/client455-progress/critical199'
REFERENCE = PRIVATE / 'reference.json'
LIVE = PRIVATE / 'live.json'


def verify_reference():
    proof = verify_regions(REFERENCE)
    raw = json.loads(REFERENCE.read_text())
    require(raw['closed']['success'] and raw['closed']['saved'], 'Owned IDA session closed')
    calls = {0x447b2f: 0x447ca0, 0x447b40: 0x43db60, 0x7f0e8b: 0x7ec6e0, 0x7ec701: 0x7d2c20,
             0x7d2c3c: 0x451270, 0x7d2c4b: 0x7dca10, 0x7d2c5c: 0x7cdfc0, 0x7d2c7a: 0x7d2ca0,
             0x7d2c86: 0x7d2cd0, 0x7d2c94: 0x7d2d20, 0x450001: 0x43e400}
    pointers = {0xaaa5bc: 0x458240, 0xaaa654: 0x45a1e0, 0xaa8d64: 0x44ffe0, 0xaa8eec: 0x44ffe0}
    for pin in proof['references']:
        binary = (WS / pin['file']).read_bytes()
        for site, target in calls.items():
            require(read_va(binary, site, 5) == b'\xe8' + struct.pack('<i', target - site - 5),
                    'Confirmed critical call at ' + hex(site))
        for site, target in pointers.items():
            require(read_va(binary, site, 4) == struct.pack('<I', target),
                    'Confirmed critical vtable slot at ' + hex(site))
    bodies = {addr: result['code'] for addr, result in raw['details'].items()}
    require('sub_406290(5) || sub_43DA10(3)' in bodies['0x43db60']
            and '1610612737' in bodies['0x447b20'] and '1610612740' in bodies['0x447b20'],
            'Critical guard and action followed by Force effect')
    require('case 0x60000001u:' in bodies['0x45a1e0'] and '+ 14' in bodies['0x45a1e0'],
            'Critical animation depends on combat mode')
    shock = bodies['0x7d2c20']
    require('0.27000001' in shock and '0.300000011920929' in shock and 'sub_7D2D20(1.0)' in shock,
            'Reference shock constants')
    save('monster-critical-reference', dict(
        **proof, raw=record(REFERENCE), scope='Critical hit action, effect queue, monster animation and shock.',
        calls={hex(site - 0x400000): hex(target - 0x400000) for site, target in calls.items()},
        critical_action='0x60000001', control_mask=3, animation_types=[14, 15], damage_anchor_slot=8,
        shake_seconds=0.27, light_height_multiplier=0.3, light_density=1))


def verify_component():
    source = WS / 'scripts/native/client455_monster_force_result_probe.cpp'
    exe = build_full_object_probe('monster-critical', source)
    files, _, clips = resource_inputs(exe.parent, animation_keys=(0x10c0, 0x10d0, 0x10e0, 0x10f0))
    critical_args = ['--critical', str(files[4]), str(files[5])]
    native, console = run_fixture(exe, files[:4], critical_args, 'monster-critical')
    require(native == dict(status='PASS', clips=[4320, 4336], critical_before_force=True,
                           control_flag_suppresses_critical=True, shake_seconds=0.27, light_radius=12,
                           light_density=1, light_position=[2, 38.8, 8]), 'Monster critical reaction')
    inputs, _ = stage_force_inputs(exe.parent)
    regression = {}
    for mode, checkpoint in [('damage-render', 'force-damage-render-checkpoint'),
                             ('block-render', 'combat-result-effect-checkpoint')]:
        result, log = run_fixture(exe, files[:4], ['--' + mode], mode)
        require(result == read(checkpoint)['native'], 'Prior render result for ' + mode)
        regression[mode] = dict(native=result, console=log)
    return dict(native=native, console=console, real_clips=clips, source=record(source),
                probe_executable=record(exe), render_inputs=inputs, regression=regression)


def main():
    verify_reference()
    component = verify_component()
    link = read('normal-link')
    live = verify_live(link, LIVE)
    names = ('normal-link', 'normal-preparation', 'normal-build', 'normal-consumers',
             'monster-critical-reference', 'skill-force-items-reference', 'live-resource-inputs',
             'own-entry', 'startup-audit', 'startup-taiwan-native', 'live-launcher-native')
    fresh = {name: record(path(name)) for name in names}
    fresh['monster-critical-live'] = record(LIVE)
    owners = ('?ExtractEffectInfo@CAllEffectInfo@@', '?ProcessDamage@CCombatState@@',
              '?CMonsterSpecialEffectDamageAction@@', '?SetAction@CBaseNpc@@')
    symbols = {name: hex(rva) for rva, name in own_symbols(link) if name.startswith(owners)}
    require(len(symbols) == len(owners), 'Critical reaction owners linked in the ordinary client')
    save('monster-critical-checkpoint', dict(
        **component, status='PARTIAL_COMPONENT_MONSTER_CRITICAL',
        scope='Force critical reaction on the monster target with actual 455 Wing clips and shock.',
        normal_executable=link['executable'], normal_link_sha256=sha(path('normal-link')), fresh_evidence=fresh,
        runtime_login_report=record(LIVE), live_smoke=live, script=record(Path(__file__)),
        port_source=record(WS / 'scripts/client455_monster_critical_port.py'), own_symbols=symbols,
        M6='OPEN', M9='OPEN'))
    print(json.dumps(component['native']))


if __name__ == '__main__':
    main()
