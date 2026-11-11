"""Verify the 455 combat route and run its ordinary handler with real clips."""

import json
import math
import struct
import subprocess
from pathlib import Path

from audit_client455_tutorial_integration import rtti, vptr_store
from build_client455_x87_math import read_va
from checkpoint_client455_monster_force import resource_inputs
from checkpoint_client455_party_window import path, read, save
from checkpoint_client455_rvp_effects import check, require, sha
from checkpoint_client455_world_observation import sample_values
from client455_own_probe import build_full_object_probe
from client455_reference_regions import verify_regions
from client455_ui_checkpoint import own_symbols, record
from compare_client_binaries import WS, pe


PRIVATE = WS / 'artifacts/client455-progress/combat192'
REFERENCE = PRIVATE / 'reference.json'
LIVE = PRIVATE / 'live.json'


def verify_reference():
    proof = verify_regions(REFERENCE)
    raw = json.loads(REFERENCE.read_text())
    require(raw['closed']['success'] and raw['closed']['saved'], 'Owned IDA session closed')
    calls = {0x561115: 0x5a4430, 0x5a4579: 0x5a4eb0, 0x5a4f7e: 0x5a34c0,
             0x5a363f: 0x5a36d0, 0x5a3537: 0x5a3ab0, 0x5a3747: 0x458690}
    pointers = {0xad223c: 0x5a4500, 0xaaa5fc: 0x43d820, 0xaaa5bc: 0x458240, 0xbd30a4: 0x30000002}
    for pin in proof['references']:
        binary = (WS / pin['file']).read_bytes()
        table, _ = vptr_store(binary, 0x5a4447)
        require(table == 0xad2238 and rtti(binary, table)['class_name'] == 'CNetMsgProcessor_Combat',
                'Pinned Combat processor')
        for site, target in calls.items():
            require(read_va(binary, site, 5) == b'\xe8' + struct.pack('<i', target - site - 5),
                    'Confirmed direct call at ' + hex(site))
        for site, value in pointers.items():
            require(read_va(binary, site, 4) == struct.pack('<I', value), 'Confirmed pointer or action at ' + hex(site))
    save('monster-force-result-reference', dict(
        **proof, raw=record(REFERENCE), scope='5/9 Combat receiver through remote monster Force assignment and action.',
        category=5, opcode=9, prefix_bytes=15, victim_stride=14, count_offset=14,
        actor_type_offset=0, actor_serial_offset=1, force_index_offset=5, force_level_offset=6,
        calls={hex(site - 0x400000): hex(target - 0x400000) for site, target in calls.items()},
        force_action='0x30000002', monster_force_permitted_by_reference=True))


def verify_live(link):
    report = json.loads(LIVE.read_text())
    require(report['normal_link_sha256'] == sha(path('normal-link')) and report['executable'] == link['executable']
            and sha(WS / report['staged_executable']) == link['executable']['sha256'], 'Exact live PE')
    check(report['events'])
    events = [json.loads(line) for line in (WS / report['events']['file']).read_text().splitlines()]
    require(report['debugger_exit'] == 0 and report['summary']['exit_observed']
            and report['live_server']['private_handoff_removed']
            and not any(row['kind'] == 'exception' and not row.get('first_chance') for row in events),
            'Clean NeutralB run')
    messages = [row['value'] for row in events if row['kind'] == 'debug_string']
    position = messages.index('RF455 Protocol:position-mode:0:0:0')
    require(messages.index('RF455 Protocol:map-bsp:0:1:0') < position
            < messages.index('RF455 Protocol:move-queued:4:1:12')
            < messages.index('RF455 Protocol:move-queued:4:12:6'), 'Own movement and stop on NeutralB')
    samples = [sample_values(value) for value in messages if value.startswith('RF455 WorldSample:')]
    require(len(samples) == 6 and samples[-2]['avatar_position'] == samples[-1]['avatar_position'],
            'Stable late position')
    displacement = math.dist(samples[0]['avatar_position'], samples[-1]['avatar_position'])
    require(displacement > 2, 'Actual avatar moved')
    require(len(report['world_frames']) == 2, 'Two NeutralB frames')
    for frame in report['world_frames']:
        check(frame)
    observed_force = sum(value.startswith('RF455 Protocol:monster-force-result:') for value in messages)
    return dict(world_frames=report['world_frames'], displacement=displacement, observed_force_events=observed_force)


def main():
    verify_reference()
    source = WS / 'scripts/native/client455_monster_force_result_probe.cpp'
    exe = build_full_object_probe('monster-force-result', source)
    files, _, clips = resource_inputs(exe.parent)
    result = subprocess.run([str(exe), *(str(file) for file in files)], cwd=exe.parent,
                            capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW, timeout=30)
    console = exe.parent / 'probe-console.txt'
    console.write_bytes(result.stdout + result.stderr)
    require(result.returncode == 0, f'Force result component check (exit {result.returncode}): '
            + result.stderr.decode(errors='replace'))
    runtime = json.loads(result.stdout)
    require(runtime == dict(status='PASS', selected_routes=2, rejected_cases=3,
                            missing_row_retained=True, real_animations=2), 'Unexpected fixture result')
    link = read('normal-link')
    live = verify_live(link)
    names = ('normal-link', 'normal-preparation', 'normal-build', 'normal-consumers',
             'monster-force-result-reference', 'skill-force-items-reference', 'live-resource-inputs',
             'own-entry', 'startup-audit', 'startup-taiwan-native', 'live-launcher-native')
    fresh = {name: record(path(name)) for name in names}
    fresh['monster-force-result-live'] = record(LIVE)
    symbols = {name: hex(rva) for rva, name in own_symbols(link)
               if name.startswith(('?MonsterForceResult455@CNetMsgProcessor_Combat@@', '?CreateForce455@CSFItem@@'))}
    require(len(symbols) == 2, 'Dispatcher and Force item both linked')
    sources = ('scripts/client455_monster_force_port.py', 'scripts/native/client455_monster_force_result.h',
               'scripts/native/client455_monster_force_dispatch.inc', 'scripts/native/client455_monster_force_result.inc')
    save('monster-force-result-checkpoint', dict(
        status='PARTIAL_COMPONENT_MONSTER_FORCE_RESULT',
        scope='Combat processor 5/9 to the active Force and normal monster action with real animation files.',
        normal_executable=link['executable'], normal_link_sha256=sha(path('normal-link')), fresh_evidence=fresh,
        runtime_login_report=record(LIVE), live_smoke=live,
        script=record(Path(__file__)), sources=[record(WS / name) for name in sources] + [record(source)],
        probe_executable={**record(exe), 'architecture': pe(exe.read_bytes())['architecture']},
        console=record(console), real_clips=clips, native=runtime, own_symbols=symbols,
        live_force_activation=bool(live['observed_force_events']), victim_effects_restored=False, M6='OPEN', M9='OPEN'))
    print(json.dumps(runtime))


if __name__ == '__main__':
    main()
