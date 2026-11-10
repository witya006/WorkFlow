"""Pin the recovered unit windows and their ordinary MainGame startup to 455."""
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
TABLE = 0xbdb6a0
COUNTRY_METHODS = [0x82c890, 0x82fbe0, 0x82c890, 0x831e10, 0x82d340, 0x82c890,
                   0x82d9f0, 0x82e770, 0x82c890, 0x82f4f0, 0x830960]
GAPS = [
    'UnitTuning item providers, main-frame/repair/tuning transaction logic and complete network consumers',
    'UnitStorehouse list row art/data, scrolling, selecting and delivery with actual units',
    'Reload while panels contain active purchases and full window lifecycle/country checks',
    'Remaining MainGame factory and window registrations, including the legacy dungeon mission ID colliding with 455 Animus',
    'Actual world, gameplay and all prior M6F acceptance gaps',
]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def check_tables(binary, country):
    tables = [
        (0xae61f4, 0x18, 0x72d950), (0xae61f4, 0x98, 0x72bb90),
        (0xae60dc, 0x18, 0x72a9f0), (0xae60dc, 0x98, 0x72a700),
        (0xae60dc, 0x28, 0x65ea40), (0xaadc3c, 4, 0x4bd1b0),
        (0xaadc3c, 12, 0x4be290),
    ]
    slots = []
    for table, offset, method in tables:
        raw = read_va(binary, table + offset, 4)
        require(struct.unpack('<I', raw)[0] == method, 'Actual 455 vtable dispatch')
        slots.append(dict(table_rva=hex(table - BASE), offset=offset,
                          target_rva=hex(method - BASE), sha256=digest(raw)))
    providers = []
    for index, (row, expected) in enumerate(zip(country['classes'], COUNTRY_METHODS)):
        table = BASE + int(row['vtables'][0]['vtable_rva'], 16)
        raw = read_va(binary, table + 356, 4)
        require(struct.unpack('<I', raw)[0] == expected, 'Country provider slot 89')
        compact = index in (1, 3, 4, 6, 7, 9, 10)
        instruction = b'\xb8\x01\x00\x00\x00' if compact else b'\x33\xc0'
        value = expected + 12
        require(read_va(binary, value, len(instruction)) == instruction, 'Country compact option')
        providers.append(dict(country=row['name'], table_rva=hex(table - BASE), slot=89,
                              target_rva=hex(expected - BASE), value_rva=hex(value - BASE),
                              value_instruction=instruction.hex(), compact=compact))
    require(len(providers) == len(COUNTRY_METHODS), 'All eleven providers')
    return slots, providers


def check_startup(binary, lines):
    anchors = {
        0x5478dc: 'push 0C8h', 0x5478e1: 'push 8', 0x5478e3: 'push 0Ch',
        0x547901: 'push 0', 0x547903: 'push 12Ch', 0x547908: 'push 22h',
        0x547929: 'cmp [ebp+var_8], 8', 0x54794a: 'mov eax, [edx+28h]',
        0x547960: 'push 4', 0x547962: 'push 1', 0x547964: 'push 0Dh',
        0x547982: 'push 0', 0x54798c: 'mov eax, [edx+28h]',
        0x5479a0: 'push 64h', 0x5479a2: 'push 12Ch', 0x5479a7: 'push 23h',
    }
    require(all(lines[a].split(' ;', 1)[0] == operand for a, operand in anchors.items()),
            'Exact MainGame pack and window parameters')
    start, end = 0x5478cd, 0x5479b6
    return dict(rva=hex(start - BASE), bytes=end - start, sha256=digest(read_va(binary, start, end - start)))


def check_skill_force_dispatch(binary):
    discovered = []
    for name, store, table, initialize, skin in (
        ('CGUISkillWindow', 0x6c9487, 0xae1224, 0x6c9570, 0x6c9790),
        ('CGUIForceWindow', 0x6bfe87, 0xae0d44, 0x6bff70, 0x6c00c0),
    ):
        assignment = read_va(binary, store, 6)
        require(assignment == b'\xc7\x00' + struct.pack('<I', table), 'Next window constructor identity')
        for offset, target in ((0x98, initialize), (0x18, skin)):
            require(struct.unpack('<I', read_va(binary, table + offset, 4))[0] == target,
                    'Next window vtable dispatch')
        discovered.append(dict(name=name, vptr_store_rva=hex(store - BASE), bytes=assignment.hex(),
                               table_rva=hex(table - BASE), init_rva=hex(initialize - BASE),
                               set_sprite_rva=hex(skin - BASE)))
    return discovered


