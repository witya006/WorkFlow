"""Corroborate 455 service-window dispatch, sprite geometry and exchange packets."""
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
    'CGUIExchangeWindow': dict(Init=0x690af0, SetSprite=0x691550, SetRaceType=0x691610,
                              InitEconomyRatePoint=0x691630, InsertEconomyRatePoint=0x691650,
                              SetExchangeRate=0x691670, SetExchangeCommission=0x6916a0, SetExchangeAdjustbar=0x6916d0,
                              SetTaxRate=0x6917d0, SetGold=0x691830, SetDalant=0x6918d0, MouseEvent=0x691a10,
                              ScrollEvent=0x691ba0, ClosingDialogBox=0x691e40),
    'CExchangeBoard': dict(InitWindow=0x491760, ExchangeMoney_Request=0x4917e0, ExchangeMoney_Result=0x4918a0,
                           ClearExchange=0x491920, MsgProc=0x491990),
    'CGUIMiningWindow': dict(Init=0x67fe80, SetSprite=0x6801a0, SelectOre=0x6802d0, Mining_On=0x680360,
                             Mining_Off=0x6803a0, EnableMiningButton=0x6803e0, MouseEvent=0x680430),
    'CGUIClassChangeWindow': dict(Init=0x68d960, SetSprite=0x68ded0, SetTotalClassNum=0x68e000, SelectClass=0x68e1e0,
                                 SetSkillIcon=0x68e270, SetClassName=0x68e560, SetDescription=0x68e5d0,
                                 MouseEvent=0x68e710),
    'CNetMsgProcessor_ItemTrade': dict(ExchangeDalantForGoldRequest_clzo=0x599160,
                                      ExchangeGoldForDalantRequest_clzo=0x5991b0,
                                      ExchangeMoneyResult_zocl=0x599200),
    'CGUIHotKeyBoard': dict(SetLinkWindow455=0x66cb20),
}
GAPS = [
    'Live currency transactions and all other item-trade subtypes; economy auxiliary value at payload offset 17',
    'Full mining conditions, mining packets, timings, tool and resource result behavior',
    'Ordinary promotion choices and skill owner data, promotion requests and results, related class-reset windows',
    'Full Linker layout, key and action dispatch, all remaining MainGame owners, world entry and M9 acceptance',
]


def pin_dispatch(binary, startup):
    slots = ((0xaad264, 4, 0x491760), (0xaaf374, 4, 0x513230), (0xaadf5c, 4, 0x4eab30),
             (0xadea34, 0x18, 0x691550), (0xadea34, 0x98, 0x690af0), (0xadea2c, 0, 0x691a10),
             (0xaddb74, 0x18, 0x6801a0), (0xaddb74, 0x98, 0x67fe80), (0xaddb6c, 0, 0x680430),
             (0xade734, 0x18, 0x68ded0), (0xade734, 0x98, 0x68d960), (0xade728, 0, 0x68e710))
    for table, slot, va in slots:
        require(read_va(binary, table + slot, 4) == struct.pack('<I', va), '455 service window dispatch')
    required = {0x547fb9: 'push 10h', 0x547fcc: 'push 0Dh', 0x547fd9: 'call eax',
                0x547fdb: 'push 11h', 0x547fee: 'push 0Bh', 0x547ffb: 'call eax',
                0x547ffd: 'push 12h', 0x54800c: 'push 64h', 0x54800e: 'push 0C8h',
                0x548013: 'push 24h', 0x548020: 'call eax'}
    require(all(startup[va].split(' ;', 1)[0] == instruction for va, instruction in required.items()),
            '455 ordinary service window IDs and positions')
    require(startup[0x548650] == 'push 6' and startup[0x54866d] == 'call sub_66CB20',
            'Single ordinary 455 Linker attachment')
    body = read_va(binary, 0x547fb9, 0x548022 - 0x547fb9)
    opcode = read_va(binary, 0x597fa6, 7)
    require(opcode[:3] == bytes.fromhex('ff248d'), '455 trade dispatch switch')
    switch = struct.unpack_from('<I', opcode, 3)[0]
    for subtype, dispatch in ((13, 0x597ffc), (14, 0x59800a), (15, 0x598018)):
        index = read_va(binary, 0x5980a4 + subtype - 2, 1)[0]
        require(read_va(binary, switch + 4 * index, 4) == struct.pack('<I', dispatch), '455 trade receipt subtype')
    for va, op in ((0x597f48, '6a0c'), (0x59918d, '6a08'), (0x599193, '6a0a'),
                   (0x5991dd, '6a08'), (0x5991e3, '6a0b'), (0x59923e, '8b5001'), (0x599249, '8b5009')):
        data = bytes.fromhex(op)
        require(read_va(binary, va, len(data)) == data, '455 exchange packed field or send arguments')
    names = {i: read_va(binary, 0xbdb6a0 + 128 * i, 128).split(b'\0', 1)[0].decode('ascii')
             for i in (1, 4, 11, 12, 20)}
    require({i: name.lower() for i, name in names.items()} ==
            {1: 'common.spr', 4: 'main.spr', 11: 'mining.spr', 12: 'exchange.spr', 20: 'class.spr'}, '455 service skins')
    return dict(sprite_names=names, boards=[[16, 13], [17, 11], [18, 36]],
                startup=dict(rva='0x147fb9', bytes=len(body), sha256=hashlib.sha256(body).hexdigest()),
                slots=[dict(table_rva=hex(table - BASE), slot=slot, target_rva=hex(va - BASE)) for table, slot, va in slots],
                linker=dict(board=6, call_rva='0x14866d', attach_rva='0x26cb20'),
                exchange=dict(group=12, requests=[10, 11], request_bytes=8, result=13,
                              success_bytes=17, gold_offset=1, dalant_offset=9))


