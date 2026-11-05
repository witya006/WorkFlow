"""Pin draw contracts and a small connected animated model/texture fixture."""
import hashlib,json,struct
from pathlib import Path
from compare_client_binaries import WS
from build_client455_x87_math import read_va
from mesh08 import decode

def sha(data):return hashlib.sha256(data).hexdigest()
def main():
    target=json.loads((WS/'config/client-target.json').read_text(encoding='utf-8'));references=[];previous=None
    ranges=[('draw_state',0x91cde0,0x33c),('palette',0x91d120,0x200),('shader_selection',0x91fb90,0x70),('material_constants',0x92d830,0x34),('shared_draw_caller',0x92e140,0x4a9),('full_main_draw',0x92e5f0,0x1590),('matrix_multiply',0x934d60,0x15)]
    for folder,label in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        raw=(WS/f'work/client-reference/{folder}/RF_Online.bin').read_bytes()
        if sha(raw)!=target[label]['sha256']:raise ValueError('Changed reference455')
        bodies=[{'name':name,'rva':hex(at-0x400000),'bytes':size,'sha256':sha(read_va(raw,at,size))} for name,at,size in ranges]
        if previous is not None and previous!=bodies:raise ValueError('Draw contracts differ')
        previous=bodies;references.append({'sha256':sha(raw),'architecture':'x86','image_base':'0x400000','functions':bodies})
    pairs=json.loads((WS/'inventory/character-mesh08-bone-pairs.json').read_text(encoding='utf-8'));pair=9;sample=pairs['samples'][pair]
    animation=json.loads((WS/'inventory/client455-animation-reference.json').read_text(encoding='utf-8'));ani=next(r for r in animation['samples'] if r['pair_index']==pair)
    root=WS/'work/client-reference/draw455';root.mkdir(parents=True,exist_ok=True);files=[]
    for path,digest in [(sample['mesh'],sample['mesh_sha256']),(f'work/client-reference/character-legacy-runtime/real_{pair:02}.bn',sample['skeleton_sha256']),(ani['copy'],ani['sha256'])]:
        if sha((WS/path).read_bytes())!=digest:raise ValueError('Changed connected input')
        files.append({'path':path,'sha256':digest})
    fixture=root/'model.txt';fixture.write_text('\n'.join(str(WS/r['path']) for r in files)+'\n',encoding='ascii')
    model=decode((WS/sample['mesh']).read_bytes());wanted={name.replace(b'/',b'\\').rsplit(b'\\',1)[-1].upper() for p in model.parts for name in [p.primary_texture,p.secondary_texture] if name}
    install=Path(json.loads((WS/'config/paths.json').read_text(encoding='utf-8'))['client_455']);directory=install/'Character/Monster/Tex';textures=[];remaining=set(wanted)
    for original in directory.iterdir():
        if not original.is_file() or original.name.upper().encode('ascii') not in remaining:continue
        raw=original.read_bytes();out=root/'tex'/original.name;out.parent.mkdir(exist_ok=True)
        if out.exists() and out.read_bytes()!=raw:raise ValueError('Preserve changed texture fixture')
        out.write_bytes(raw);textures.append({'copy':out.relative_to(WS).as_posix(),'sha256':sha(raw),'original':original.relative_to(install).as_posix(),'requested':original.name.upper(),'bytes':len(raw)});remaining.remove(original.name.upper().encode('ascii'))
    # Read only each RFS index, then only requested members. No whole-corpus dump.
    for archive in sorted(directory.glob('*.RFS')):
        with archive.open('rb') as stream:
            word=stream.read(4)
            if len(word)!=4:continue
            count=struct.unpack('<I',word)[0]
            if count>(archive.stat().st_size-4)//64:raise ValueError('Invalid texture index')
            entries=stream.read(count*64)
            for i in range(count):
                name=entries[i*64:i*64+56].split(b'\0',1)[0]
                requested=next((r for r in remaining if name.upper() in [r,r.rsplit(b'.',1)[0]+b'.RFT',r.rsplit(b'.',1)[0]+b'.RFC']),None)
                if requested is None:continue
                offset,size=struct.unpack_from('<II',entries,i*64+56);stream.seek(offset);raw=stream.read(size)
                if len(raw)!=size:raise ValueError('Short texture member')
                out=root/'tex'/name.decode('ascii');out.parent.mkdir(exist_ok=True)
                if out.exists() and out.read_bytes()!=raw:raise ValueError('Preserve changed texture fixture')
                out.write_bytes(raw);textures.append({'copy':out.relative_to(WS).as_posix(),'sha256':sha(raw),'archive':archive.relative_to(install).as_posix(),'member':name.decode('ascii'),'requested':requested.decode('ascii'),'offset':offset,'bytes':size});remaining.remove(requested)
        if not remaining:break
    if remaining:raise ValueError('Missing selected model textures:'+repr(sorted(remaining)))
    report={'scope':'Recovered state/palette/shared draw contracts and one connected real animated model;full draw routing remains open','references':references,'files':files,'fixture':fixture.relative_to(WS).as_posix(),'fixture_sha256':sha(fixture.read_bytes()),'pair_index':pair,'skeleton_original':sample['skeleton_original'],'parts':len(model.parts),'textures':textures,'script_sha256':sha(Path(__file__).read_bytes()),'limits':['Draw primitives are source,full92E5F0/effects/queues/CPU fallback/normal integration still open','Reference EXE is never executed;GPU run is source integration evidence,not original frame equivalence']}
    (WS/'inventory/client455-draw-reference.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(f'PASS:7pinned ranges;one real animated model/{len(model.parts)}parts/{len(textures)}textures')
if __name__=='__main__':main()
