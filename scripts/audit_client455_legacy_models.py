"""Pin the intermediate legacy MSH/BN reader and produce independent field goldens."""
import hashlib,json,struct
from pathlib import Path
from compare_client_binaries import WS
from build_client455_x87_math import read_va
from audit_character_init455 import legacy_extent

FUNCTIONS=[('part_ctor',0x93c020,0x23),('part_dtor',0x91c270,0x86),
           ('import_release',0x91fb20,0x63),('legacy_reader',0x93c2f0,0x470),
           ('raw_thunk',0x93c760,5),('file_importer_pending',0x93c770,0x123),
           ('runtime_converter_pending',0x93cd60,0x1083)]
POINTERS=[696,700,704,716,712]
def sha(data):return hashlib.sha256(data).hexdigest()

def expand(compact,names,fill=0xa5):
    output=bytearray([fill])*(len(compact)//40*424)
    for i in range(len(compact)//40):
        source=compact[40*i:40*i+40];at=424*i;output[at:at+8]=source[:8]
        count=struct.unpack_from('<i',source,4)[0]
        if count>4:raise ValueError('Fixture outside bounded influence domain')
        for n in range(max(0,count)):
            index=struct.unpack_from('<I',source,8+4*n)[0]
            name=names[100*index:100*(index+1)]
            if len(name)!=100:raise ValueError('Invalid fixture name index')
            copied=name[:99].split(b'\0',1)[0];output[at+8+100*n:at+108+100*n]=copied.ljust(100,b'\0')
            bits=struct.unpack_from('<I',source,24+4*n)[0]
            if bits&0x7f800000==0x7f800000 and bits&0x7fffff:bits|=0x400000
            struct.pack_into('<I',output,at+408+4*n,bits)
    return bytes(output)

def expected(data):
    extent=legacy_extent(data)
    if not extent['accepted']:raise ValueError('Golden needs complete plain framing')
    at=2;parts=[]
    for counts in extent['records']:
        header=data[at:at+693];at+=693;record=bytearray([0xa5])*720;record[:693]=header
        for offset in POINTERS:struct.pack_into('<I',record,offset,0)
        v=28*counts['vertices'];f=88*counts['faces'];p=counts['physiques'];blocks=[data[at:at+v],data[at+v:at+v+f],None,None,None];at+=v+f
        if counts['compact']:
            n=struct.unpack_from('<I',data,at)[0];at+=4;struct.pack_into('<I',record,708,n)
            if n:
                names=data[at:at+100*n];at+=100*n;compact=data[at:at+40*p];at+=40*p
                blocks[2:]=[expand(compact,names),compact,names]
        elif p:blocks[2]=data[at:at+424*p];at+=424*p
        parts.append((bytes(record),blocks))
    if at!=len(data):raise ValueError('Fixture cursor mismatch')
    resource=bytearray([0xa5])*28;struct.pack_into('<H',resource,2,len(parts))
    for offset in [4,12,20]:struct.pack_into('<I',resource,offset,0)
    if parts:struct.pack_into('<I',resource,24,extent['records'][-1]['compact'])
    return bytes(resource),parts

def synthetic():
    def part(v,f,p,compact,tail):
        h=bytearray((i*17+3)&255 for i in range(693));struct.pack_into('<HHH',h,392,v,f,p);struct.pack_into('<I',h,642,compact)
        return h+bytes((i*13+9)&255 for i in range(28*v+88*f))+tail
    plain=bytearray((i*11)&255 for i in range(424));struct.pack_into('<i',plain,4,5) # copied, not expanded
    names=b'A\0'+b'z'*98+b'B'*100
    compact=bytearray(80);struct.pack_into('<Ii4I4I',compact,0,7,4,0,1,0,1,0x3f800001,0x80000000,0x7f800123,0xff800001);struct.pack_into('<Ii',compact,40,9,-1)
    return [('plain',b'\x01\0'+part(2,1,1,0,plain)),
            ('compact',b'\x01\0'+part(1,2,2,1,struct.pack('<I',2)+names+compact)),
            ('compact_zero_dictionary',b'\x01\0'+part(0,0,3,1,bytes(4))),
            ('compact_empty_physique',b'\x01\0'+part(0,0,0,1,struct.pack('<I',2)+names)),
            ('empty',bytes(2))]

def main():
    pins=json.loads((WS/'config/client-target.json').read_text(encoding='utf-8'));references=[];previous=None
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        raw=(WS/f'work/client-reference/{folder}/RF_Online.bin').read_bytes()
        if sha(raw)!=pins[key]['sha256']:raise ValueError('Pinned PE changed')
        functions=[{'name':name,'rva':hex(va-0x400000),'bytes':size,'sha256':sha(read_va(raw,va,size))} for name,va,size in FUNCTIONS]
        if previous is not None and previous!=functions:raise ValueError('Legacy reader bodies differ between pins')
        previous=functions;references.append({'sha256':sha(raw),'architecture':'x86','image_base':'0x400000','functions':functions})
    pairs=json.loads((WS/'inventory/character-mesh08-bone-pairs.json').read_text(encoding='utf-8'));samples=[]
    for sample in pairs['samples']:
        source=WS/sample['skeleton_copy'];raw=source.read_bytes()
        if sha(raw)!=sample['skeleton_sha256']:raise ValueError('Pinned BN changed')
        samples.append((source,raw,'real_bn'))
    root=WS/'work/client-reference/character-legacy-models';root.mkdir(parents=True,exist_ok=True)
    for name,raw in synthetic():
        source=root/(name+'.bin');source.write_bytes(raw);samples.append((source,raw,'synthetic'))
    golden=bytearray(b'LGBN'+struct.pack('<II',1,len(samples)));records=[];part_total=0;nonempty=0
    for source,raw,kind in samples:
        resource,parts=expected(raw);path=source.relative_to(WS).as_posix().encode('ascii');golden+=struct.pack('<H',len(path))+path+struct.pack('<I',len(raw))+resource
        for record,blocks in parts:
            golden+=record
            for block in blocks:
                golden+=struct.pack('<I',0xffffffff if block is None else len(block))
                if block is not None:golden+=block
        extent=legacy_extent(raw);records.append({'copy':source.relative_to(WS).as_posix(),'sha256':sha(raw),'kind':kind,'bytes':len(raw),'records':extent['mesh_count'],'compact_records':sum(bool(x['compact']) for x in extent['records']),'vertices':sum(x['vertices'] for x in extent['records']),'faces':sum(x['faces'] for x in extent['records']),'physiques':sum(x['physiques'] for x in extent['records'])});part_total+=len(parts);nonempty+=sum(x['vertices'] or x['faces'] for x in extent['records'])
    destination=root/'golden.bin';destination.write_bytes(golden)
    report={'scope':'Intermediate legacy MSH/BN parser/part lifetime;file importer/runtime converter still pending','references':references,'samples':records,'parts':part_total,'nonempty_geometry_records':nonempty,'golden':destination.relative_to(WS).as_posix(),'golden_sha256':sha(golden),'allocator_test_fill':165,'pair_report_sha256':sha((WS/'inventory/character-mesh08-bone-pairs.json').read_bytes()),'script_sha256':sha(Path(__file__).read_bytes()),'limits':['Plain header/payload oracle uses previously checked independent Python framing;compact name/weight expansion modeled from separately pinned instructions','Unwritten fields are allocator-dependent;A5 used only by owned test allocator','Bounded count/influence/index/short-read/nullallocation cleanup is ownpolicy,not unchecked AV/OOM/exception equivalence','No full BNruntime matrices/vertex conversion/material/GPU/animation ornormal dispatcher integration','Raw artifacts/character-legacy455;owned926983beclosed/save;no referenceEXE run']}
    (WS/'inventory/client455-legacy-models-reference.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(f'PASS:{len(samples)}legacy fixtures/{part_total}records,7pinned bodies;golden ready')
if __name__=='__main__':main()
