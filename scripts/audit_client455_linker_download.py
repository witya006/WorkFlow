"""Verify initial Linker continuation opcodes and owner lookups against both pins."""
import json
import struct
from pathlib import Path

from build_client455_x87_math import read_va
from checkpoint_client455_party_window import read, save
from checkpoint_client455_rvp_effects import require
from client455_reference_regions import verify_regions
from client455_ui_checkpoint import record
from compare_client_binaries import WS


BASE = 0x400000
CALLS = {0x563263: 0x56ead0, 0x5634b6: 0x566b10, 0x56ee52: 0x566aa0, 0x56ee5d: 0x56fb90, 0x566fbf: 0x56fed0}
REQUESTS = {0x566ab9: (3, 49), 0x56fb9c: (13, 104), 0x56fee2: (27, 111)}
GAPS = [
    'Live nonempty Linker slots and configured banks; gesture and macro owners; auxiliary window and menu settings',
    'Macro and patriarch shout reply consumers and the subsequent initialization phases',
    'Inventory, Force, quests, map creation and ordinary playable world',
]


def main():
    private = WS / 'artifacts/client455-progress'
    raw = private / 'linker177-reference.json'
    proof = verify_regions(raw)
    require(proof['full_functions'] == 9, 'Nine complete selected functions')
    prior = read('mastery-quests-reference')
    require(all(any(row['rva'] == '0x16ead0' for row in ref['functions']) for ref in prior['references']),
            'Existing full Linker handler evidence')
    for pin in proof['references']:
        binary = (WS / pin['file']).read_bytes()
        for site, target in CALLS.items():
            code = read_va(binary, site, 5)
            require(code[0] == 0xe8 and site + 5 + struct.unpack_from('<i', code, 1)[0] == target,
                    'Pinned call ' + hex(site - BASE))
        for site, (group, opcode) in REQUESTS.items():
            expected = b'\xc6\x45\xf4' + bytes([group]) + b'\xc6\x45\xf5' + bytes([opcode])
            require(read_va(binary, site, 8) == expected, f'Pinned request {group}/{opcode}')
    sources = [Path(__file__), WS / 'scripts/client455_initial_download_port.py',
               WS / 'scripts/client455_linker_window_port.py', WS / 'scripts/native/client455_initial_download.h',
               WS / 'scripts/native/client455_initial_download.inc']
    report = dict(**proof, raw=record(raw), decompilation=record(private / 'linker177-handlers.json'),
                  linker_handler_rva='0x16ead0', linker_bytes=157, macro_handler_rva='0x166b10',
                  calls=[dict(site_rva=hex(site - BASE), handler_rva=hex(target - BASE)) for site, target in CALLS.items()],
                  requests=[dict(site_rva=hex(site - BASE), group=group, opcode=opcode)
                            for site, (group, opcode) in REQUESTS.items()], sources=[record(p) for p in sources], gaps=GAPS)
    save('linker-download-reference', report)
    print(json.dumps({key: proof[key] for key in ('full_functions', 'full_instructions', 'positive_cfg_blocks')}))


if __name__ == '__main__':
    main()
