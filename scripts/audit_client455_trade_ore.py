"""Check the player trade and ore dispatch, startup and skin evidence."""
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
    'CGUITradeWindow': {
        'Init': 0x71fb20, 'SetSprite': 0x7207d0, 'SetLock_Avatar': 0x720dc0,
        'SetAccept_Avatar': 0x720ef0, 'SetLock_Other': 0x721360, 'SetAccept_Other': 0x7213c0,
        'SetAvatarDalant': 0x720c40, 'SetAvatarGold': 0x720d00, 'SetOtherDalant': 0x721240,
        'SetOtherGold': 0x7212d0, 'SetEnableSocketNum_Avatar': 0x720a20,
        'SetEnableSocketNum_Other': 0x721000, 'MouseEvent': 0x721450,
    },
    'CGUIOreProcWindow': {
        'Init': 0x6956d0, 'SetSprite': 0x695f30, 'SetProcPrice': 0x6960b0,
        'EnableDisposal': 0x696710, 'TakeInResultOre': 0x696140, 'EnableProc': 0x696840,
    },
}
GAPS = [
    'Trade and ore transactions through the real client protocol and managed item providers',
    '64-bit player money entry, validation and packet ownership; legacy trade packets remain',
    'Complete trade drag quantity, focus, locale and device reload behavior',
    'Complete mining and item work owners, remaining startup registrations and game world',
]


def pin_dispatch(binary, lines):
    targets = ((0xaad9ec, 4, 0x4b5e30), (0xaacabc, 4, 0x482840),
               (0xae574c, 0x18, 0x7207d0), (0xae574c, 0x98, 0x71fb20),
               (0xadec6c, 0x18, 0x695f30), (0xadec6c, 0x98, 0x6956d0))
    for table, slot, method in targets:
        require(read_va(binary, table + slot, 4) == struct.pack('<I', method), '455 window dispatch')
    startup = {
        0x547c1b: 'push 0Fh', 0x547c1d: 'push 1', 0x547c1f: 'push 0Ah', 0x547c2c: 'call eax',
        0x547c3d: 'push 0', 0x547c3f: 'push 0C8h', 0x547c44: 'push 17h', 0x547c51: 'call eax',
        0x547c62: 'push 28h', 0x547c64: 'push 1', 0x547c66: 'push 0Bh', 0x547c73: 'call eax',
        0x547c84: 'push 0', 0x547c91: 'call eax', 0x547ca2: 'push 0', 0x547ca4: 'push 0',
        0x547ca6: 'push 0Ch', 0x547cb3: 'call eax',
        0x547cea: 'push 0Fh', 0x547d2e: 'push 10h', 0x547fcc: 'push 0Dh', 0x547fee: 'push 0Bh',
        0x5484e6: 'push 13h',
    }
    require(all(lines[va].split(' ;', 1)[0] == operand for va, operand in startup.items()),
            '455 board startup instructions')
    names = {i: read_va(binary, 0xbdb6a0 + 128 * i, 128).split(b'\0', 1)[0].decode('ascii')
             for i in (1, 10, 16, 44)}
    require({i: name.lower() for i, name in names.items()} ==
            {1: 'common.spr', 10: 'oreproc.spr', 16: 'trade.spr', 44: 'socketstate.spr'}, '455 sprite lookup names')
    ranges = [(0x547c1b, 0x547cb5), (0x54681f, 0x546871), (0x547270, 0x547351),
              (0x547cc4, 0x547d3d), (0x547fb9, 0x547ffd), (0x5484e0, 0x5484fb),
              (0x5454e0, 0x54579c), (0x546056, 0x54608d)]
    return dict(
        sprite_names=names, windows={'player_trade': 23, 'ore_processing': 12},
        slots=[dict(table_rva=hex(table - BASE), slot=slot, target_rva=hex(method - BASE))
               for table, slot, method in targets],
        code=[dict(rva=hex(start - BASE), bytes=end - start,
                   sha256=hashlib.sha256(read_va(binary, start, end - start)).hexdigest())
              for start, end in ranges],
    )


def main():
    private = WS / 'artifacts/client455-progress'
    raw = private / 'trade-ore170-reference.json'
    proof = verify_regions(raw)
    require(proof['full_functions'] == 21, 'Full selected window methods')
    board = private / 'board166-reference.json'
    rows = json.loads(board.read_text())['asm']['0x5477c0']
    lines = {int(line['addr'], 16): line['instruction'] for page in rows for line in page['asm']['lines']}
    variants = [pin_dispatch((WS / pin['file']).read_bytes(), lines) for pin in proof['references']]
    require(variants[0] == variants[1], 'Both pins agree on window registration and dispatch')
    client = Path(json.loads((WS / 'config/paths.json').read_text())['client_455'])
    assets = []
    for name in variants[0]['sprite_names'].values():
        for locale in ('zh-tw', 'Common'):
            source = client / 'SpriteImage' / locale / name
            if not source.is_file():
                continue
            data = source.read_bytes()
            assets.append(dict(file=str(source), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data), **sprite(data)))
    require(any(row['file'].lower().endswith('trade.spr') and row['frames'][0] >= 5 for row in assets) and
            any(row['file'].lower().endswith('oreproc.spr') for row in assets), 'Stock trade and ore assets')
    sources = [Path(__file__), WS / 'scripts/client455_trade_ore_port.py',
               WS / 'scripts/native/client455_player_trade_window.inc', WS / 'scripts/native/client455_ore_window.inc']
    report = dict(**proof, raw=record(raw), startup=variants[0], assets=assets, sources=[record(p) for p in sources],
                  gaps=GAPS, M6='OPEN', M9='OPEN')
    (WS / 'inventory/client455-trade-ore-reference.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(dict(methods=proof['full_functions'], instructions=proof['full_instructions'],
                          cfg_blocks=proof['positive_cfg_blocks'], skins=len(assets))))


if __name__ == '__main__':
    main()
