"""Check the selected 455 view and startup evidence for Skill and Force."""
import hashlib
import json
import struct
from pathlib import Path

from audit_client455_sprites import sprite
from build_client455_x87_math import read_va
from checkpoint_client455_rvp_effects import require
from client455_reference_regions import verify_regions
from client455_ui_checkpoint import record
from compare_client_binaries import WS


BASE = 0x400000
GAPS = [
    'Real production SkillForce.edf population through managed payloads and the ordinary board owners',
    'Remaining mastery names and levels, hotkey transfer, cooldowns, tooltips, skill/force use and network consumers',
    'Full resize/reload, scroll position and nonfinite/error cases for populated windows',
    'Equipment storage/ID migration, remaining MainGame registrations and complete gameplay acceptance',
]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def check_dispatch(binary):
    tables = {
        0xae112c: {0x18: 0x6c84e0, 0x98: 0x6c80b0, 0x10: 0x6c8550},
        0xae106c: {0x18: 0x6c7240, 0x98: 0x620410},
        0xae1224: {0x18: 0x6c9790, 0x98: 0x6c9570},
        0xae0d44: {0x18: 0x6c00c0, 0x98: 0x6bff70},
        0xae0fb4: {0x18: 0x6c6960, 0x0c: 0x6c69e0},
        0xaad15c: {0x84: 0x4903e0}, 0xaacfcc: {0x04: 0x48d490, 0x84: 0x48d220},
    }
    slots = []
    for table, methods in tables.items():
        for offset, method in methods.items():
            data = read_va(binary, table + offset, 4)
            require(struct.unpack('<I', data)[0] == method, 'Pinned 455 Skill/Force dispatch')
            slots.append(dict(table_rva=hex(table - BASE), slot=offset, target_rva=hex(method - BASE), bytes=data.hex()))
    return slots


def check_startup(binary, lines):
    operands = {
        0x547a4e: 'push 14h', 0x547a50: 'push 7', 0x547a52: 'push 7', 0x547a70: 'push 3Ch',
        0x547a72: 'push 0C8h', 0x547a77: 'push 5', 0x547a95: 'push 64h', 0x547a97: 'push 0Ch',
        0x547a99: 'push 7', 0x547aa3: 'mov eax, [edx+84h]',
        0x547aba: 'push 14h', 0x547abc: 'push 6', 0x547abe: 'push 3', 0x547adc: 'push 3Ch',
        0x547ade: 'push 12Ch', 0x547ae3: 'push 6', 0x547b01: 'push 64h', 0x547b03: 'push 18h',
        0x547b05: 'push 6', 0x547b0f: 'mov eax, [edx+84h]',
    }
    require(all(lines[a].split(' ;', 1)[0] == value for a, value in operands.items()), 'Actual board startup operands')
    result = []
    for name, start, end in [('skill_force', 0x547a3f, 0x547b17), ('gauge_window_id', 0x54723a, 0x547256)]:
        data = read_va(binary, start, end - start)
        if name == 'gauge_window_id':
            require(data[:2] == b'\x6a\x04' and data[-2:] == b'\xff\xd0', 'Actual Gauge ID 4 dispatch')
        result.append(dict(name=name, rva=hex(start - BASE), bytes=end - start, sha256=digest(data)))
    return result


def main():
    private = WS / 'artifacts/client455-progress'
    raw = private / 'skill-force168-reference.json'
    proof = verify_regions(raw)
    require(proof['full_functions'] == 24, 'All selected 455 Skill/Force bodies')
    main_game = private / 'board166-reference.json'
    lines = {int(line['addr'], 16): line['instruction']
             for page in json.loads(main_game.read_text())['asm']['0x5477c0'] for line in page['asm']['lines']}
    refs = []
    for pin in proof['references']:
        binary = (WS / pin['file']).read_bytes()
        table = 0xbdb6a0
        sprite_names = []
        for index, name in ((1, 'common.spr'), (45, 'skillwindow.spr'), (46, 'forcewindow.spr')):
            value = read_va(binary, table + 128 * index, 128).split(b'\0', 1)[0].decode('ascii')
            require(value.lower() == name, 'Target sprite name ' + name)
            sprite_names.append(value)
        refs.append(dict(slots=check_dispatch(binary), startup=check_startup(binary, lines), sprite_names=sprite_names))
    require(refs[0] == refs[1], 'Both reference binaries agree on Skill/Force startup, vtables and sprite names')
    client = Path(json.loads((WS / 'config/paths.json').read_text())['client_455'])
    assets = []
    for locale in ('Common', 'zh-tw'):
        for name in refs[0]['sprite_names']:
            path = client / 'SpriteImage' / locale / name
            if path.is_file():
                data = path.read_bytes()
                assets.append(dict(file=str(path), sha256=digest(data), bytes=len(data), **sprite(data)))
    require(any(row['file'].lower().endswith('skillwindow.spr') and row['frames'][1] >= 5 for row in assets), 'Skill tab frames')
    require(any(row['file'].lower().endswith('forcewindow.spr') and row['frames'][0] >= 6 for row in assets), 'Force tab frames')
    native = WS / 'scripts/native'
    source = [Path(__file__), WS / 'scripts/client455_skill_force_window_port.py',
              native / 'client455_skill_force_window.inc', native / 'client455_force_window.inc',
              native / 'client455_skill_force_row.inc', native / 'client455_gui_tab_board.cpp']
    normal = WS / 'work/client455-port/normal/source'
    generated = [normal / 'define.h', normal / 'gameprogress/cgp_maingame.cpp']
    generated += [normal / 'userinterface/gamewindow/skillforce' / name for name in
                  ('guiskillwindow.h', 'guiskillwindow.cpp', 'guiforcewindow.cpp')]
    report = dict(status='STATIC_CONFIRMED_PARTIAL', **proof, raw=record(raw), main_game_reference=record(main_game),
                  both_pin_dispatch=refs[0], assets=assets, sources=[record(path) for path in source],
                  generated=[record(path) for path in generated],
                  skill=dict(board=7, packs=7, slots=20, window=5, position=[200, 60], creation=[7, 12, 100],
                             section_counts=[4, 4, 1, 3, 1], sprite=[45, 1]),
                  force=dict(board=3, packs=6, slots=20, window=6, position=[300, 60], creation=[6, 24, 100],
                             section_counts=[4, 4, 4, 4, 4], sprite=[46, 0], first_frame={'Bellato': 0, 'Cora': 5},
                             accretia_window_created=False),
                  row=dict(size=[207, 44], icon_background=[40, 40], icon=[38, 38], row_sprite=[45, 0]),
                  gaps=GAPS, full_gameplay=False, input_exe_executed=False, server_modified=False)
    (WS / 'inventory/client455-skill-force-window-reference.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(dict(functions=proof['full_functions'], instructions=proof['full_instructions'], assets=len(assets))))


if __name__ == '__main__':
    main()
