"""Freeze real inputs and independent valid-input geometry/binding expectations."""
import hashlib,json,math,ntpath,shutil,struct
from pathlib import Path
from compare_client_binaries import WS
from audit_character_init455 import legacy_extent
from audit_client455_legacy_models import expand

def sha(data):return hashlib.sha256(data).hexdigest()
def quiet(bits):return bits|0x400000 if bits&0x7f800000==0x7f800000 and bits&0x7fffff else bits
def name(raw):
    if b'\0' not in raw:raise ValueError('Unterminated fixture field')
    value=raw.split(b'\0',1)[0]
    if any(x>=128 for x in value):raise ValueError('Non-ASCII fixture needs locale evidence')
    return ntpath.basename(value)
def parse(raw):
    extent=legacy_extent(raw)
    if not extent['accepted']:raise ValueError('Not complete legacy framing')
    parts=[];at=2
    for p in extent['records']:
        h=raw[at:at+693];at+=693;v=raw[at:at+28*p['vertices']];at+=len(v);f=raw[at:at+88*p['faces']];at+=len(f);ph=b''
        if p['compact']:
            n=struct.unpack_from('<I',raw,at)[0];at+=4
            if n:
                names=raw[at:at+100*n];at+=len(names);compact=raw[at:at+40*p['physiques']];at+=len(compact);ph=expand(compact,names,0)
        else:ph=raw[at:at+424*p['physiques']];at+=len(ph)
        parts.append({'header':h,'vertices':v,'faces':f,'physique':ph,'counts':p})
    if at!=len(raw):raise ValueError('Fixture parser mismatch')
    return parts
