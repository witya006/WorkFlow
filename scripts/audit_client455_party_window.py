"""Pin the 455 party window, target resources and base request to both clients."""
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
METHODS = {
    'CGUIPartyMemberInfo': dict(Init=0x6eb000, SetSprite=0x6eb740, ClearMemberInfo=0x6eb890, SetCharName=0x6eb920,
                               SetLevel=0x6eb9a0, SetGauge455=0x6ebac0, MouseEvent=0x6ebfb0, Layout455=0x6ec1e0),
    'CGUIPartyWindow': dict(Init=0x6ed090, SetSprite=0x6ed400, SetWindowType=0x6ed4e0, AddMember=0x6edb50,
                           RemoveMember=0x6ee220, RemoveAllMember=0x6ee680, EnableLockNLeaveButton=0x6ef2d0,
                           SetDistribution455=0x6ef320, MouseEvent=0x6ef480, SetTotalMemberNum=0x6ef6b0,
                           Layout455=0x6ef840),
    'CPartyBoard': dict(InitWindow=0x4a32a0),
    'CNetworkMgr': dict(InitMsg_BaseDownloadRequest_clzo=0x56be40),
}
GAPS = [
    'Full live party roster data and class portrait provider, status tooltips, locks, loot policy and related packet paths',
    'Remaining 455 window interactions and complete party creation, join, invite and leave scenarios',
    'Base download result, follow-up player inventory and map data, world entry and M9 acceptance',
]


def inspect_pin(binary, assembly):
    slots = ((0xaad7d8, 4, 0x4a32a0), (0xae2df4, 0x18, 0x6eb740), (0xae2de8, 0, 0x6ebfb0),
             (0xae2ec4, 0x18, 0x6ed400), (0xae2ec4, 0x98, 0x6ed090), (0xae2ebc, 0, 0x6ef480),
             (0xab0324, 0x38, 0x5488d0))
    for table, slot, target in slots:
        require(read_va(binary, table + slot, 4) == struct.pack('<I', target), '455 party or base request dispatch')
    require(assembly[0x5484e4] == 'push 0' and assembly[0x5484e6] == 'push 13h' and
            assembly[0x5484f9] == 'call eax' and assembly[0x5488bc] == 'call eax', '455 MainGame party and download sites')
    require(read_va(binary, 0x56be59, 8) == bytes.fromhex('c645f803c645f903'), '455 request bytes 03 03')
    names = {i: read_va(binary, 0xbdb6a0 + 128 * i, 128).split(b'\0', 1)[0].decode('ascii') for i in (1, 4, 20, 49)}
    require({i: n.lower() for i, n in names.items()} == {1: 'common.spr', 4: 'main.spr', 20: 'class.spr', 49: 'etcui.spr'},
            '455 party skins')
    call = read_va(binary, 0x5484e4, 0x5484fb - 0x5484e4)
    return dict(window=19, startup_rva='0x1484e4', startup_sha256=hashlib.sha256(call).hexdigest(),
                sprite_names=names, base_request=dict(group=3, subtype=3, payload=0, send_rva='0x16be40'),
                slots=[dict(table_rva=hex(table - BASE), slot=slot, target_rva=hex(target - BASE))
                       for table, slot, target in slots])


def main():
    private = WS / 'artifacts/client455-progress'
    raw = private / 'party-window173-reference.json'
    proof = verify_regions(raw)
    require(proof['full_functions'] == 25, 'All selected party and base request bodies')
    pages = json.loads((private / 'board166-reference.json').read_text())['asm']['0x5477c0']
    assembly = {int(line['addr'], 16): line['instruction'] for page in pages for line in page['asm']['lines']}
    variants = [inspect_pin((WS / item['file']).read_bytes(), assembly) for item in proof['references']]
    require(variants[0] == variants[1], 'Both pinned binaries agree')
    client = Path(json.loads((WS / 'config/paths.json').read_text())['client_455'])
    frames = {1: {(1, i) for i in range(4)}, 4: {(0, i) for i in range(1, 4)} | {(6, i) for i in range(19)},
              20: {(0, 2)}, 49: {(0, 0), (0, 2)}}
    assets = []
    for i, name in variants[0]['sprite_names'].items():
        locale = client / 'SpriteImage' / 'zh-tw' / name
        path = locale if locale.is_file() else client / 'SpriteImage' / 'Common' / name
        geom = sprite_geometry(path, frames[i])
        require(len(geom['requested']) == len(frames[i]), '455 stock party frames')
        assets.append(dict(id=i, file=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest(), geometry=geom))
    lang = client / 'DataTable/zh-tw/NDLanguage.edf'
    data = lang.read_bytes()
    entries, _ = records(decode(data))
    labels = {hex(i): entries[i][1].hex() for i in range(0x3de, 0x3e8)}
    require(entries[0x3e6][1].count(b'%d') == 1 and entries[0x3e7][1].count(b'%d') == 2, '455 party title formats')
    sources = [Path(__file__), WS / 'scripts/client455_party_window_port.py', WS / 'scripts/native/client455_party_window.inc']
    report = dict(**proof, raw=record(raw), startup=variants[0], assets=assets,
                  language=dict(file=str(lang), sha256=hashlib.sha256(data).hexdigest(), labels=labels),
                  sources=[record(p) for p in sources], gaps=GAPS, M6='OPEN', M9='OPEN')
    (WS / 'inventory/client455-party-window-reference.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(dict(methods=proof['full_functions'], instructions=proof['full_instructions'],
                          cfg_blocks=proof['positive_cfg_blocks'], skins=len(assets))))


if __name__ == '__main__':
    main()
