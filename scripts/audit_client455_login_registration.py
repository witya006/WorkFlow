"""Pin the real screen registration and Login sprite-loading boundary.

Static input only. A matching body in the backup is provenance evidence, not
proof that the own client already implements the whole screen/Login behavior.
"""
import hashlib
import json
import struct
from pathlib import Path
from build_client455_x87_math import read_va
from compare_client_binaries import WS, pe


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    source = WS/'artifacts/client455-progress/login138-reference/registration-full.json'
    body = json.loads(source.read_text())
    functions = body['ranges']['result']
    cfg = {int(row['addr'],16): row for row in body['cfg']['result']}
    rows = []
    for row in functions:
        assert not row['error']
        address, size = int(row['fn']['addr'],16), int(row['fn']['size'],16)
        key = next(key for key in body['assemblies'] if int(key,16)==address)
        pages = body['assemblies'][key]
        assert pages[-1]['cursor']['done'] and body['functions'][key]['cursor']['done']
        decoded = [line for page in pages for line in page['asm']['lines']]
        assert all(len(page['asm']['lines'])<=100 for page in pages)
        assert len(decoded)==pages[0]['total_instructions']
        starts = {int(line['addr'],16) for line in decoded}
        assert len(starts)==len(decoded) and min(starts)==address
        flow = cfg[address]
        assert flow['cursor']['done'] and flow['count']==flow['total_blocks']
        blocks = [block for block in flow['blocks'] if block['size']>0]
        assert all(address<=int(block['start'],16)<int(block['end'],16)<=address+size for block in blocks)
        assert all(int(block['start'],16) in starts for block in blocks)
        rows.append(dict(rva=hex(address-0x400000),bytes=size,instructions=len(decoded),positive_cfg_blocks=len(blocks)))
    root = body['assemblies']['0x630A60'][0]['asm']['lines']
    assert next(line for line in root if line['addr']=='630aae')['instruction']=='push 0'
    assert next(line for line in root if line['addr']=='630ab8')['instruction']=='mov eax, [edx+30h]'
    target = json.loads((WS/'config/client-target.json').read_text())
    pins = []
    for folder, key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        file = WS/f'work/client-reference/{folder}/RF_Online.bin'
        raw = file.read_bytes()
        assert sha(file)==target[key]['sha256'] and pe(raw)['architecture']=='x86'
        u32 = lambda va: struct.unpack('<I',read_va(raw,va,4))[0]
        assert u32(0xADAD8C-4)==0xB808B4 and u32(0xB808B4)==0 and u32(0xB808B4+4)==0
        assert u32(0xB808B4+12)==0xBD5D1C
        assert read_va(raw,0xBD5D1C+8,16)==b'.?AVCGUIScreen@@'
        assert u32(0xADAD8C+208)==0x630A60 and u32(0xADAD8C+40)==0x632430
        ranges = [dict(row,sha256=hashlib.sha256(read_va(raw,0x400000+int(row['rva'],16),row['bytes'])).hexdigest()) for row in rows]
        pins.append(dict(file=file.relative_to(WS).as_posix(),sha256=sha(file),architecture='x86',image_base='0x400000',functions=ranges))
    assert pins[0]['functions']==pins[1]['functions']
    report = dict(status='STATIC_CONFIRMED_PARTIAL',scope='Root screen registration and six Login sprite requests;not complete455Login/UI acceptance',
        evidence=dict(file=source.relative_to(WS).as_posix(),sha256=sha(source)),references=pins,
        full_functions=len(rows),full_instructions=sum(row['instructions'] for row in rows),positive_cfg_blocks=sum(row['positive_cfg_blocks'] for row in rows),
        screen_vtable_rva='0x6dad8c',registration_rva='0x230a60',
        contracts=['Null registration is a no-op','AlwaysTop selects main-list front insertion;otherwise append',
                   'Container insertion deduplicates and temporarily inherits parent visibility',
                   'Root registration always calls child SetParent(root),then virtual Show(FALSE),even for a duplicate',
                   'Login sprite loading releases the manager,then requests target IDs0,1,3,2,4,5'],
        gaps=['Full root window/draw-layer/input/focus/state integration','Full455window init/layout and all10Login windows',
              'System sprite group5 and all remaining legacy-to-target UI callers','Four stages,Title movie,auth/selection/world flow'],
        input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN',
        script=dict(file=Path(__file__).relative_to(WS).as_posix(),sha256=sha(Path(__file__))))
    (WS/'inventory/client455-login-registration-reference.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(functions=len(rows),instructions=report['full_instructions'],cfg_blocks=report['positive_cfg_blocks'],equal_pins=2)))


if __name__=='__main__':
    main()
