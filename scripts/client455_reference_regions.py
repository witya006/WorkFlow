"""Validate complete selected CFG/disassembly evidence against both455pins."""
import hashlib,json
from compare_client_binaries import WS,pe
from build_client455_x87_math import read_va

def verify_regions(raw_file):
    raw=json.loads(raw_file.read_text());functions=[]
    for entry in raw['ranges']['result']:
        assert entry['fn'] and not entry['error'];addr=int(entry['fn']['addr'],16)
        pages=raw['asm'][entry['query']];assert pages[-1]['cursor']['done']
        lines=[line for page in pages for line in page['asm']['lines']]
        starts={int(line['addr'],16) for line in lines};assert len(starts)==len(lines)==pages[0]['total_instructions']
        assert all(len(page['asm']['lines'])<=100 for page in pages)
        cfg=next(c for c in raw['cfg']['result'] if int(c['addr'],16)==addr)
        assert cfg['cursor']['done'] and cfg['count']==cfg['total_blocks']
        blocks=sorted((b for b in cfg['blocks'] if b['size']>0),key=lambda b:int(b['start'],16))
        assert all(int(b['start'],16) in starts for b in blocks)
        assert all(any(int(b['start'],16)<=a<int(b['end'],16) for b in blocks) for a in starts)
        regions=[]
        for block in blocks:
            a,b=int(block['start'],16),int(block['end'],16);assert b-a==block['size']
            if regions and regions[-1][1]==a:regions[-1][1]=b
            else:regions.append([a,b])
        functions.append(dict(rva=hex(addr-0x400000),instructions=len(lines),positive_cfg_blocks=len(blocks),regions=[dict(rva=hex(a-0x400000),bytes=b-a) for a,b in regions]))
    pins=json.loads((WS/'config/client-target.json').read_text());references=[]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';binary=path.read_bytes();digest=hashlib.sha256(binary).hexdigest()
        assert digest==pins[key]['sha256'] and pe(binary)['architecture']=='x86'
        for row in raw['asm'].values():
            for page in row:
                for line in page['asm']['lines']:
                    if 'bytes' in line:assert read_va(binary,int(line['addr'],16),len(bytes.fromhex(line['bytes'])))==bytes.fromhex(line['bytes'])
        confirmed=[dict(f,regions=[dict(r,sha256=hashlib.sha256(read_va(binary,0x400000+int(r['rva'],16),r['bytes'])).hexdigest()) for r in f['regions']]) for f in functions]
        references.append(dict(file=path.relative_to(WS).as_posix(),sha256=digest,architecture='x86',image_base='0x400000',functions=confirmed))
    assert references[0]['functions']==references[1]['functions']
    return dict(references=references,full_functions=len(functions),full_instructions=sum(f['instructions'] for f in functions),positive_cfg_blocks=sum(f['positive_cfg_blocks'] for f in functions))
