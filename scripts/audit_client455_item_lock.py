"""Pin the actual item lock child before migrating typed drag handlers."""
import hashlib
import json
import shutil
import struct
from pathlib import Path

from audit_client455_item_payloads import record
from audit_client455_sprites import sprite
from build_client455_x87_math import read_va
from checkpoint_client455_rvp_effects import check, load, require, sha
from compare_client_binaries import WS, pe


def main():
    evidence = WS/'artifacts/client455-progress/item-lock100-reference.json'
    raw = json.loads(evidence.read_text())
    functions = [row['fn'] for row in raw['ranges']['result']]
    require(len(functions) == 17 and all(functions), 'Canonical function coverage')
    require(all(row['cursor']['done'] for row in raw['functions']+raw['assembly']), 'Complete bodies')
    instructions = sum(row['instruction_count'] for row in raw['assembly'])
    require(instructions == 1610, 'Instruction coverage')
    pins = json.loads((WS/'config/client-target.json').read_text())
    references = []
    for folder, key in [('current', 'behavior_reference'), ('reference-backup', 'secondary_reference')]:
        path = WS/f'work/client-reference/{folder}/RF_Online.bin'
        binary = path.read_bytes()
        require(sha(path) == pins[key]['sha256'] and pe(binary)['architecture'] == 'x86', 'Pinned client')
        ranges = []
        for function in functions:
            addr, size = int(function['addr'], 16), int(function['size'], 16)
            ranges.append(dict(rva=hex(addr-0x400000), bytes=size,
                               sha256=hashlib.sha256(read_va(binary, addr, size)).hexdigest()))
        references.append(dict(sha256=sha(path), architecture='x86', image_base='0x400000', ranges=ranges))
    require(references[0]['ranges'] == references[1]['ranges'], 'Selected pins differ')
    client = Path(json.loads((WS/'config/paths.json').read_text())['client_455'])
    original = client/'SpriteImage/Common/ItemLock.spr'
    root = WS/'work/client-reference/item-lock455'
    root.mkdir(parents=True, exist_ok=True)
    copy = root/original.name
    shutil.copyfile(original, copy)
    shape = sprite(copy.read_bytes())
    require(shape['actions'] and shape['frames'][0], 'Actual lock glyph')
    inputs = load('client455-ready-cooldown-reference')['inputs']
    for row in inputs:
        check(row)
    fields=struct.unpack_from('<6I',copy.read_bytes(),12)
    inputs = inputs+[dict(**record(copy), original=str(original), target_id=52,
                         original_size=list(fields[1:3]),texture_size=list(fields[3:5]),
                         runtime_relative='SpriteImage/Common/ItemLock.spr', **shape)]
    report = dict(status='CONFIRMED_SELECTED', scope='Actual GUIItem lock child andtyped wrapper/Linker lock refresh;not full drag/use handlers',
                  script_sha256=sha(Path(__file__)), raw_evidence=[record(evidence)], references=references,
                  functions=17, instructions=instructions, inputs=inputs,
                  contracts=['flag21 BYTE controls lock visibility;wrapper refresh normalizes to0/1;direct GUI setter keeps BYTE value',
                             'sprite52/action0/frame0;position x+width-glyphWidth-3,y+3;Size alone doesnotreposition',
                             'SetData copies sprite descriptor/Show,then reapplies destination position;Empty leaves lock state',
                             'Both normal andclipped GUIItem Draw call the lock child normal Draw after timer/label;lock isnot clipped by item rectangle'],
                  gaps=['Typed hover manager/screen drag/actual use-remove-swap-hover/MsgProc/livecallbacks/potioncache/Macro/Vending/fullAdd/bootstrap remain mandatory',
                        'FullGUIItemchildren/privateABI/deviceReset/numeric/unsafe/OOM/concurrency/shutdown andallpriorclientgaps remain open'],
                  input_exe_executed=False, server_modified=False, M6='OPEN', M6F='OPEN', M7='OPEN', M9='OPEN')
    (WS/'inventory/client455-item-lock-reference.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(dict(functions=17, instructions=instructions, equal_ranges=17, sprite=shape,original_size=fields[1:3],texture_size=fields[3:5])))


if __name__ == '__main__':
    main()
