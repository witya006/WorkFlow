"""Verify the target window functions and resources on the two pinned clients."""
import hashlib
import json
import struct
from pathlib import Path

from audit_client455_language import decode, records
from audit_client455_minimap_opacity import sprite_geometry
from build_client455_x87_math import read_va
from checkpoint_client455_rvp_effects import require
from client455_reference_regions import verify_regions
from client455_ui_checkpoint import record
from compare_client_binaries import WS


BASE = 0x400000
SLOTS = (
    (0xadd6ec, 0x18, 0x678b30), (0xadd6ec, 0x98, 0x678920),
    (0xadd804, 0x18, 0x679ca0), (0xadd804, 0x98, 0x679b50),
    (0xadd8fc, 0x18, 0x67a9d0), (0xadd8fc, 0x98, 0x67a620),
    (0xadd8fc, 0xd4, 0x67b4f0), (0xadd8fc, 0xdc, 0x67b6f0),
    (0xae586c, 0x18, 0x721ef0), (0xae586c, 0x98, 0x721ea0),
    (0xae5a8c, 0x18, 0x7231d0), (0xae5a8c, 0x98, 0x723060),
)
GAPS = [
    'Selected actor portrait, species, type-specific badges, status effects and player details',
    'Full target lifecycle and dynamic menu entries, sanction permissions and dispatch',
    '455 mission state window and complete dungeon counter lifecycle',
    'Base download and inventory data, world entry and M9 acceptance',
]


def main():
    raw = WS / 'artifacts/client455-progress/target-windows174-reference.json'
    proof = verify_regions(raw)
    require(proof['full_functions'] == 20, 'Complete selected target and dungeon window functions')
    assets = {4: ('main.spr', {(7, 0), (7, 1), (7, 2), (9, 1)} | {(8, i) for i in range(4)}),
              17: ('dungeon.spr', {(0, 0), (0, 1), (0, 3), (3, 0)}),
              41: ('renewal.spr', {(0, 1)})}
    for pin in proof['references']:
        binary = (WS / pin['file']).read_bytes()
        for table, slot, target in SLOTS:
            require(read_va(binary, table + slot, 4) == struct.pack('<I', target), 'Target window vtable')
        for ident, (name, _) in assets.items():
            field = read_va(binary, 0xbdb6a0 + 128 * ident, 128).split(b'\0', 1)[0]
            require(field.decode('ascii') == name, 'Target window sprite name')

    client = Path(json.loads((WS / 'config/paths.json').read_text())['client_455'])
    skins = []
    for ident, (name, frames) in assets.items():
        sprites = client / 'SpriteImage'
        path = sprites / 'zh-tw' / name
        if not path.is_file():
            path = sprites / 'Common' / name
        geometry = sprite_geometry(path, frames)
        require(len(geometry['requested']) == len(frames), 'All target window frames exist')
        skins.append(dict(id=ident, file=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest(), geometry=geometry))

    lang = client / 'DataTable/zh-tw/NDLanguage.edf'
    data = lang.read_bytes()
    entries, _ = records(decode(data))
    labels = {hex(i): entries[i][1].hex() for i in (*range(0x484, 0x48f), 0x16b1)}
    require(all(labels.values()), 'All selected target labels exist')
    sources = [Path(__file__), WS / 'scripts/client455_target_windows_port.py',
               WS / 'scripts/native/client455_target_windows.inc', WS / 'scripts/native/client455_target_menu.inc',
               WS / 'scripts/native/client455_dungeon_counter.inc']
    report = dict(**proof, raw=record(raw), sprites=skins,
                  vtable_slots=[dict(vtable_rva=hex(table - BASE), slot=slot, method_rva=hex(target - BASE))
                                for table, slot, target in SLOTS],
                  language=dict(file=str(lang), sha256=hashlib.sha256(data).hexdigest(), labels=labels),
                  sources=[record(p) for p in sources], gaps=GAPS, M6='OPEN', M9='OPEN')
    (WS / 'inventory/client455-target-windows-reference.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(dict(methods=proof['full_functions'], instructions=proof['full_instructions'],
                          cfg_blocks=proof['positive_cfg_blocks'], skins=len(skins), labels=len(labels))))


if __name__ == '__main__':
    main()