def main():
    private = WS / 'artifacts/client455-progress'
    raw = private / 'unit167-reference.json'
    proof = verify_regions(raw)
    require(proof['full_functions'] == 16, 'Selected full 455 unit bodies')
    unit_asm = json.loads(raw.read_text())['asm']
    messages = {0x730089: 0x538, 0x730280: 0x504, 0x7302df: 0x504, 0x730341: 0x504,
                0x7306f5: 0x535, 0x73071e: 0x536, 0x730744: 0x537, 0x73076a: 0x1204}
    emits = {int(line['addr'], 16): line['instruction'] for page in unit_asm['0x730050'] for line in page['asm']['lines']}
    require(all(emits[address].lower().split(';', 1)[0].strip() == f'push {value:x}h'
                for address, value in messages.items()), 'Target unit window message producers')
    dispatch = {int(line['addr'], 16): line['instruction'] for page in unit_asm['0x4be290'] for line in page['asm']['lines']}
    require(dispatch[0x4be2fd].endswith(', 504h'), 'Target unit board removal route')
    prior = private / 'board166-reference.json'
    lines = {int(line['addr'], 16): line['instruction']
             for page in json.loads(prior.read_text())['asm']['0x5477c0'] for line in page['asm']['lines']}
    country_file = WS / 'inventory/client455-charinfo-country-discovery.json'
    country = json.loads(country_file.read_text())
    refs = []
    for pin in proof['references']:
        binary = (WS / pin['file']).read_bytes()
        names = {}
        for sprite_id, expected in ((1, 'common.spr'), (18, 'unit.spr'), (44, 'SocketState.spr')):
            raw_name = read_va(binary, TABLE + 128 * sprite_id, 128).split(b'\0', 1)[0]
            require(raw_name.decode('ascii').lower() == expected.lower(), 'Target unit sprite filename')
            names[str(sprite_id)] = raw_name.decode('ascii')
        slots, providers = check_tables(binary, country)
        refs.append(dict(startup=check_startup(binary, lines), slots=slots, countries=providers, sprite_names=names,
                         next_skill_force=check_skill_force_dispatch(binary)))
    require(refs[0] == refs[1], 'Both 455 pins share unit startup, vtables and names')
    client = Path(json.loads((WS / 'config/paths.json').read_text())['client_455'])
    assets = []
    for locale in ('Common', 'zh-tw', 'ko-kr'):
        for name in refs[0]['sprite_names'].values():
            path = client / 'SpriteImage' / locale / name
            if not path.is_file():
                continue
            data = path.read_bytes()
            assets.append(dict(file=str(path), sha256=digest(data), bytes=len(data), **sprite(data)))
    sources = [Path(__file__), WS / 'scripts/client455_unit_windows_port.py']
    sources += [WS / 'scripts/native' / name for name in
                ('client455_unit_view_skin.h', 'client455_unit_tuning.inc', 'client455_unit_storehouse.inc')]
    normal = WS / 'work/client455-port/normal/source'
    generated = [normal / name for name in ('gameprogress/cgp_maingame.cpp', 'define.h', 'definemessage.h',
                                            'gameobject/board/shopboard/cunittuningboard.cpp')]
    generated += [normal / 'userinterface/gamewindow/unit' / name
                  for name in ('guiunittuningwindow.cpp', 'guiunitstorewindow.cpp')]
    report = dict(status='STATIC_CONFIRMED_PARTIAL', raw=record(raw), **proof,
                  both_pin_dispatch=refs[0], stock_assets=assets,
                  main_game_reference=record(prior), country_table_discovery=record(country_file),
                  sources=[record(path) for path in sources], generated=[record(path) for path in generated],
                  tuning=dict(board=12, packs=8, slots_per_pack=200, window=34, position=[300, 0],
                              size=[228, 571], create_rva='0x1478f0', init_rva='0x147915', pack_rva='0x14794d'),
                  store=dict(board=13, packs=1, slots_per_pack=4, window=35, position=[300, 100],
                             size=[228, 288], create_rva='0x147971', init_rva='0x1479b4', pack_rva='0x14798f'),
                  unit_window_messages=[dict(rva=hex(address - BASE), message=hex(value)) for address, value in messages.items()],
                  unit_board_remove_comparison_rva='0xbe2fd',
                  gaps=GAPS, full_unit_gameplay=False, input_exe_executed=False, server_modified=False)
    (WS / 'inventory/client455-unit-windows-reference.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(dict(functions=proof['full_functions'], instructions=proof['full_instructions'], assets=len(assets))))


if __name__ == '__main__':
    main()