def asset_records(root, names):
    requested = {1: {(4, 0)} | {(0, f) for f in range(6)} | {(1, f) for f in range(4)} |
                    {(2, f) for f in range(4)} | {(8, f) for f in range(6, 12)},
                 4: {(8, f) for f in range(4)}, 11: {(0, 0), (0, 1), (0, 2)},
                 12: {(0, 0)}, 20: {(0, 0), (0, 1), (0, 2)}}
    rows = []
    for ident, name in names.items():
        locale = root / 'SpriteImage' / 'zh-tw' / name
        path = locale if locale.is_file() else root / 'SpriteImage' / 'Common' / name
        geometry = sprite_geometry(path, requested[ident])
        require(len(geometry['requested']) == len(requested[ident]), 'Every 455 service sprite frame exists')
        rows.append(dict(id=ident, file=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest(), geometry=geometry))
    return rows


def main():
    private = WS / 'artifacts/client455-progress'
    raw = private / 'service-windows172-reference.json'
    proof = verify_regions(raw)
    require(proof['full_functions'] == 45, 'All selected service window, Linker and wire functions')
    pages = json.loads((private / 'board166-reference.json').read_text())['asm']['0x5477c0']
    startup = {int(line['addr'], 16): line['instruction'] for page in pages for line in page['asm']['lines']}
    variants = [pin_dispatch((WS / pin['file']).read_bytes(), startup) for pin in proof['references']]
    require(variants[0] == variants[1], 'Both pins agree on service windows and exchange wire')
    root = Path(json.loads((WS / 'config/paths.json').read_text())['client_455'])
    assets = asset_records(root, variants[0]['sprite_names'])
    labels = []
    for folder in ('zh-tw', 'ko-kr', 'ru-ru', 'en-gb'):
        path = root / 'DataTable' / folder / 'NDLanguage.edf'
        if not path.is_file():
            continue
        data = path.read_bytes()
        rows, _ = records(decode(data))
        indices = (0x39b, 0x39c, 0x39d, 0x39e, *range(0x13c2, 0x13c9))
        labels.append(dict(file=str(path), sha256=hashlib.sha256(data).hexdigest(),
                           records={hex(i): bool(i < len(rows) and rows[i][1].rstrip(b'\0')) for i in indices}))
    sources = [Path(__file__), WS / 'scripts/client455_service_windows_port.py', WS / 'scripts/client455_board_startup_port.py']
    sources += [WS / 'scripts/native' / name for name in ('client455_exchange_window.inc', 'client455_exchange_board.inc',
                                                        'client455_mining_window.inc', 'client455_class_change_window.inc')]
    report = dict(**proof, raw=record(raw), startup=variants[0], assets=assets, labels=labels,
                  sources=[record(p) for p in sources], gaps=GAPS, M6='OPEN', M9='OPEN')
    (WS / 'inventory/client455-service-windows-reference.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(dict(methods=proof['full_functions'], instructions=proof['full_instructions'],
                          cfg_blocks=proof['positive_cfg_blocks'], skins=len(assets), locales=len(labels))))


if __name__ == '__main__':
    main()
