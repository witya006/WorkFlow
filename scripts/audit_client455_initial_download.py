"""Pin the initial-download handler ranges, opcode routes and lookup tables."""
import json
import struct
from pathlib import Path

from build_client455_x87_math import read_va
from checkpoint_client455_rvp_effects import require
from client455_reference_regions import verify_regions
from client455_ui_checkpoint import record
from compare_client_binaries import WS


BASE = 0x400000
ROUTES = {4: (0x5631b9, 0x56bea0), 6: (0x5631ca, 0x56d080),
          8: (0x5631fd, 0x56d960), 10: (0x56320e, 0x56df30)}
REQUESTS = {5: (0x56cff9, 0x56cfe0), 7: (0x56d8d9, 0x56d8c0), 9: (0x56dea9, 0x56de90)}
LEGACY_ITEM_KINDS = bytes((1, 2, 3, 4, 5, 7, 6, 8, 9, 10, 11, 12, 14, 13, 0, 18, 15, 16,
                           17, 19, 20, 21, 22, 23, 24, 25))
GAPS = [
    'Additional 455 item kinds, alternate accessory and special equipment slots, item modifiers and timers',
    'Additional base fields including ranking, secondary gauge, appearance and flags; full error UI',
    'Mastery and quest handlers, subsequent initial download phases, ordinary map and avatar creation',
]


def main():
    raw = WS / 'artifacts/client455-progress/initial-download175-reference.json'
    proof = verify_regions(raw)
    require(proof['full_functions'] == 8, 'Eight complete download-related bodies')
    for pin in proof['references']:
        binary = (WS / pin['file']).read_bytes()
        for opcode, (site, target) in ROUTES.items():
            instruction = read_va(binary, site, 5)
            require(instruction[0] == 0xe8 and site + 5 + struct.unpack_from('<i', instruction, 1)[0] == target,
                    f'455 reply route 3/{opcode}')
        for opcode, (site, _) in REQUESTS.items():
            instruction = read_va(binary, site, 8)
            require(instruction == bytes.fromhex('c645f803c645f9') + bytes((opcode,)),
                    f'455 request type 3/{opcode}')
        require(b'\x68\xaf\x01\x00\x00' in read_va(binary, 0x56bece, 0x56bee1 - 0x56bece),
                '431-byte base copy')
        require(read_va(binary, 0xab3770, len(LEGACY_ITEM_KINDS)) == LEGACY_ITEM_KINDS,
                'Supported equipment and inventory table index mapping')
    source = [Path(__file__), WS / 'scripts/client455_initial_download_port.py',
              WS / 'scripts/native/client455_initial_download.h', WS / 'scripts/native/client455_initial_download.inc']
    report = dict(**proof, raw=record(raw), group=3, base_bytes=431, inventory_prefix=3, inventory_stride=30,
                  force_prefix=2, force_stride=11, item_map_rva=hex(0xab3770 - BASE),
                  supported_item_kinds=list(LEGACY_ITEM_KINDS),
                  routes=[dict(opcode=op, site_rva=hex(site - BASE), handler_rva=hex(target - BASE))
                          for op, (site, target) in ROUTES.items()],
                  requests=[dict(opcode=op, site_rva=hex(site - BASE), handler_rva=hex(target - BASE))
                            for op, (site, target) in REQUESTS.items()],
                  sources=[record(item) for item in source], gaps=GAPS, M6='OPEN', M9='OPEN')
    (WS / 'inventory/client455-initial-download-reference.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(dict(methods=proof['full_functions'], instructions=proof['full_instructions'],
                          cfg_blocks=proof['positive_cfg_blocks'])))


if __name__ == '__main__':
    main()
