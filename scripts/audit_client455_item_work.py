"""Verify the 455 crafting and upgrade dispatch, assets and selected methods."""
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
METHODS = {
    'CGUIItemMakeWindow': dict(Init=0x6b9dc0, SetSprite=0x6ba0f0, SetMakeGroup=0x6ba1c0, SetMaterialStr=0x6ba570),
    'CGUIItemListWindow': dict(Create=0x6b8910, Init=0x6b8c80, SetSprite=0x6b9050, TakeInItem=0x6b9160,
                              TakeOutItem=0x6b9300, SetTab=0x6b94d0, SetPage=0x6b9640, SelectItem=0x6b9730,
                              DeselectItem=0x6b97e0, MouseEvent=0x6b9830),
    'CGUIItemUpgradeWindow': dict(Init=0x6becc0, SetSprite=0x6bf2b0, UpdateReturnButton455=0x6bf350,
                                 TakeInItem=0x6bf420, TakeOutItem=0x6bf4d0, MouseEvent=0x6bf5b0),
}
GAPS = [
    'Ordinary 455 recipe table owners, skill and eligibility checks, and material lookups',
    'Full crafting and upgrade requests, authoritative server results and managed item movement',
    'Remaining 455 error paths, locale/device reload behavior and all remaining MainGame startup owners',
    'World entry and M9 acceptance',
]


def pin_dispatch(binary, lines):
    targets = ((0xaac9dc, 4, 0x4811d0), (0xaac8e4, 4, 0x47fd90),
               (0xae0694, 0x18, 0x6ba0f0), (0xae0694, 0x98, 0x6b9dc0),
               (0xae0584, 0x18, 0x6b9050), (0xae0584, 0x98, 0x6b8c80),
               (0xae0a3c, 0x18, 0x6bf2b0), (0xae0a3c, 0x98, 0x6becc0))
    for table, slot, method in targets:
        require(read_va(binary, table + slot, 4) == struct.pack('<I', method), '455 crafting dispatch')
    startup = {
        0x547cc4: 'push 0', 0x547cc6: 'push 0', 0x547cc8: 'push 0Eh', 0x547cd5: 'call eax',
        0x547ce6: 'push 0', 0x547ce8: 'push 0', 0x547cea: 'push 0Fh', 0x547cf7: 'call eax',
        0x547d08: 'push 6', 0x547d0a: 'push 1', 0x547d0c: 'push 0Fh', 0x547d19: 'call eax',
        0x547d2a: 'push 0', 0x547d2c: 'push 0', 0x547d2e: 'push 10h', 0x547d3b: 'call eax',
        0x547d4c: 'push 0', 0x547d59: 'call eax',
    }
    require(all(lines[va].split(' ;', 1)[0] == op for va, op in startup.items()), '455 startup arguments')
    counts = struct.unpack('<3H', read_va(binary, 0xbd74e0, 6))
    require(counts == (9, 5, 2), '455 recipe tab counts')
    names = {i: read_va(binary, 0xbdb6a0 + 128 * i, 128).split(b'\0', 1)[0].decode('ascii')
             for i in (1, 14, 15, 44)}
    require({i: name.lower() for i, name in names.items()} ==
            {1: 'common.spr', 14: 'itemmake.spr', 15: 'itemupgrade.spr', 44: 'socketstate.spr'}, '455 item skins')
    body = read_va(binary, 0x547cc4, 0x547d5b - 0x547cc4)
    return dict(sprite_names=names, tabs=list(counts), recipe_capacity=100, craft_window=15, upgrade_window=16,
                startup=dict(rva='0x147cc4', bytes=len(body), sha256=hashlib.sha256(body).hexdigest()),
                slots=[dict(table_rva=hex(table - BASE), slot=slot, target_rva=hex(method - BASE))
                       for table, slot, method in targets])


def main():
    private = WS / 'artifacts/client455-progress'
    raw = private / 'item-work171-reference.json'
    proof = verify_regions(raw)
    require(proof['full_functions'] == 24, 'All selected item work methods')
    pages = json.loads((private / 'board166-reference.json').read_text())['asm']['0x5477c0']
    lines = {int(line['addr'], 16): line['instruction'] for page in pages for line in page['asm']['lines']}
    variants = [pin_dispatch((WS / pin['file']).read_bytes(), lines) for pin in proof['references']]
    require(variants[0] == variants[1], 'Both pins agree on item work dispatch, tabs and startup')
    client = Path(json.loads((WS / 'config/paths.json').read_text())['client_455'])
    assets = []
    for name in variants[0]['sprite_names'].values():
        for locale in ('zh-tw', 'Common'):
            source = client / 'SpriteImage' / locale / name
            if not source.is_file():
                continue
            data = source.read_bytes()
            assets.append(dict(file=str(source), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data), **sprite(data)))
    require(any(r['file'].lower().endswith('itemmake.spr') and r['frames'] == [1, 10, 6, 3] for r in assets)
            and any(r['file'].lower().endswith('itemupgrade.spr') for r in assets), 'Stock craft and upgrade skins')
    sources = [Path(__file__), WS / 'scripts/client455_item_work_port.py', WS / 'scripts/client455_shop_window_port.py']
    sources += [WS / 'scripts/native' / name for name in
                ('client455_item_make.inc', 'client455_item_upgrade.inc', 'client455_gui_page_board.h',
                 'client455_shop_window.inc')]
    report = dict(**proof, raw=record(raw), startup=variants[0], assets=assets, sources=[record(p) for p in sources],
                  gaps=GAPS, M6='OPEN', M9='OPEN')
    (WS / 'inventory/client455-item-work-reference.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(dict(methods=proof['full_functions'], instructions=proof['full_instructions'],
                          cfg_blocks=proof['positive_cfg_blocks'], skins=len(assets))))


if __name__ == '__main__':
    main()
