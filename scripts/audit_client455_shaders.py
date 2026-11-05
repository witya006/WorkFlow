"""Pin Character shader bootstrap, decode only its twelve installed programs."""
import hashlib,json
from pathlib import Path
from compare_client_binaries import WS
from build_client455_x87_math import read_va
def sha(data):return hashlib.sha256(data).hexdigest()
NAMES=['sh_basic','sh_normal','sh_norm_spec','sh_shadow','sh_basic_Bump','sh_basic_BumpEffect','sh_basic_Scroll','sh_basic_DScroll','sh_basic_EnvScroll','sh_basic_GradeEffect','sh_basic_GradeEnvEffect','sh_basic_alpha']
def sections(decoded):
    visible=decoded.split(b'\0',1)[0];v=visible.find(b'[vertex shader]');p=visible.find(b'[pixel shader]');data=bytearray(visible)+b'\0';starts=[]
    for at,length in [(v,15),(p,14)]:
        if at<0:starts.append(None);continue
        data[at]=0;at+=length
        while data[at] in [10,13]:at+=1
        starts.append(at)
    result=[]
    for at in starts:result.append(None if at is None else bytes(data[at:data.index(0,at)]))
    return result
def main():
    target=json.loads((WS/'config/client-target.json').read_text(encoding='utf-8'));refs=[];last=None;key=None
    ranges=[('character_shader_bootstrap',0x91fd40,0x2d2),('program_append',0x939bb0,0x6d),('program_release',0x939d00,0xdc),('manager_ctor_prefix',0x93a160,0x1e),('manager_dtor',0x93a1f0,0xa5),('compile_program',0x93a350,0x34a),('file_dispatch_decode',0x93a6a0,0x24e),('load_wrapper',0x93a8f0,0x16),('strip_last_extension',0x93a9d0,0x33)]
    for folder,label in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        raw=(WS/f'work/client-reference/{folder}/RF_Online.bin').read_bytes()
        if sha(raw)!=target[label]['sha256']:raise ValueError('Changed455')
        currentKey=read_va(raw,0xb39918,134)+bytes(3)
        if key is not None and key!=currentKey:raise ValueError('Shader keys differ')
        key=currentKey;bodies=[{'name':n,'rva':hex(at-0x400000),'bytes':size,'sha256':sha(read_va(raw,at,size))} for n,at,size in ranges]
        if last is not None and last!=bodies:raise ValueError('Shader bootstrap bodies differ')
        last=bodies;refs.append({'sha256':sha(raw),'architecture':'x86','image_base':'0x400000','functions':bodies,'key_rva':'0x739918','key_sha256':sha(key)})
    header=('#pragma once\nstatic const unsigned char RF455_SHADER_KEY[137]={'+','.join('0x%02x'%value for value in key)+'};\n').encode('ascii');path=WS/'scripts/native/client455_shader_key.h'
    if path.exists() and path.read_bytes()!=header:raise ValueError('Preserving changed generated shader key')
    if not path.exists():path.write_bytes(header)
    original=Path(json.loads((WS/'config/paths.json').read_text(encoding='utf-8'))['client_455'])/'System/shader';files={p.name.lower():p for p in original.iterdir() if p.is_file()};root=WS/'work/client-reference/shaders455';root.mkdir(parents=True,exist_ok=True);records=[]
    for name in NAMES:
        source=files[(name+'.sho').lower()];raw=source.read_bytes();decoded=bytes(value^key[i%137] for i,value in enumerate(raw));vertex,pixel=sections(decoded)
        if (vertex is None and pixel is None) or any(b'main' not in stage for stage in [vertex,pixel] if stage is not None):raise ValueError('Missing shader stages:'+name+':'+repr(decoded[:96]))
        copy=root/(name+'.sho');plain=root/(name+'.decoded.txt')
        for p,data in [(copy,raw),(plain,decoded)]:
            if p.exists() and p.read_bytes()!=data:raise ValueError('Preserving changed shader fixture')
            if not p.exists():p.write_bytes(data)
        records.append({'name':name,'original':source.relative_to(original.parent.parent).as_posix(),'copy':copy.relative_to(WS).as_posix(),'sha256':sha(raw),'bytes':len(raw),'decoded':plain.relative_to(WS).as_posix(),'decoded_sha256':sha(decoded),'vertex_sha256':sha(vertex) if vertex is not None else None,'vertex_bytes':len(vertex) if vertex is not None else 0,'pixel_sha256':sha(pixel) if pixel is not None else None,'pixel_bytes':len(pixel) if pixel is not None else 0})
    report={'scope':'Pinned Character shader resource bootstrap,not full renderer/normal integration','references':refs,'programs':records,'compile':{'entry':'main','vertex_profile':'vs_2_0','pixel_profile':'ps_3_0','flags':'0x8008','defines':None,'include':None},'key_header_sha256':sha(header),'script_sha256':sha((WS/'scripts/audit_client455_shaders.py').read_bytes()),'raw_analysis':'artifacts/character-animation455/render-*.json/renderer-start-*.json;owned95159529 closed/save','remaining':['Full Character draw/state/constants andnormal typedconsumer migration','Invalid input/compile failure resource behavior/UI equivalence','Old ChAnimation name4/ID260 versus455 name5/ID264 prevents isolatedmanager swap']}
    (WS/'inventory/client455-shaders-reference.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('PASS:9pinned shader ranges/12real SHO;source profiles andflags pinned');print([(p['name'],p['vertex_bytes'],p['pixel_bytes']) for p in records])
if __name__=='__main__':main()
