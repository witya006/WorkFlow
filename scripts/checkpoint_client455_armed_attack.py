"""Check the typed armed-attack path against the 455 weapon consumers."""

import json
import struct
from pathlib import Path

from build_client455_x87_math import read_va
from checkpoint_client455_party_window import path, read, save
from checkpoint_client455_rvp_effects import check, require, sha
from client455_reference_regions import verify_regions
from client455_ui_checkpoint import record
from compare_client_binaries import WS


PRIVATE = WS / 'artifacts/client455-progress/armed201'
REFERENCE = PRIVATE / 'reference.json'
LIVE = PRIVATE / 'live.json'


def verify_reference():
    proof = verify_regions(REFERENCE)
    raw = json.loads(REFERENCE.read_text())
    require(raw['closed']['success'] and raw['closed']['saved'], 'Owned IDA session closed')
    slots = {0xaa91b8: 0x453d90, 0xaa91b4: 0x453730, 0xaa92ac: 0x462070}
    calls = {0x412efd: 0x413440, 0x4134e5: 0x5a4910, 0x5a49d7: 0x5a44d0}
    for pin in proof['references']:
        binary = (WS / pin['file']).read_bytes()
        for address, function in slots.items():
            require(read_va(binary, address, 4) == struct.pack('<I', function), 'Equipment slot ' + hex(address))
        for site, target in calls.items():
            require(read_va(binary, site, 5) == b'\xe8' + struct.pack('<i', target - site - 5),
                    'Armed attack call ' + hex(site))
        require(read_va(binary, 0x5a49cc, 2) == b'\x6a\x08', '455 ordinary request sends eight bytes')
    code = {address: function['code'] for address, function in raw['details'].items()}
    require(all(fragment in code['0x460bf0'] for fragment in ('+ 184', '+ 185', '== 20', '+ 192', '+ 228', '+ 224', '+ 220')),
            'Weapon, range device and unit-weapon metadata')
    require('sub_460BF0(this)' in code['0x462070'] and 'this + 156' in code['0x462070'],
            'Normal payload range adjustment')
    require('v2 == 5 || v2 == 6 || v2 == 7 || v2 == 11' in code['0x460dd0']
            and 'this + 268' in code['0x4718b0'] and 'this + 232' in code['0x426f10'],
            'Weapon and ammunition type comparison')
    save('armed-attack-reference', dict(
        **proof, raw=record(REFERENCE), scope='455 typed range, ammunition metadata and ordinary attack writer.',
        player_range_rva='0x53d90', weapon_range_offset=228, range_modifier_code=20,
        range_payload_bonus_offset=156, ammunition_categories=[5, 6, 7, 11],
        weapon_ammunition_offset=268, ammunition_tag_offset=232, ordinary_request_bytes=8,
        calls={hex(site - 0x400000): hex(target - 0x400000) for site, target in calls.items()}))


def verify_live(link):
    live = json.loads(LIVE.read_text())
    require(live['normal_link_sha256'] == sha(path('normal-link')) and live['executable'] == link['executable'],
            'Exact own armed attack build')
    check(dict(file=live['staged_executable'], sha256=link['executable']['sha256']))
    check(live['events'])
    require(live['debugger_exit'] == 0 and live['summary']['exit_observed'] and
            live['live_server']['private_handoff_removed'], 'Observed own exit and handoff cleanup')
    rows = [json.loads(line) for line in (WS / live['events']['file']).read_text().splitlines()]
    require(not any(row['kind'] == 'exception' and not row.get('first_chance') for row in rows),
            'No unhandled exception after the armed attack input')
    values = [row['value'] for row in rows if row['kind'] == 'debug_string']
    click = next(value for value in values if value.startswith('RF455 Protocol:combat-click:1:'))
    target = click.split(':')[-2]
    pick = 'RF455 Protocol:combat-pick:1:' + target
    keys = [value for value in values if value.startswith('RF455 Protocol:combat-key:')]
    require(len(keys) == 2 and all(key.split(':')[-2] == '32' for key in keys)
            and values.index(click) < values.index(pick + ':0') < values.index(keys[0])
            < values.index(pick + ':1') < values.index('RF455 Protocol:tx:5:14:1') < values.index(keys[1]),
            'Live pick, localized attack key and current mode transition')
    checks = [value for value in values if value.startswith('RF455 Protocol:combat-avatar-check:')]
    require(checks and all(value.endswith(':1:1:0') for value in checks)
            and values.count('RF455 Protocol:combat-weapon:6:5:1') == len(checks)
            and 'RF455 Protocol:combat-weapon:6:5:1' in values[values.index(keys[-1]):],
            'Live weapon is a bow and the ordinary ammunition check stops the attack')
    require('RF455 Protocol:base-applied:0:0:0' in values
            and 'RF455 Protocol:inventory-applied:3:21:0' in values,
            'Base equipment and 21 inventory records reach unpopulated board consumers')
    require(not any(value.startswith(('RF455 Protocol:combat-range-check:', 'RF455 Protocol:tx:5:1:'))
                    for value in values), 'Attack stops before range and serialization')
    for frame in live['monster_frames']:
        check(frame)
    return dict(target=int(target), localized_attack_keys=len(keys), bow_checks=len(checks),
                weapon_category=5, ammunition_check_passed=False, base_items_created=0,
                inventory_rows=21, inventory_placed=0, ordinary_attack_sent=False, unhandled_exceptions=0)


def main():
    verify_reference()
    link = read('normal-link')
    result = verify_live(link)
    names = ('normal-link', 'normal-preparation', 'normal-build', 'normal-consumers', 'armed-attack-reference',
             'own-entry', 'startup-audit', 'startup-taiwan-native', 'live-launcher-native')
    sources = ('scripts/client455_armed_attack_port.py', 'scripts/native/client455_equipment_conditions.h',
               'scripts/client455_initial_download_port.py', 'scripts/native/client455_walk_observation.inc',
               'scripts/native/client455_camera_mouse_observation.inc')
    save('armed-attack-checkpoint', dict(
        status='PARTIAL_LIVE_AMMUNITION_UNAVAILABLE',
        scope='The ordinary armed attack reaches typed bow and ammunition validation on NeutralB.',
        normal_executable=link['executable'], normal_link_sha256=sha(path('normal-link')),
        runtime_login_report=record(LIVE), observations=result, script=record(Path(__file__)),
        sources=[record(WS / name) for name in sources],
        fresh_evidence={name: record(path(name)) for name in names},
        previous_attempts=[record(PRIVATE / f'{stage}-live.json') for stage in ('first', 'second', 'third')],
        M6='OPEN', M9='OPEN'))
    print(json.dumps(result))


if __name__ == '__main__':
    main()
