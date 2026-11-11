"""Verify 455 monster health reception and application at Force impacts."""

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


PRIVATE = WS / 'artifacts/client455-progress/health194'
REFERENCE = PRIVATE / 'reference.json'
LIVE = PRIVATE / 'live.json'


def verify_reference():
    proof = verify_regions(REFERENCE)
    raw = json.loads(REFERENCE.read_text())
    require(raw['closed']['success'] and raw['closed']['saved'], 'Owned IDA session closed')
    dispatcher = raw['details']['0x58a6f0']['code']
    require('case 0x1B:' in dispatcher and 'sub_58BF70' in dispatcher
            and 'case 0x1D:' in dispatcher and 'sub_58C0C0' in dispatcher, 'Both 455 health input routes')
    calls = {0x58a7e0: 0x58bf70, 0x58a7f1: 0x58c0c0, 0x58c237: 0x43d480,
             0x58c02a: 0x52ed00, 0x52ed70: 0x43d480, 0x43d4c4: 0x43e3d0,
             0x43d4e1: 0x446ca0, 0x43d513: 0x446ca0, 0x43e3e7: 0x43b650}
    pointers = {0xaaa5ec: 0x404910, 0xaaa5f0: 0x404940, 0xad1898: 0x58a6f0}
    for pin in proof['references']:
        binary = (WS / pin['file']).read_bytes()
        for site, target in calls.items():
            require(read_va(binary, site, 5) == b'\xe8' + struct.pack('<i', target - site - 5),
                    'Confirmed health route at ' + hex(site))
        for site, target in pointers.items():
            require(read_va(binary, site, 4) == struct.pack('<I', target), 'Confirmed health/dispatcher slot')
        require(read_va(binary, 0xaa9be8, 8) == struct.pack('<d', 10000.0), 'Health packet scale')
        require(read_va(binary, 0xaa8c38, 4) == struct.pack('<f', -1.0), 'Pending fraction initializer')
    save('monster-health-reference', dict(
        **proof, raw=record(REFERENCE), scope='Monster displayed/pending health, 13/27 and 13/29, and Force impact.',
        calls={hex(site - 0x400000): hex(target - 0x400000) for site, target in calls.items()},
        displayed_fraction_offset=632, pending_fraction_offset=12, scale=10000,
        update=dict(opcode=29, minimum=8, actor_type=1, serial=2, fraction=6),
        target_info=dict(opcode=27, minimum=16, actor_type=2, serial=3, fraction=7),
        impact_rva='0x47900'))


def main():
    verify_reference()
    source = WS / 'scripts/native/client455_monster_force_result_probe.cpp'
    exe = build_full_object_probe('monster-health', source)
    files, _, clips = resource_inputs(exe.parent)
    dispatch, dispatch_console = run_fixture(exe, files, [], 'force-dispatch')
    damage, damage_console = run_fixture(exe, files, ['--damage'], 'force-damage')
    require(dispatch == dict(status='PASS', selected_routes=2, rejected_cases=3,
                             missing_row_retained=True, real_animations=2), 'Previous Force dispatch')
    require(damage == dict(status='PASS', target_rows=6, resolved_targets=5, largest_damage=70000,
                           verified_impact_frames=2), 'Previous Force damage accounting')
    native, console = run_fixture(exe, files, ['--health'], 'monster-health')
    require(native == dict(status='PASS', health_routes=[27, 29], initial_fraction=1, before_impact=0.8,
                           after_final_impact=0.5, after_recovery=0.95, verified_impact_frames=2,
                           short_update_rejected=True), 'Health routes and impact')

    link = read('normal-link')
    live = verify_live(link, LIVE)
    report = json.loads(LIVE.read_text())
    health_events = [line for line in report['protocol_observations']
                     if line.startswith('RF455 Protocol:monster-health:')]
    live['observed_health_events'] = len(health_events)
    live['applied_health_events'] = sum(line.endswith(':1') for line in health_events)
    names = ('normal-link', 'normal-preparation', 'normal-build', 'normal-consumers',
             'monster-health-reference', 'skill-force-items-reference', 'live-resource-inputs',
             'own-entry', 'startup-audit', 'startup-taiwan-native', 'live-launcher-native')
    fresh = {name: record(path(name)) for name in names}
    fresh['monster-health-live'] = record(LIVE)
    owners = ('?AnalysisServerPacket@CNetMsgProcessor_ItemArrangement@@', '?ReceiveHealth455@CMonster@@',
              '?ApplyHealthImpact455@CMonster@@', '?ProcessDamage@CCombatState@@')
    symbols = {name: hex(rva) for rva, name in own_symbols(link) if name.startswith(owners)}
    require(len(symbols) == len(owners), 'Both dispatcher and actual monster health owners linked')
    sources = ('scripts/client455_monster_health_port.py', 'scripts/native/client455_monster_health.inc',
               'scripts/native/client455_monster_health_dispatch.inc')
    save('monster-health-checkpoint', dict(
        status='PARTIAL_COMPONENT_MONSTER_HEALTH_FRACTION',
        scope='Ordinary 13/27 and 13/29 monster health and 5/9 Force impact application.',
        normal_executable=link['executable'], normal_link_sha256=sha(path('normal-link')), fresh_evidence=fresh,
        runtime_login_report=record(LIVE), live_smoke=live, script=record(Path(__file__)),
        sources=[record(WS / name) for name in sources] + [record(source)],
        probe_executable={**record(exe), 'architecture': pe(exe.read_bytes())['architecture']},
        console=console, real_clips=clips, native=native, own_symbols=symbols,
        regressions=dict(dispatch=dispatch, damage=damage, console=[dispatch_console, damage_console]),
        live_health_received=bool(live['observed_health_events']),
        live_health_applied=bool(live['applied_health_events']), M6='OPEN', M9='OPEN'))
    print(json.dumps(native))


if __name__ == '__main__':
    main()
