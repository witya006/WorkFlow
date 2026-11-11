"""Verify the post-selection mastery, quest and special download routes in 455."""
import json
import struct
from pathlib import Path

from build_client455_x87_math import read_va
from checkpoint_client455_rvp_effects import require
from client455_reference_regions import verify_regions
from client455_ui_checkpoint import record
from compare_client_binaries import WS


BASE = 0x400000
ROUTES = {8: (0x5631fd, 0x56d960), 12: (0x56321f, 0x56e0e0),
          14: (0x563241, 0x56e470), 15: (0x563252, 0x56e880),
          45: (0x563263, 0x56ead0), 55: (0x5634e6, 0x568e90)}
REQUESTS = {11: (0x56e099, 0x56e080), 13: (0x56e429, 0x56e410),
            46: (0x56ea49, 0x56ea30), 54: (0x568e3c, 0x568e30)}
GAPS = [
    'Inventory, Force, and ore records still require compatible item owners and data providers',
    'Quest catalog resolution does not restore the active journal, goals, progress, timers or text',
    'Populated unit, Animus and miner paths need data owners and live verification; miner items are not placed',
    'Linker slots and configuration, subsequent client startup, and entry into the playable world',
]


def rvas(mapping):
    return [dict(opcode=op, site_rva=hex(site - BASE), handler_rva=hex(target - BASE))
            for op, (site, target) in mapping.items()]


def main():
    raw = WS / 'artifacts/client455-progress/mastery-quests176-reference.json'
    proof = verify_regions(raw)
    require(proof['full_functions'] == 11, 'Eleven complete selected functions')
    for pin in proof['references']:
        binary = (WS / pin['file']).read_bytes()
        for opcode, (site, target) in ROUTES.items():
            instruction = read_va(binary, site, 5)
            require(instruction[0] == 0xe8 and site + 5 + struct.unpack_from('<i', instruction, 1)[0] == target,
                    f'455 reply route 3/{opcode}')
        for opcode, (site, _) in REQUESTS.items():
            require(read_va(binary, site, 8) == bytes.fromhex('c645f803c645f9') + bytes((opcode,)),
                    f'455 request type 3/{opcode}')
    sources = [Path(__file__), WS / 'scripts/client455_initial_download_port.py']
    sources.extend(WS / 'scripts/native' / name for name in
                   ('client455_initial_download.h', 'client455_initial_download.inc', 'client455_client_items.h',
                    'client455_item_object.cpp', 'client455_item_payloads.h'))
    report = dict(**proof, raw=record(raw), group=3, routes=rvas(ROUTES), requests=rvas(REQUESTS),
                  mastery_prefix=322, mastery_full_bytes=382, quest_stride=14, unit_stride=67,
                  animus_stride=18, miner_stride=5, sources=[record(p) for p in sources], gaps=GAPS)
    (WS / 'inventory/client455-mastery-quests-reference.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({key: proof[key] for key in ('full_functions', 'full_instructions', 'positive_cfg_blocks')}))


if __name__ == '__main__':
    main()
