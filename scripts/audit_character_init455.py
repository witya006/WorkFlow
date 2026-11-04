"""Pin455vertex/MSH08 paths and representative resources; do not run a game."""
import hashlib,json,shutil,struct
from pathlib import Path
from compare_client_binaries import WS
from build_client455_x87_math import read_va
from export_character_analysis import coff_function_records
from coff_source_bindings import BINDINGS

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def legacy_extent(data):
    if data.startswith(b'MESH08'):return {'accepted':False,'reason':'MESH08 requires its separate455loader'}
    if len(data)<2:raise ValueError('Short count')
    count=struct.unpack_from('<H',data)[0];at=2;records=[]
    for _ in range(count):
        if at+693>len(data):raise ValueError('Short693byte record')
        head=data[at:at+693];at+=693;vertices,faces,physiques=struct.unpack_from('<HHH',head,392);compact=struct.unpack_from('<I',head,642)[0]
        at+=vertices*28+faces*88
        if at>len(data):raise ValueError('Short geometry')
        bones=None
        if compact:
            if at+4>len(data):raise ValueError('Short compact bone count')
            bones=struct.unpack_from('<I',data,at)[0];at+=4
            if bones:at+=100*bones+40*physiques
        else:at+=424*physiques
        if at>len(data):raise ValueError('Short physique')
        records.append({'vertices':vertices,'faces':faces,'physiques':physiques,'compact':compact,'bones':bones})
    return {'accepted':at==len(data),'mesh_count':count,'extent':at,'trailing_bytes':len(data)-at,'records':records,'scope':'Bounded framing only,not complete geometry/skin/renderer semantics'}

def main():
    target=json.loads((WS/'config/client-target.json').read_text(encoding='utf-8'));reference=[];baseline=None
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        path=WS/f'work/client-reference/{folder}/RF_Online.bin';data=path.read_bytes()
        if sha(path)!=target[key]['sha256']:raise ValueError('Reference changed')
        functions=[];bodies=[]
        for name,va,size in [('convert_vertex64',0x93b020,0x31),('convert_uv64',0x93b5f0,0x17),('decode_physique64',0x93aa10,0x2c0),
            ('make_indexed_vertex',0x93b310,0x2db),('vertex64_to36',0x93b130,0x1c4),('mesh08_gate',0x91f250,0x4c),('mesh08_loader',0x922a00,0xe9b)]:
            body=read_va(data,va,size);bodies.append(body);functions.append({'name':name,'va':hex(va),'rva':hex(va-0x400000),'size':size,'sha256':hashlib.sha256(body).hexdigest()})
        if baseline is not None and bodies!=baseline:raise ValueError('Vertex/MSH08 bodies differ between reference pins')
        baseline=bodies
        # x87 FCHS and stores at normal+32,36,40; UV stores at44,48.
        for va,wanted in [(0x93b038,'d94010d9e0d95920'),(0x93b040,'d94014d9e0d95924'),(0x93b048,'d94018d9e0d95928'),(0x93b5f8,'d9582c'),(0x93b603,'d95830')]:
            if read_va(data,va,len(bytes.fromhex(wanted)))!=bytes.fromhex(wanted):raise ValueError('Vertex field instruction changed')
        for va,offset,char in [(0x91f274,0,'M'),(0x91f279,1,'E'),(0x91f27f,2,'S'),(0x91f285,3,'H'),(0x91f28b,4,'0'),(0x91f291,5,'8')]:
            expected=bytes([0x80,0x38,ord(char)]) if offset==0 else bytes([0x80,0x78,offset,ord(char)])
            if read_va(data,va,len(expected))!=expected:raise ValueError('MESH08 gate changed')
        for va,dest in [(0x9238f0,0x91f250),(0x923902,0x922a00)]:
            if read_va(data,va,5)!=b'\xe8'+struct.pack('<i',dest-va-5):raise ValueError('MESH08 client call changed')
        reference.append({'sha256':sha(path),'architecture':'x86','image_base':'0x400000','functions':functions,'confirmed_normal_sign':'x87 load/negate/store into normal+32/36/40','confirmed_magic':'MESH08 at first6bytes','confirmed_load_real_calls':['0x9238f0','0x923902']})
    old=[];inputs=json.loads((WS/'inventory/character-codeview.json').read_text(encoding='utf-8'))['objects'];obj=WS/inputs[6]['working_object'];records=coff_function_records(obj.read_bytes())
    if sha(obj)!=inputs[6]['sha256']:raise ValueError('Legacy vertex object changed')
    for symbol in BINDINGS:
        r=records[symbol];old.append({'symbol':symbol,'file_offset':r['file_offset'],'size':r['size'],'body_sha256':hashlib.sha256(r['bytes']).hexdigest(),'rva':None})
    root=WS/'work/client-reference/character-models';root.mkdir(parents=True,exist_ok=True)
    paths=json.loads((WS/'config/paths.json').read_text(encoding='utf-8'));client=Path(paths['client_455']);samples=[]
    for relative in ['item/Shield/Mesh/ACCRETIA_ARMOR_LSHIELD_031.msh','item/Shield/Mesh/ACCRETIA_ARMOR_LSHIELD_065.msh','item/Armor/Mesh/ACCRETIA_ARMOR_CLOAK_002.msh']:
        source=client/relative;copy=root/source.name;digest=sha(source)
        if copy.exists() and sha(copy)!=digest:raise ValueError('Preserving changed model copy')
        if not copy.exists():shutil.copyfile(source,copy)
        raw=copy.read_bytes();samples.append({'original_relative':relative,'copy':copy.relative_to(WS).as_posix(),'sha256':digest,'bytes':len(raw),'prefix_hex':raw[:16].hex(),'mesh08_prefix':raw.startswith(b'MESH08'),'legacy_framing':legacy_extent(raw)})
    report={'reference':reference,'legacy_object_sha256':sha(obj),'legacy_functions':old,'samples':samples,
        'confirmed':['Legacy source InitVertex/36byte vertices are a dependency restoration,not full455geometry behavior','455negates normals and uses64byte weighted/indexed/tangent vertex data','Actual reference LoadRealData detects MESH08 and uses a distinct loader;installed065sample has this header'],
        'unknown':['MESH08 full framing/material/texture/skin/vertex/index semantics and source implementation','All other installed model variants/complete model inventory','455packed5803byte mesh and GPU/D3D9pipeline;legacy source comparison does not certify them'],
        'raw_analysis':'artifacts/character-mesh-source/vertex-*.json and mesh08-*.json;owned IDAab009b3b/012583e5closed/save;no input EXE executed'}
    (WS/'inventory/character-init-reference.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('PASS:7vertex/MSH08bodies,normal/UV/magic instructions and2caller edges match both pinned455PE;3model samples pinned.')

if __name__=='__main__':main()
