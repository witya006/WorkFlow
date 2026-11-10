"""Verify the 455 shop startup, selected methods and stock sprite assets."""
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
    'Ordinary NPC catalog, managed item ownership and full per-item metadata',
    'Exact mouse, dialog and board dispatch, purchase/sale/repair and server results',
    'Production sources for 64-bit money and PVP/points, locale and resource reload',
    'Remaining MainGame board registrations, world entry and M9 acceptance',
]


def pin_startup(binary):
    slots = ((0xaada94, 4, 0x4b8350), (0xadef0c, 0x18, 0x6990a0), (0xadef0c, 0x98, 0x6987f0))
    for table, offset, callee in slots:
        require(read_va(binary, table + offset, 4) == struct.pack('<I', callee), '455 shop dispatch')
    instructions = {
        0x547bb3: '68c8000000', 0x547bb8: '6a01', 0x547bba: '6a09', 0x547bc7: 'ffd0',
        0x547bd8: '6a00', 0x547be5: 'ffd0', 0x547bf6: '6a00', 0x547bf8: '68c8000000',
        0x547bfd: '6a07', 0x547c0a: 'ffd0',
    }
    for va, hex_bytes in instructions.items():
        expected = bytes.fromhex(hex_bytes)
        require(read_va(binary, va, len(expected)) == expected, '455 shop startup argument')
    table = 0xbdb6a0
    names = {i: read_va(binary, table + 128 * i, 128).split(b'\0', 1)[0].decode('ascii') for i in (1, 9)}
    require({i: name.lower() for i, name in names.items()} == {1: 'common.spr', 9: 'shop.spr'}, '455 shop skins')
    region = read_va(binary, 0x547bb3, 0x547c0c - 0x547bb3)
    return dict(startup_rva='0x147bb3', startup_bytes=len(region), startup_sha256=hashlib.sha256(region).hexdigest(),
                board=9, pack_slots=200, window=7, original_position=[200, 0], sprite_names=names,
                slots=[dict(table_rva=hex(table - BASE), slot=offset, target_rva=hex(target - BASE))
                       for table, offset, target in slots])


def main():
    raw = WS / 'artifacts/client455-progress/shop169-reference.json'
    proof = verify_regions(raw)
    require(proof['full_functions'] == 16, 'Full selected shop methods')
    paths = json.loads((WS / 'config/paths.json').read_text())
    client = Path(paths['client_455'])
    variants = [pin_startup((WS / pin['file']).read_bytes()) for pin in proof['references']]
    require(variants[0] == variants[1], 'Both 455 references agree on shop startup')
    assets = []
    for name in variants[0]['sprite_names'].values():
        for locale in ('zh-tw', 'Common'):
            source = client / 'SpriteImage' / locale / name
            if not source.is_file():
                continue
            data = source.read_bytes()
            assets.append(dict(file=str(source), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data), **sprite(data)))
    require(any(row['file'].lower().endswith('shop.spr') and row['frames'][0] >= 3 for row in assets),
            'Stock shop root and tabs')
    require(any(row['file'].lower().endswith('common.spr') and row['frames'][6] >= 7 for row in assets),
            'Stock common pager action')
    sources = [Path(__file__), WS / 'scripts/client455_shop_window_port.py', WS / 'scripts/native/client455_shop_window.inc']
    report = dict(**proof, raw=record(raw), startup=variants[0], assets=assets, sources=[record(p) for p in sources],
                  gaps=GAPS, M6='OPEN', M9='OPEN')
    (WS / 'inventory/client455-shop-window-reference.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(dict(methods=proof['full_functions'], instructions=proof['full_instructions'],
                          cfg_blocks=proof['positive_cfg_blocks'], skins=len(assets))))


if __name__ == '__main__':
    main()
