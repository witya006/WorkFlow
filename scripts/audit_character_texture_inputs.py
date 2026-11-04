"""Pin small real Character textures/RFS andgenerate independent native fixtures."""
import hashlib,json,shutil,struct
from pathlib import Path
from compare_client_binaries import WS
from build_client455_x87_math import read_va
from character_texture import parse_rfs,prepare_dds,synthetic_dds,make_rfs,CharacterTextureError

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def fnv(raw):
    value=2166136261
    for byte in raw:value=((value^byte)*16777619)&0xffffffff
    return value
def main():
    client=Path(json.loads((WS/'config/paths.json').read_text(encoding='utf-8'))['client_455'])
    reference=WS/'work/client-reference/reference-backup/RF_Online.bin'
    if sha(reference)!='46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558':raise ValueError('Reference changed')
    key=read_va(reference.read_bytes(),0xbf83f0,128);root=WS/'work/client-reference/character-textures/fixtures';root.mkdir(parents=True,exist_ok=True);tex=root/'tex';tex.mkdir(exist_ok=True)
    files=[];assets=[];archives=[]
    for name in ['GTT.RFS','TRT.RFS','RFSInfo.dat','GT_A_042.dds','GT_B_003.dds','GT_C_022.dds']:
        source=client/'Character/GuardTower/Tex'/name;copy=tex/name
        if copy.exists() and sha(copy)!=sha(source):raise ValueError('Preserving changed texture fixture')
        if not copy.exists():shutil.copyfile(source,copy)
        files.append({'source':source.relative_to(client).as_posix(),'copy':copy.relative_to(WS).as_posix(),'sha256':sha(copy),'bytes':copy.stat().st_size})
        if name.lower().endswith('.dds'):assets.append((name,copy.read_bytes(),'loose'))
        elif name.lower().endswith('.rfs'):
            raw=copy.read_bytes();container=parse_rfs(raw)
            if container.encode()!=raw:raise ValueError('RFS exact roundtrip changed data')
            records=[]
            for n,e in enumerate(container.entries):
                data=container.member(n);decoded=prepare_dds(data,key)
                records.append({'name':e.name.decode('ascii'),'offset':e.offset,'size':e.size,'sha256':hashlib.sha256(data).hexdigest(),'width':decoded['width'],'height':decoded['height'],'cube':decoded['cube']})
                assets.append((e.name.decode('ascii'),data,name))
            archives.append({'file':name,'entries':records})
    def mask(raw):return bytes(a^b for a,b in zip(raw,key))+raw[128:]
    # Native scratch inputs use newdirectories so negative caching is testable.
    generated={
        'SYNTH.DDS':synthetic_dds(),
        'SYNTH.RFC':mask(synthetic_dds()),
        'CUBE.DDS':synthetic_dds(cube=True),
        'BROKEN.DDS':bytes(192),
    }
    # 2x2uncompressed24-bit BMP:top red/green,bottom blue/white.
    bmp=struct.pack('<2sIHHI',b'BM',70,0,0,54)+struct.pack('<IiiHHIIiiII',40,2,2,1,24,0,16,0,0,0,0)+bytes([255,0,0,255,255,255,0,0,0,0,255,0,255,0,0,0])
    generated['CHECKER.BMP']=bmp
    for name,raw in generated.items():(tex/name).write_bytes(raw)
    for name in ['SYNTH.DDS','SYNTH.RFC','CUBE.DDS','BROKEN.DDS']:assets.append((name,generated[name],'synthetic'))
    growth=root/'growth';growth.mkdir(exist_ok=True)
    growthRaw=make_rfs([(f'TEX_{n:03}.RFT'.encode(),mask(synthetic_dds())) for n in range(50)])
    (growth/'DATA0.RFS').write_bytes(growthRaw)
    duplicate=root/'duplicate';duplicate.mkdir(exist_ok=True)
    (duplicate/'A.RFS').write_bytes(make_rfs([(b'SHARED.RFT',b'first')]))
    (duplicate/'B.RFS').write_bytes(make_rfs([(b'SHARED.RFT',b'second')]))
    (duplicate/'RFSINFO.DAT').write_text('A.RFS\nB.RFS\n',encoding='ascii')
    golden=bytearray(b'T9GX'+struct.pack('<II',1,len(assets)));cases=0;real=0
    for name,raw,origin in assets:
        resource=('.\\tex\\'+name).encode('ascii');golden+=struct.pack('<H',len(resource))+resource+struct.pack('<II',len(raw),fnv(raw));profiles=[(0,2048,2048),(1,2048,2048),(2,2048,2048),(9,255,2048)]
        golden+=struct.pack('<I',len(profiles))
        for lod,w,h in profiles:
            try:p=prepare_dds(raw,key,lod,w,h)
            except CharacterTextureError:p=None
            golden+=struct.pack('<IIII',lod,w,h,int(p is not None))
            if p:golden+=struct.pack('<IIIII',p['skip'],p['width'],p['height'],int(p['cube']),len(p['bytes']))+p['bytes']
            cases+=1
        real+=origin!='synthetic'
    output=root/'golden.bin';output.write_bytes(golden)
    meshes=[]
    models=root/'models';models.mkdir(exist_ok=True)
    corpus=json.loads((WS/'inventory/character-mesh08-corpus.json').read_text(encoding='utf-8'))
    for n in [3,4,5]:
        sample=corpus['samples'][n-1];source=WS/sample['copy'];copy=models/f'model_{n}.msh'
        if sha(source)!=sample['sha256']:raise ValueError('Pinned mesh changed')
        if copy.exists() and sha(copy)!=sample['sha256']:raise ValueError('Preserving changed mesh fixture')
        if not copy.exists():shutil.copyfile(source,copy)
        meshes.append({'copy':copy.relative_to(WS).as_posix(),'sha256':sha(copy),'parts':sample['meshes']})
    manifest=[{'relative':p.relative_to(root).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(root.rglob('*')) if p.is_file()]
    report={'scope':'Small real Character texture corpus:2GuardTower RFS/13members+3looseDDS;not full texture/RFS inventory','fixture_root':root.relative_to(WS).as_posix(),'fixture_files':manifest,'original_files':files,'archives':archives,'real_assets':real,'native_assets':len(assets),'dds_profiles':cases,'golden':output.relative_to(WS).as_posix(),'golden_sha256':sha(output),'meshes':meshes,'mesh_parts':sum(x['parts'] for x in meshes),'python_source_sha256':{name:sha(WS/'scripts'/name) for name in ['character_texture.py','audit_character_texture_inputs.py']},'key_sha256':hashlib.sha256(key).hexdigest(),'limits':['Copied inputs only;fixture model/texture directory pairing not full game asset-selection proof','DDS profiles preserve observed skip/header quirks;physicalGPU verified separately','Malformed input safety is bounded,not reference unchecked read/OOM equivalence']}
    (WS/'inventory/character-texture-inputs.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(f'PASS:2real RFS/13members+3loose DDS,{cases}DDS profiles/{len(assets)}assets;3real meshes/{report["mesh_parts"]}parts pinned.')
if __name__=='__main__':main()
