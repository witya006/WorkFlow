"""Verify the selected base-portal instructions and the ordinary inventory path."""

import argparse
import json
import struct
from pathlib import Path

from audit_client455_tutorial_integration import rtti, u32
from build_client455_x87_math import read_va
from checkpoint_client455_monster_force_damage import run_fixture
from checkpoint_client455_party_window import path, read, save
from checkpoint_client455_rvp_effects import check, require, sha
from client455_normal_link_evidence import validate_normal_link
from client455_own_probe import build_full_object_probe
from client455_reference_regions import verify_regions
from client455_ui_checkpoint import record
from compare_client_binaries import WS


REFERENCE = WS / 'artifacts/client455-progress/base-portal212/reference.json'
TRANSITION = REFERENCE.with_name('transition-reference.json')
LIVE = WS / 'artifacts/client455-progress/client455-world-base-portal-live-taiwan-native.json'
FIRST_ATTEMPT = WS / 'work/m9/f9d3bd6b/world-base-portal-live-taiwan001/debug-events.jsonl'
CALLS = {
    0x4750a6: 0x5c42d0,
    0x5c431c: 0x5c13b0,
    0x5c446d: 0x42d4f0,
    0x5c44cb: 0x4fad00,
    0x5c44e2: 0x7ca570,
    0x475cf8: 0x4fa290,
    0x42d5d4: 0x40c880,
}


def verify_linker_reference():
    binary = WS / 'work/client-reference/current/RF_Online.bin'
    fingerprint = sha(binary)
    require(fingerprint == 'b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b',
            'Pinned x86 455 Linker reference')
    raw = binary.read_bytes()
    table = 0xaae914
    identity = rtti(raw, table)
    require(identity['class_name'] == 'CLinkBoard' and u32(raw, table + 132) == 0x500f80,
            'Linker primary vtable use method')
    for site, target in {0x5010dd: 0x4faa70, 0x501122: 0x4faa70,
                         0x55b0e2: 0x55b9f0, 0x55b588: 0x55b9f0,
                         0x55e3d1: 0x6692e0}.items():
        require(read_va(raw, site, 5) == b'\xe8' + struct.pack('<i', target - site - 5),
                f'Linker reference call at {site:#x}')
    require(read_va(raw, 0x55e3ac, 7) == bytes.fromhex('c745f8c0000000'),
            'Reference bank-switch virtual key is VK_OEM_3')
    return dict(sha256=fingerprint, architecture='x86', use_rva='0x100f80',
                physical_source_ids=[1, 0], slot_keys_rva='0x15b9f0',
                next_bank_rva='0x15e3a0', next_bank_vk=0xc0, **identity)


def verify_reference():
    proof = verify_regions(REFERENCE)
    transition = verify_regions(TRANSITION)
    for file in (REFERENCE, TRANSITION):
        raw = json.loads(file.read_text(encoding='utf-8'))
        require(raw['closed']['success'] and raw['closed']['saved'], 'Owned IDA session closed')
    for name in ('full_functions', 'full_instructions', 'positive_cfg_blocks'):
        proof[name] += transition[name]
    for pin, extra in zip(proof['references'], transition['references']):
        require(pin['sha256'] == extra['sha256'], 'Same pinned client')
        pin['functions'] += extra['functions']
    for pin in proof['references']:
        binary = (WS / pin['file']).read_bytes()
        for site, target in CALLS.items():
            require(read_va(binary, site, 5) == b'\xe8' + struct.pack('<i', target - site - 5),
                    f'455 base portal call at {site:#x}')
    save('base-portal-reference', dict(
        **proof, raw=record(REFERENCE), raw_transition=record(TRANSITION),
        group=4, request_opcode=26, request_payload_bytes=2,
        result_opcode=27, successful_codes=[0, 10], successful_bytes=8, signed_position_offsets=[2, 4, 6],
        successful_return_item_removal=1, same_map_delay_ms=700, after_arrival_delay_ms=1300,
        original_calls={hex(site - 0x400000): hex(target - 0x400000) for site, target in CALLS.items()}))


