"""Verify the positive-damage Force effect queued by the client impact consumer."""

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


PRIVATE = WS / 'artifacts/client455-progress/impact196'
REFERENCE = PRIVATE / 'reference.json'
LIVE = PRIVATE / 'live.json'


def verify_reference():
    proof = verify_regions(REFERENCE)
    raw = json.loads(REFERENCE.read_text())
    require(raw['closed']['success'] and raw['closed']['saved'], 'Owned IDA session closed')
    calls = {0x447bf2: 0x447770, 0x43c703: 0x408aa0, 0x43c77d: 0x458040, 0x458070: 0x458160,
             0x4581dd: 0x463780, 0x4054f8: 0x405510, 0x43c78b: 0x43c840, 0x43c7a5: 0x43c800,
             0x43c7b6: 0x43c7d0, 0x43c7e8: 0x405510, 0x7f1173: 0x7ef770,
             0x7f0efd: 0x7ec840, 0x7ec8ae: 0x7e6ed0}
    for pin in proof['references']:
        binary = (WS / pin['file']).read_bytes()
        for site, target in calls.items():
            require(read_va(binary, site, 5) == b'\xe8' + struct.pack('<i', target - site - 5),
                    'Confirmed Force effect call at ' + hex(site))
        require(read_va(binary, 0xaa9414, 4) == struct.pack('<I', 0x4054e0), 'Force data code vtable slot')
        require(read_va(binary, 0x447c47, 5) == bytes.fromhex('6804000060'), '455 Force effect action')
        require(read_va(binary, 0x43c7ed, 6) == bytes.fromhex('8a800c040000'), 'Force effect range field')
    save('monster-force-impact-reference', dict(
        **proof, raw=record(REFERENCE), scope='Positive Force impact effect command and queue payload.',
        calls={hex(site - 0x400000): hex(target - 0x400000) for site, target in calls.items()},
        effect_action='0x60000004', effect_type=7, code_offset=4, range_offset=1036,
        amount_offset=44, extra_offset=48, effective_level_offset=13,
        renderer_dispatch_rva='0x3f0b70', renderer_force_damage_rva='0x3ef770',
        neighboring_block_renderer_rva='0x3ec840'))


def verify_component():
    source = WS / 'scripts/native/client455_monster_force_result_probe.cpp'
    exe = build_full_object_probe('monster-force-impact', source)
    files, _, clips = resource_inputs(exe.parent)
    impact, console = run_fixture(exe, files, ['--impact-effect'], 'force-impact')
    require(impact == dict(status='PASS', effect_id='0x92000e', range=0, checked_impacts=2,
                           total_damage=70000, second_range=1), 'Positive Force effect payload')
    health, health_console = run_fixture(exe, files, ['--health'], 'monster-health')
    reaction, reaction_console = run_fixture(exe, files, ['--reaction'], 'force-reaction')
    require(health == read('monster-health-checkpoint')['native'] and
            reaction == read('monster-force-reaction-checkpoint')['native'], 'Previous HP and reaction checks')
    return source, dict(native=impact, console=console, real_clips=clips,
                        regressions=dict(health=health, reaction=reaction, consoles=[health_console, reaction_console]),
                        probe_executable={**record(exe), 'architecture': pe(exe.read_bytes())['architecture']})


def main():
    verify_reference()
    source, component = verify_component()
    link = read('normal-link')
    live = verify_live(link, LIVE)
    names = ('normal-link', 'normal-preparation', 'normal-build', 'normal-consumers', 'monster-force-impact-reference',
             'skill-force-items-reference', 'live-resource-inputs', 'own-entry', 'startup-audit',
             'startup-taiwan-native', 'live-launcher-native')
    fresh = {name: record(path(name)) for name in names}
    fresh['monster-force-impact-live'] = record(LIVE)
    owners = ('?ProcessDamage@CCombatState@@', '?SetEffectInfo@CCharacter@@',
              '?GetDTCode@CSFItem@@', '?GetRangeTypeForEffect@CSFItem@@')
    symbols = {name: hex(rva) for rva, name in own_symbols(link) if name.startswith(owners)}
    require(len(symbols) == len(owners), 'Normal impact, effect queue and Force row accessors linked')
    sources = ('scripts/client455_monster_force_port.py', 'scripts/client455_monster_health_port.py',
               'scripts/native/client455_monster_force_result.inc')
    save('monster-force-impact-checkpoint', dict(
        **component, status='PARTIAL_COMPONENT_MONSTER_FORCE_IMPACT',
        scope='Positive 5/9 Force queues effect key, amount and range on the normal impact path.',
        normal_executable=link['executable'], normal_link_sha256=sha(path('normal-link')), fresh_evidence=fresh,
        runtime_login_report=record(LIVE), live_smoke=live, script=record(Path(__file__)),
        sources=[record(WS / name) for name in sources] + [record(source)], own_symbols=symbols,
        live_force_received=bool(live['observed_force_events']), M6='OPEN', M9='OPEN'))
    print(json.dumps(component['native']))


if __name__ == '__main__':
    main()
