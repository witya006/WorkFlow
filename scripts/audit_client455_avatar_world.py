"""Verify avatar weapon/shield fade and compact chat on the pinned 455 builds."""
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
CALLS = {0x41b1af: 0x43d0d0, 0x41b1c8: 0x66ab70, 0x548c00: 0x44c5f0, 0x548c42: 0x44c5f0,
         0x548c27: 0x46e220, 0x548c35: 0x46e220, 0x548c69: 0x46e220, 0x548c77: 0x46e220}
VTABLE_SLOTS = {0xaa8d10: 0x41b190, 0xae7994: 0x747940, 0xae79a4: 0x747b20}
COLORS = {0x747cc1: 0x60030303, 0x747cf6: 0x90919181, 0x747d28: 0x90919181,
          0x747d67: 0x90919181, 0x747da0: 0x90919181}


def main():
    private = WS / 'artifacts/client455-progress'
    raw = private / 'avatar180-reference.json'
    proof = verify_regions(raw)
    require(proof['full_functions'] == 9, 'Nine complete selected functions')
    for pin in proof['references']:
        binary = (WS / pin['file']).read_bytes()
        for site, target in CALLS.items():
            code = read_va(binary, site, 5)
            require(code[0] == 0xe8 and site + 5 + struct.unpack_from('<i', code, 1)[0] == target,
                    'Pinned call ' + hex(site - BASE))
        for site, target in VTABLE_SLOTS.items():
            require(read_va(binary, site, 4) == struct.pack('<I', target), 'Pinned vtable slot ' + hex(site - BASE))
        for site, color in COLORS.items():
            require(read_va(binary, site, 5) == b'\x68' + struct.pack('<I', color), 'Pinned compact chat color')
    sources = [Path(__file__), WS / 'scripts/client455_player_owner_port.py', WS / 'scripts/client455_chat_port.py',
               WS / 'scripts/client455_initial_download_port.py', WS / 'scripts/native/client455_equipment_conditions.h',
               WS / 'scripts/probe_client455_device_startup.py']
    report = dict(**proof, raw=record(raw), decompilation=record(private / 'avatar180-handlers.json'),
                  calls=[dict(site_rva=hex(site - BASE), handler_rva=hex(target - BASE)) for site, target in CALLS.items()],
                  avatar=dict(mode_rva='0x1b190', create_rva='0x1488f0', wrapper_rva='0x4c5f0', fade_rva='0x6e220'),
                  chat=dict(init_rva='0x3478a0', empty_setup_rva='0x347940', draw_rva='0x347b20'),
                  sources=[record(p) for p in sources])
    save('avatar-world-reference', report)
    print(json.dumps({key: proof[key] for key in ('full_functions', 'full_instructions', 'positive_cfg_blocks')}))


if __name__ == '__main__':
    main()
