"""Verify the target store-list request, NPC records and MainGame gate."""
import json
import struct
from pathlib import Path

from build_client455_x87_math import read_va
from checkpoint_client455_party_window import save
from checkpoint_client455_rvp_effects import require
from client455_reference_regions import verify_regions
from client455_ui_checkpoint import record
from compare_client_binaries import WS


BASE = 0x400000
CALLS = {0x56ee4a: 0x4bb120, 0x4bb135: 0x5980c0, 0x5980e2: 0x597f30, 0x597fb4: 0x5980f0,
         0x598147: 0x51b3f0, 0x59817e: 0x558ac0, 0x54658c: 0x56eef0, 0x563197: 0x56ef90}
OPERANDS = {0x5980dd: '6a08', 0x597f48: '6a0c', 0x558ad2: '89481c',
            0x546532: '83781c00', 0x56ef0f: 'c645f403c645f501'}


def main():
    private = WS / 'artifacts/client455-progress'
    raw = private / 'store179-reference.json'
    proof = verify_regions(raw)
    require(proof['full_functions'] == 9, 'Nine complete functions')
    for pin in proof['references']:
        binary = (WS / pin['file']).read_bytes()
        for site, target in CALLS.items():
            code = read_va(binary, site, 5)
            require(code[0] == 0xe8 and site + 5 + struct.unpack_from('<i', code, 1)[0] == target,
                    'Pinned call ' + hex(site - BASE))
        for site, pattern in OPERANDS.items():
            expected = bytes.fromhex(pattern)
            require(read_va(binary, site, len(expected)) == expected, 'Pinned operand ' + hex(site - BASE))
    sources = [Path(__file__), WS / 'scripts/client455_initial_download_port.py',
               WS / 'scripts/native/client455_initial_download.h', WS / 'scripts/native/client455_initial_download.inc',
               WS / 'scripts/probe_client455_device_startup.py', WS / 'scripts/probe_client455_live_launcher.py']
    report = dict(**proof, raw=record(raw), decompilation=record(private / 'store179-handlers.json'),
                  calls=[dict(site_rva=hex(site - BASE), handler_rva=hex(target - BASE)) for site, target in CALLS.items()],
                  store=dict(group=12, request=8, reply=9, request_rva='0x1980c0', handler_rva='0x1980f0',
                             prefix=1, stride=16, position=4),
                  gate=dict(owner_offset='0x1c', setter_rva='0x158ac0', reader_rva='0x1464d0'),
                  position=dict(group=3, request=1, reply=2, request_rva='0x16eef0', handler_rva='0x16ef90'),
                  sources=[record(p) for p in sources])
    save('store-download-reference', report)
    print(json.dumps({key: proof[key] for key in ('full_functions', 'full_instructions', 'positive_cfg_blocks')}))


if __name__ == '__main__':
    main()
