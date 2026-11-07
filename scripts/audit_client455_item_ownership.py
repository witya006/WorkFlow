"""Pin selected item ownership bodies and extract independent x86 record oracles."""
import hashlib
import json
import struct
from pathlib import Path

from build_client455_x87_math import read_va
from checkpoint_client455_rvp_effects import check, require, sha
from compare_client_binaries import WS, pe


def record(path):return dict(file=path.relative_to(WS).as_posix(),sha256=sha(path))


def eax_immediate_store(raw,va):
    """Decode only C6/C7 /0 [EAX+optional disp8],imm8/32,never execute bytes."""
    code=read_va(raw,va,12);require(code[0] in [0xc6,0xc7],'Expected immediate store')
    mod,reg,rm=code[1]>>6,(code[1]>>3)&7,code[1]&7
    require(mod in [0,1] and reg==0 and rm==0,'Unexpected store addressing')
    offset=struct.unpack('b',code[2:3])[0] if mod==1 else 0
    at=3 if mod==1 else 2;width=1 if code[0]==0xc6 else 4
    return dict(rva=hex(va-0x400000),offset=offset,bytes=width,
                value=int.from_bytes(code[at:at+width],'little'),instruction=code[:at+width].hex())


def main():
    raw_path=WS/'artifacts/client455-progress/item-ownership087-reference.json'
    ref=json.loads(raw_path.read_text());pins=json.loads((WS/'config/client-target.json').read_text())
    require(len(ref['functions'])==24 and all(r['code'] and not r['truncated'] and r['line_count']==r['total_lines']
            for r in ref['functions']),'Incomplete selected pseudocode')
    require(len(ref['ranges']['result'])==24 and all(r['fn'] and not r['error'] for r in ref['ranges']['result']),'Incomplete ranges')
    ranges={r['fn']['addr'].lower():r['fn'] for r in ref['ranges']['result']};assemblies=[]
    for body in ref['assembly']:
        lines=[r for p in body['pages'] for r in p['asm']['lines']]
        start=int(body['addr'],16);end=start+int(ranges[body['addr'].lower()]['size'],16)
        require(len(lines)==len({r['addr'] for r in lines})==body['pages'][0]['total_instructions'] and
                all(start<=int(line['addr'],16)<end for line in lines),'Truncated/duplicated assembly '+body['addr'])
        assemblies.append(dict(rva=hex(start-0x400000),instructions=len(lines)))
    require(len(assemblies)==14 and sum(r['instructions'] for r in assemblies)==579,'Assembly coverage')
    references=[];ctor_writes=[]
    stores=[0x45fc8f,0x45fc98,0x45fca2,0x45fcac,0x45fcb3,0x45fcbd,0x45fcc4,0x45fccb]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';raw=path.read_bytes()
        require(sha(path)==pins[key]['sha256'] and pe(raw)['architecture']=='x86','Changed pin')
        selected=[]
        for row in ref['ranges']['result']:
            fn=row['fn'];va,size=int(fn['addr'],16),int(fn['size'],16)
            selected.append(dict(rva=hex(va-0x400000),bytes=size,sha256=hashlib.sha256(read_va(raw,va,size)).hexdigest()))
        writes=[eax_immediate_store(raw,va) for va in stores]
        require(not references or references[0]['ranges']==selected and writes==ctor_writes,'Selected functions/oracle differ between pins')
        references.append(dict(sha256=sha(path),architecture='x86',image_base='0x400000',ranges=selected));ctor_writes=writes
    require([(r['offset'],r['bytes']) for r in ctor_writes]==[(0,4),(4,4),(8,4),(12,1),(16,4),(20,1),(21,1),(88,4)],'Constructor field layout')
    root=WS/'work/client-reference/item-ownership455';root.mkdir(parents=True,exist_ok=True)
    initialized=bytearray([0xa5]*92)
    for row in ctor_writes:
        value=0x10203040 if row['offset']==0 else row['value']
        initialized[row['offset']:row['offset']+row['bytes']]=value.to_bytes(row['bytes'],'little')
    source=bytearray((37*i+11)%256 for i in range(92));copied=bytearray([0xcc]*92)
    copied[:4]=(0x55667788).to_bytes(4,'little')
    for offset,size in [(4,4),(8,4),(12,1),(16,4),(20,1),(21,1),(22,64),(88,4)]:
        copied[offset:offset+size]=source[offset:offset+size]
    board=bytearray((31*i+7)%256 for i in range(620));board[584:588]=bytes(4)
    board_copy=bytearray([0xdd]*620);board_copy[:4]=(0x90abcdef).to_bytes(4,'little')
    for offset,size in [(4,1),(8,585),(596,21)]:board_copy[offset:offset+size]=board[offset:offset+size]
    fixtures=[]
    for name,data in [('header-initialized.bin',initialized),('header-source.bin',source),('header-copied.bin',copied),
                      ('board-source.bin',board),('board-copied.bin',board_copy)]:
        path=root/name;path.write_bytes(data);fixtures.append(record(path))
    report=dict(status='CONFIRMED_SELECTED',scope='Selected CItem header/copy/refcount and CItemObject release/clone;not full derived factory or ordinary Linker migration',
        references=references,assembly=assemblies,actual_instructions=579,raw_evidence=[record(raw_path)],
        constructor_writes=ctor_writes,fixtures=fixtures,script_sha256=sha(Path(__file__)),
        raw_parser='C6/C7 /0 EAX+disp8 immediate stores only;data decoding,no input code execution',
        copy_oracle='Manually reviewed complete copy-constructor assembly;preserve all destination padding/unwritten fields',
        primary_cache_guard=dict(manager_rva='0x80c020',empty_field_rva='0x80c02c',gesture_manager_rva='0x80bff4'),
        gaps=['Full CItem derived physical/SF/Animus/Gesture/Macro metadata and item factories/managers are not ported',
              'Opaque CResObject fields copy as bytes;their render/clear/destructor side effects remain required',
              'Production ownership host and ordinary Linker/board/hover/GUI consumers remain unbound',
              'Allocator failures tested as selected null returns,not full C++ exception/OOM/unwind equivalence'],
        input_exe_executed=False,server_modified=False,M6='OPEN',M6F='OPEN',M7='OPEN',M9='OPEN')
    (WS/'inventory/client455-item-ownership-reference.json').write_text(json.dumps(report,indent=2)+'\n')
    print('CONFIRMED_SELECTED:24equalranges/579asm/8decodedctorstores;ordinary ownership integration OPEN')


if __name__=='__main__':main()