def verify_live(link_sha):
    report = json.loads(LIVE.read_text(encoding='utf-8'))
    require(report['normal_link_sha256'] == link_sha and report['debugger_exit'] == 0 and
            report['reached_first_login'] and report['live_server']['private_handoff_removed'],
            'Current own client and authorized local server handoff')
    require(report['base_portal_input'] == [
        dict(kind='base_portal_inventory_posted', own_child_validated=True, sent=True)],
        'One ordinary inventory event')
    require(not any(not row.get('first_chance') for row in report['exceptions']),
            'No unhandled exception in the live portal scenario')
    events = report['protocol_observations']
    prefix = 'RF455 Protocol:'
    lines = [value.removeprefix(prefix) for value in events if value.startswith(prefix)]
    require(lines.count('tx:4:26:2') == 1 and lines.count('rx:4:27:8') == 1,
            'One actual portal request and result')
    expected = ['rx:3:2:1', 'tx:4:26:2', 'rx:4:27:8', 'base-portal-result:4:0:8',
                'tx:3:1:1', 'rx:3:2:1', 'position-mode:3:0:0']
    position = -1
    ordered = []
    for value in expected:
        position = lines.index(value, position + 1)
        ordered.append(dict(event=value, index=position))
    events_file = WS / report['events']['file']
    check(report['events'])
    first = [json.loads(line) for line in FIRST_ATTEMPT.read_text(encoding='utf-8').splitlines()]
    fault = next(row for row in first if row['kind'] == 'exception' and not row['first_chance'])
    require(fault['rva'] == '0x13893a' and fault['code'] == '0xc0000005',
            'Original live reproduction after successful response')
    samples = [value for value in report['world_observations'] if value.startswith('RF455 WorldSample:')]
    return dict(report=record(LIVE), events=record(events_file), ordered=ordered, samples=samples,
                first_attempt=record(FIRST_ATTEMPT), first_attempt_draw_rva=fault['rva'])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--with-live', action='store_true')
    args = parser.parse_args()
    verify_reference()
    linker_reference = verify_linker_reference()
    link = read('normal-link')
    require(validate_normal_link(link) == 'PASS', 'Exact current client build')
    link_sha = sha(path('normal-link'))
    startup = read('startup-taiwan-native')
    require(startup['normal_link_sha256'] == link_sha and startup['debugger_exit'] == 0 and
            startup['summary']['after_sound_reached'] and startup['summary']['exit_observed'],
            'Current independent early Taiwan startup')
    item = next(row for row in read('item-payloads-reference')['inputs']
                if Path(row['file']).name == 'item.edf')
    check(item)
    client = Path(json.loads((WS / 'config/paths.json').read_text())['client_455'])
    key_map = client / 'DataTable/ru-ru/KeyMap.dat'
    source = WS / 'scripts/native/client455_base_portal_probe.cpp'
    exe = build_full_object_probe('base-portal', source)
    native, console = run_fixture(exe, [WS / item['file'], key_map], [], 'base-portal')
    require(native == dict(status='PASS', request=[4, 26], reply=[4, 27], success_codes=[0, 10],
                           quantity=[10, 9], bad_map_cases=2, refusal=True, malformed=True,
                           send_failure=True, cancel=True, same_map_no_loading_overlay=True,
                           linker_mouse=[4, 9], stale_shortcut=True, linker_f10=[4, 9],
                           keyboard_slots=10, chat_focus_suppressed=True, repeat_interval_ms=500),
            'Base portal native fixture')
    names = ('normal-link', 'normal-preparation', 'normal-build', 'normal-consumers',
             'own-entry', 'startup-audit', 'startup-taiwan-native', 'base-portal-reference')
    sources = ('client455_base_portal_port.py', 'native/client455_base_portal_inventory.inc',
               'native/client455_base_portal_position.inc', 'native/client455_base_portal_probe.cpp',
               'client455_linker_window_port.py', 'native/client455_linker_use.inc',
               'native/client455_linker_window.cpp', 'client455_linker_input_port.py',
               'native/client455_linker_input.inc')
    live = verify_live(link_sha) if args.with_live else None
    save('base-portal-checkpoint' if live else 'linker-use-checkpoint', dict(
        status='PARTIAL_LIVE_BASE_PORTAL' if live else 'PARTIAL_COMPONENT_BASE_PORTAL',
        scope='Inventory, fifth-bank Linker mouse/F1–F10, send ring and ordinary map transition.',
        normal_executable=link['executable'], normal_link_sha256=link_sha,
        component=native, component_executable=record(exe), component_console=console, item=item,
        linker_reference=linker_reference,
        key_map=dict(relative=key_map.relative_to(client).as_posix(), sha256=sha(key_map)),
        script=record(Path(__file__)), sources=[record(WS / 'scripts' / name) for name in sources],
        fresh_evidence={name: record(path(name)) for name in names},
        gaps=['Physical mouse use, travel from farther away and movement after arrival remain to be checked.' if live
              else 'Server reply and post-transition movement still need a live Bellato HQ run.',
              'Special Return map/area checks and cross-map resources remain open.',
              'The current map remains bound during the request for legacy world consumers.'],
        own_live_run=live is not None, live=live, M6='OPEN', M9='OPEN'))
    print(json.dumps(dict(executable=link['executable']['sha256'], component=native,
                          live=live['ordered'] if live else None)))


if __name__ == '__main__':
    main()
