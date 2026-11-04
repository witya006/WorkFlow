"""Read-only loose-model MESH08 inventory and lossless/native fixture preparation."""
import hashlib,json,shutil,struct
from pathlib import Path
from compare_client_binaries import WS
from mesh08 import decode,describe,Mesh08Error,MAGIC

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def fnv(data):
    value=2166136261
    for byte in data:value=((value^byte)*16777619)&0xffffffff
    return value

def main():
    paths=json.loads((WS/'config/paths.json').read_text(encoding='utf-8'));client=Path(paths['client_455'])
    candidates=sorted(p for p in client.rglob('*') if p.is_file() and p.suffix.lower() in {'.msh','.bn'})
    records=[];other=0;errors=[];total_size=0;totals={'meshes':0,'vertices':0,'indices':0,'bone_records':0};limit_errors=0
    for index,p in enumerate(candidates,1):
        with p.open('rb') as stream:prefix=stream.read(8)
        if not prefix.startswith(MAGIC):other+=1;continue
        raw=p.read_bytes();relative=p.relative_to(client).as_posix();digest=hashlib.sha256(raw).hexdigest();total_size+=len(raw)
        try:
            model=decode(raw,enforce_index_limit=False)
            if model.encode()!=raw:raise ValueError('Lossless MESH08 round trip changed input')
            info=describe(model);too_large=any(part.index_count>64000 for part in model.parts);limit_errors+=int(too_large)
            for name in totals:totals[name]+=info[name]
            records.append({'relative':relative,'bytes':len(raw),'sha256':digest,'runtime_index_limit_ok':not too_large,**info})
        except (Mesh08Error,ValueError) as exc:errors.append({'relative':relative,'bytes':len(raw),'sha256':digest,'error':str(exc)})
        if index%500==0:print(f'Model audit:{index}/{len(candidates)},MESH08decoded{len(records)},errors{len(errors)}',flush=True)
    artifacts=WS/'artifacts/character-mesh08';artifacts.mkdir(parents=True,exist_ok=True)
    full=artifacts/'corpus.json';full.write_text(json.dumps({'scope':'Loose MSH/BN files only;other signatures are not identified by this audit','records':records,'errors':errors},indent=2)+'\n',encoding='utf-8')
    valid=[r for r in records if r['runtime_index_limit_ok']];selected=[];seen=set()
    def choose(record):
        if record and record['sha256'] not in seen:seen.add(record['sha256']);selected.append(record)
    choose(next((r for r in valid if r['relative'].endswith('ACCRETIA_ARMOR_LSHIELD_065.msh')),None))
    for key in ['bone_records','vertices','indices','meshes','bytes']:
        choose(max(valid,key=lambda r:r[key],default=None))
    for group in ['Character/','item/Armor/','item/Shield/','item/Weapon/']:
        choose(next((r for r in valid if r['relative'].lower().startswith(group.lower()) and r['bone_records']),None))
    for record in valid:
        if len(selected)>=12:break
        choose(record)
    fixtures=WS/'work/client-reference/character-models/mesh08-native';fixtures.mkdir(parents=True,exist_ok=True)
    golden=bytearray(b'M8FX'+struct.pack('<II',1,len(selected)));samples=[]
    for n,record in enumerate(selected,1):
        source=client/record['relative'];raw=source.read_bytes()
        if hashlib.sha256(raw).hexdigest()!=record['sha256']:raise ValueError('Model changed during audit')
        name=f'sample_{n:03d}.msh';copy=fixtures/name
        if copy.exists() and sha(copy)!=record['sha256']:raise ValueError('Preserving changed native model copy')
        if not copy.exists():shutil.copyfile(source,copy)
        model=decode(raw);encoded=name.encode('ascii')
        golden+=struct.pack('<H',len(encoded))+encoded+struct.pack('<IHI I',len(raw),len(model.parts),model.consumed,fnv(raw))
        for part in model.parts:
            golden+=struct.pack('<11I',part.offset,part.vertex_offset,part.index_offset,part.bone_offset,part.vertex_count,part.index_count,part.bone_count,fnv(part.header),fnv(part.vertices),fnv(part.indices),fnv(part.bones))
        samples.append({'original_relative':record['relative'],'copy':copy.relative_to(WS).as_posix(),'sha256':record['sha256'],'bytes':len(raw),'meshes':record['meshes'],'vertices':record['vertices'],'indices':record['indices'],'bone_records':record['bone_records']})
    output=fixtures/'golden.bin';output.write_bytes(golden)
    summary={'scope':'Read-only installed loose .msh/.bn files;not archived/RFS models or full client resource inventory','candidate_files':len(candidates),'mesh08_files':len(records)+len(errors),'decoded_files':len(records),'other_prefix_files':other,'framing_errors':errors,
        'mesh08_bytes':total_size,'totals':totals,'runtime_index_limit_exceeded_files':limit_errors,'trailing_byte_files':sum(r['trailing_bytes']!=0 for r in records),
        'out_of_range_index_files':sum(any(p['out_of_range_indices'] for p in r['parts']) for r in records),'influence_count_over4_files':sum(any(p['influence_count_over4'] for p in r['parts']) for r in records),
        'corpus':full.relative_to(WS).as_posix(),'corpus_sha256':sha(full),'samples':samples,'native_golden':output.relative_to(WS).as_posix(),'native_golden_sha256':sha(output),'python_parser_sha256':sha(WS/'scripts/mesh08.py'),
        'limits':['Framing/byte preservation only;runtime texture/material/bone resolution andGPU not implemented here','Bounded reader safety errors differ from unchecked reference malformed/OOM behavior']}
    (WS/'inventory/character-mesh08-corpus.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:summary[k] for k in ['candidate_files','mesh08_files','decoded_files','other_prefix_files','mesh08_bytes','totals','runtime_index_limit_exceeded_files','trailing_byte_files','out_of_range_index_files','influence_count_over4_files']}))
    if errors:raise ValueError('Unresolved MESH08 framing errors;see corpus evidence')

if __name__=='__main__':main()