def geometry(part,mtg):
    p=part['counts'];vertices=[]
    for i in range(p['vertices']):
        v=bytearray(64);source=part['vertices'][28*i:28*i+28]
        for at in [0,4,8]:struct.pack_into('<I',v,at,quiet(struct.unpack_from('<I',source,at)[0]))
        for at in [16,20,24]:struct.pack_into('<I',v,at+16,quiet(struct.unpack_from('<I',source,at)[0])^0x80000000)
        struct.pack_into('<I',v,12,0x3f800000);vertices.append(v)
    ph=part['physique'];names=[]
    for i in range(len(ph)//424):
        count=struct.unpack_from('<i',ph,424*i+4)[0]
        if count>4:raise ValueError('Unsafe fixture influence count')
        for b in range(max(0,count)):
            value=ph[424*i+8+100*b:424*i+108+100*b].split(b'\0',1)[0]
            if value not in names:names.append(value)
    for i in range(len(ph)//424):
        index,count=struct.unpack_from('<ii',ph,424*i);v=vertices[index];v[12:32]=bytes(20)
        for b in range(max(0,count)):
            value=ph[424*i+8+100*b:424*i+108+100*b].split(b'\0',1)[0];struct.pack_into('<H',v,24+2*b,names.index(value))
            if b<3:struct.pack_into('<I',v,12+4*b,quiet(struct.unpack_from('<I',ph,424*i+408+4*b)[0]))
    out=bytearray()
    for f in range(p['faces']):
        face=part['faces'][88*f:88*f+88]
        for corner in range(3):
            v=bytearray(vertices[struct.unpack_from('<I',face,4*corner)[0]])
            u,w=struct.unpack_from('<II',face,48+12*corner);vf=struct.unpack('<f',struct.pack('<I',w))[0]
            if not math.isfinite(vf):raise ValueError('Nonfinite UV fixture needs separate FP oracle')
            struct.pack_into('<I',v,44,quiet(u));struct.pack_into('<f',v,48,1.0-vf)
            if mtg is not None:
                for j in range(3):struct.pack_into('<I',v,52+4*j,quiet(struct.unpack_from('<I',mtg,84*f+28*corner+4*j)[0]))
            out+=v
    unique=[];indices=[];lookup={}
    for i in range(len(out)//64):
        v=bytes(out[64*i:64*i+64])
        if v not in lookup:lookup[v]=len(unique);unique.append(v)
        indices.append(lookup[v])
    return bytes(out),b''.join(unique),indices

def scene(compact=False,influences=4):
    raw=bytearray(struct.pack('<H',3));dictionary=[b'BONE Root',b'Bip01 Spine1'];mtg=bytearray()
    for n,mesh in enumerate([b'BONE Root',b'Bip01 Spine1',b'Bip01 Ponytail L1']):
        h=bytearray(693);h[:len(mesh)]=mesh;parent=b'' if n==0 else dictionary[n-1 if n<2 else 1];h[100:100+len(parent)]=parent
        for at in [200,264,328]:
            for i in range(16):struct.pack_into('<f',h,at+4*i,1.0 if i%5==0 else 0.0)
        for i in [0,5,10]:struct.pack_into('<f',h,200+4*i,float(n+2))
        struct.pack_into('<3f',h,200+48,float(n+1),2.0,3.0);struct.pack_into('<I',h,642,int(compact))
        vertices=bytearray();faces=bytearray();ph=bytearray()
        if n==2:
            struct.pack_into('<HHH',h,392,3,2,3)
            for i in range(3):
                vertices+=struct.pack('<3fI3f',float(i),float(i+1),-float(i),99,0.0,0.0,1.0)
                p=bytearray(424);struct.pack_into('<ii',p,0,i,influences)
                for b in range(influences):p[8+100*b:8+100*b+len(dictionary[b%2])]=dictionary[b%2];struct.pack_into('<f',p,408+4*b,0.25 if influences>2 else 0.5)
                ph+=p
            for f in range(2):
                face=bytearray(88);struct.pack_into('<3I',face,0,0,1,2)
                for c in range(3):struct.pack_into('<2f',face,48+12*c,c*0.25,c*0.125)
                faces+=face
                for c in range(3):mtg+=struct.pack('<7I',0x7f800123 if compact and f==0 and c==0 else struct.unpack('<I',struct.pack('<f',0.25*(f+c+1)))[0],0x80000000,0x3f800000,0,0,0,0)
        raw+=h+vertices+faces
        if compact:
            raw+=struct.pack('<I',2 if n==2 else 0)
            if n==2:
                raw+=b''.join(v.ljust(100,b'\0') for v in dictionary)
                for i in range(3):raw+=struct.pack('<Ii4I4f',i,influences,0,1,0,1,*([0.25]*4 if influences>2 else [0.5,0.5,0,0]))
        else:raw+=ph
    return bytes(raw),bytes(mtg)

def main():
    root=WS/'work/client-reference/character-legacy-runtime';root.mkdir(parents=True,exist_ok=True);inputs=[]
    refs=json.loads((WS/'inventory/client455-legacy-runtime-reference.json').read_text(encoding='utf-8'));pairs=json.loads((WS/'inventory/character-mesh08-bone-pairs.json').read_text(encoding='utf-8'));paths=json.loads((WS/'config/paths.json').read_text(encoding='utf-8'));client=Path(paths['client_455'])
    originals=[(s['skeleton_copy'],s['skeleton_sha256'],s['skeleton_original'],'real_bn') for s in pairs['samples']]+[(s['copy'],s['sha256'],s['original_relative'],'real_mesh') for s in refs['real_legacy_meshes']]
    for i,(copy,digest,original,kind) in enumerate(originals):
        raw=(WS/copy).read_bytes()
        if sha(raw)!=digest:raise ValueError('Pinned input changed')
        target=root/f'real_{i:02}{Path(original).suffix}';target.write_bytes(raw);sidecar=client/Path(original).with_suffix('.mtg');mtg=None
        if sidecar.is_file():mtg=sidecar.read_bytes();target.with_suffix('.mtg').write_bytes(mtg)
        elif target.with_suffix('.mtg').exists():raise ValueError('Unexpected stale real MTG')
        inputs.append((target,raw,mtg,kind))
    for label,compact,influences,with_mtg in [('scene_plain',False,4,True),('scene_compact',True,4,True),('scene_two',False,2,False)]:
        raw,mtg=scene(compact,influences);target=root/(label+'.msh');target.write_bytes(raw)
        if with_mtg:target.with_suffix('.mtg').write_bytes(mtg)
        inputs.append((target,raw,mtg if with_mtg else None,'synthetic'))
    golden=bytearray(b'LR45'+struct.pack('<II',1,len(inputs)));manifest=[];total=0
    def string(value):golden.extend(struct.pack('<H',len(value)));golden.extend(value)
    for source,raw,mtg,kind in inputs:
        ps=parse(raw);names=[name(p['header'][:100]) for p in ps];string(source.relative_to(WS).as_posix().encode('ascii'));golden+=struct.pack('<III',len(ps),int(mtg is not None),struct.unpack_from('<I',ps[-1]['header'],642)[0] if ps else 0);mtg_at=0
        for p in ps:
            h=p['header'];parent=name(h[100:200]);string(name(h[:100]));string(parent);golden+=struct.pack('<I',names.index(parent)+1 if parent in names else 0)+h
            selected=[];missing=0
            for r in range(len(p['physique'])//424):
                count=struct.unpack_from('<i',p['physique'],424*r+4)[0]
                for b in range(max(0,count)):
                    query=p['physique'][424*r+8+100*b:424*r+108+100*b].split(b'\0',1)[0]
                    token=names.index(query)+1 if query in names else 0
                    if token and token not in selected:selected.append(token)
                    elif not token:missing+=1
            golden+=struct.pack('<II',len(selected),missing)+b''.join(struct.pack('<I',t) for t in selected)
            tangents=None
            if mtg is not None:
                size=84*p['counts']['faces'];tangents=mtg[mtg_at:mtg_at+size];mtg_at+=size
                if len(tangents)!=size:raise ValueError('Short real MTG input')
            expanded,unique,indices=geometry(p,tangents);golden+=struct.pack('<III',len(expanded)//64,len(unique)//64,struct.unpack_from('<i',p['physique'],4)[0] if p['physique'] else 0)+expanded+unique+b''.join(struct.pack('<H',i) for i in indices)
        total+=len(ps);manifest.append({'copy':source.relative_to(WS).as_posix(),'sha256':sha(raw),'kind':kind,'records':len(ps),'mtg':source.with_suffix('.mtg').relative_to(WS).as_posix() if mtg is not None else None,'mtg_sha256':sha(mtg) if mtg is not None else None})
    out=root/'runtime-golden.bin';out.write_bytes(golden);report={'scope':'RealBN+legacyMSH andsynthetic fullconverter inputs/independent geometry/binding expectations;not full clientacceptance','samples':manifest,'parts':total,'golden':out.relative_to(WS).as_posix(),'golden_sha256':sha(golden),'reference_report_sha256':sha((WS/'inventory/client455-legacy-runtime-reference.json').read_bytes()),'script_sha256':sha(Path(__file__).read_bytes()),'limits':['ASCII names/finite real UV;matrix expectations tested usingactual pinned D3DXprovider separately','Nearestfloat32 valid geometry oracle;other FPmodes/NaN covered bynative primitive tests','Fixture pairing notproof ofruntime assetselection']}
    (WS/'inventory/client455-legacy-runtime-inputs.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(f'PASS:{len(inputs)}converter fixtures/{total}parts;realMTG={sum(m is not None for _,_,m,k in inputs if k!="synthetic")}')
if __name__=='__main__':main()
