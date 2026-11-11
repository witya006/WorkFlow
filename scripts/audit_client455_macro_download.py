"""Pin the macro continuation, announcement setter and guild reply routes."""
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
CALLS = {0x5634b6: 0x566b10, 0x566fbf: 0x56fed0, 0x58a8bd: 0x58abd0,
         0x58ac0f: 0x511a90, 0x5af25f: 0x5b5f70}
VTABLE_SLOTS = {0xad1898: 0x58a6f0, 0xad26b0: 0x5aed10}
GAPS = [
    'Macro actions, chat command interpretation, slot presentation and keyboard execution',
    'Patriarch shout board and window; existing character-scoped state only retains the bounded text',
    'Guild member data application, Linker references, item owners, quest journal and entry into the playable world',
]


def main():
    private = WS / 'artifacts/client455-progress'
    raw = private / 'macro178-reference.json'
    proof = verify_regions(raw)
    require(proof['full_functions'] == 8, 'Eight complete functions')
    for pin in proof['references']:
        binary = (WS / pin['file']).read_bytes()
        for site, target in CALLS.items():
            code = read_va(binary, site, 5)
            require(code[0] == 0xe8 and site + 5 + struct.unpack_from('<i', code, 1)[0] == target,
                    'Pinned call ' + hex(site - BASE))
        for site, target in VTABLE_SLOTS.items():
            require(struct.unpack('<I', read_va(binary, site, 4))[0] == target, 'Pinned dispatcher vtable')
        require(read_va(binary, 0x56fee2, 8) == bytes.fromhex('c645f41bc645f56f'), 'Pinned request 27/111')
    sources = [Path(__file__), WS / 'scripts/client455_initial_download_port.py',
               WS / 'scripts/native/client455_initial_download.h', WS / 'scripts/native/client455_initial_download.inc']
    report = dict(**proof, raw=record(raw), decompilation=record(private / 'macro178-handlers.json'),
                  calls=[dict(site_rva=hex(site - BASE), handler_rva=hex(target - BASE)) for site, target in CALLS.items()],
                  macro=dict(handler_rva='0x166b10', bytes=954, action_refs=33, automatic_settings=3,
                             text_bank_count=2, text_rows_per_bank=5, text_stride=81),
                  shout=dict(handler_rva='0x18abd0', bytes=650, text_rows=10, text_stride=65),
                  guild=dict(request_rva='0x16fed0', group=27, request=111, reply=112, handler_rva='0x1b5f70'),
                  sources=[record(p) for p in sources], gaps=GAPS)
    save('macro-download-reference', report)
    print(json.dumps({key: proof[key] for key in ('full_functions', 'full_instructions', 'positive_cfg_blocks')}))


if __name__ == '__main__':
    main()
