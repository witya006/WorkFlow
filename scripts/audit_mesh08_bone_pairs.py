"""Pin real mesh/skeleton pairs and independent first-match binding expectations.

Same-basename pair selection is a fixture choice, not proof of the client's asset
selection rules. These tests cover binding given those two arrays, not loading it.
"""
import hashlib,json,ntpath,shutil,struct
from pathlib import Path
from compare_client_binaries import WS
from mesh08 import decode
from audit_character_init455 import legacy_extent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def basename(raw):
    if b'\0' not in raw:raise ValueError('Unterminated fixture name')
    value=raw.split(b'\0',1)[0]
    if any(x>=128 for x in value):raise ValueError('Non-ASCII fixture name needs locale verification')
    return ntpath.basename(value)
def plain_names(data):
    extent=legacy_extent(data)
    if not extent['accepted']:raise ValueError('Paired skeleton is not exact plain framing')
    at=2;names=[]
    for record in extent['records']:
        head=data[at:at+693];names.append(basename(head[:100]));at+=693+28*record['vertices']+88*record['faces']
        if record['compact']:
            at+=4
            if record['bones']:at+=100*record['bones']+40*record['physiques']
        else:at+=424*record['physiques']
    if at!=len(data):raise ValueError('Skeleton fixture cursor mismatch')
    return names
def first(names,name):
    try:return names.index(name)
    except ValueError:return None
def token(external,local,name):
    index=first(external,name)
    if index is not None:return index+1
    index=first(local,name)
    return -(index+1) if index is not None else 0
def main():
    corpus=json.loads((WS/'inventory/character-mesh08-corpus.json').read_text(encoding='utf-8'))
    paths=json.loads((WS/'config/paths.json').read_text(encoding='utf-8'));root=Path(paths['client_455'])
    destination=WS/'work/client-reference/character-models/mesh08-bones';destination.mkdir(parents=True,exist_ok=True)
    golden=bytearray(b'M8BG'+struct.pack('<II',1,len(corpus['samples'])));samples=[];meshTotal=boneTotal=missingTotal=maxSelected=0
    def number(value):golden.extend(struct.pack('<I',value&0xffffffff))
    def string(value):golden.extend(struct.pack('<H',len(value)));golden.extend(value)
    for index,sample in enumerate(corpus['samples'],1):
        model=WS/sample['copy']
        if sha(model)!=sample['sha256']:raise ValueError('Pinned mesh changed')
        sourcePath=Path(sample['original_relative']);bone=root/sourcePath.parent.parent/'Bone'/sourcePath.with_suffix('.bn').name
        copy=destination/f'skeleton_{index:03}.bn';digest=sha(bone)
        if copy.exists() and sha(copy)!=digest:raise ValueError('Preserving changed skeleton fixture')
        if not copy.exists():shutil.copyfile(bone,copy)
        external=plain_names(copy.read_bytes());mesh=decode(model.read_bytes());local=[basename(p.header[:100]) for p in mesh.parts]
        string(model.relative_to(WS).as_posix().encode('ascii'));number(len(external))
        for name in external:string(name)
        number(len(local));selectedTotal=missing=maximum=0
        for part,name in zip(mesh.parts,local):
            parent=basename(part.header[100:200]);parentToken=token(external,local,parent)
            selected=[];misses=0
            for r in range(part.bone_count):
                influences=struct.unpack_from('<i',part.bones,404*r)[0]
                if influences>4:raise ValueError('Unsafe influence fixture')
                for b in range(max(0,influences)):
                    field=part.bones[404*r+4+100*b:404*r+104+100*b]
                    if b'\0' not in field:raise ValueError('Unterminated influence fixture')
                    query=field.split(b'\0',1)[0];found=token(external,local,query)
                    if not found:misses+=1
                    elif found not in selected:selected.append(found)
            if len(selected)>50:raise ValueError('Fixture beyond source safety domain')
            string(name);string(parent);number(parentToken);number(len(selected))
            for selectedToken in selected:number(selectedToken)
            number(misses);selectedTotal+=len(selected);missing+=misses;maximum=max(maximum,len(selected))
        samples.append({'mesh':sample['copy'],'mesh_sha256':sample['sha256'],'skeleton_original':bone.relative_to(root).as_posix(),'skeleton_copy':copy.relative_to(WS).as_posix(),'skeleton_sha256':digest,'meshes':len(local),'skeleton_meshes':len(external),'resolved_per_mesh_total':selectedTotal,'missing_influence_occurrences':missing,'max_resolved_per_mesh':maximum})
        meshTotal+=len(local);boneTotal+=len(external);missingTotal+=missing;maxSelected=max(maxSelected,maximum)
    output=destination/'golden.bin';output.write_bytes(golden)
    report={'scope':'12same-basename real mesh/skeleton fixtures;source binding inputs,not proof of runtime asset selection/full skeleton loading','samples':samples,'mesh_count':meshTotal,'skeleton_mesh_count':boneTotal,'missing_influence_occurrences':missingTotal,'max_resolved_per_mesh':maxSelected,'golden':output.relative_to(WS).as_posix(),'golden_sha256':sha(output),'corpus_report_sha256':sha(WS/'inventory/character-mesh08-corpus.json'),'script_sha256':sha(Path(__file__)),'limits':['ASCII fixture basename extraction only;CRT path/locale edge domains open','No source transforms/animation/material/GPU/shared buffer/full model loader integration']}
    (WS/'inventory/character-mesh08-bone-pairs.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(f'PASS:pinned{len(samples)}real mesh/skeleton pairs;{meshTotal}meshes/{boneTotal}skeleton records,max{maxSelected}resolved/mesh,{missingTotal}missing occurrences.')
if __name__=='__main__':main()
