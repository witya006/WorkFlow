"""Pin renderer owner/device/lifetime bodies and preserve constructor write masks."""
import hashlib,json,struct
from compare_client_binaries import WS
from build_client455_x87_math import read_va

def sha(data):return hashlib.sha256(data).hexdigest()
def main():
    pins=json.loads((WS/'config/client-target.json').read_text(encoding='utf-8'));refs=[];previous=None;constants=None
    functions=[('interface_create',0x5dfa80,0xce),('owner_ctor',0x5dfb70,0xcd),('renderer_defaults',0x91c8f0,0x106),('bind_device',0x920590,0xd6),('interface_bind_thunk',0x931300,5),('owner_dtor',0x9228a0,0x157),('effect_manager_dtor',0x922730,0xb9),('shader_set_device',0x939b70,9),('manager_ctor',0x5dfe60,0x6e),('texture_ctor',0x5dfc40,0x69),('effect_ctor',0x5e7e90,0x30)]
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        raw=(WS/f'work/client-reference/{folder}/RF_Online.bin').read_bytes()
        if sha(raw)!=pins[key]['sha256']:raise ValueError('Changed455')
        bodies=[{'name':name,'rva':hex(at-0x400000),'bytes':n,'sha256':sha(read_va(raw,at,n))} for name,at,n in functions]
        log=read_va(raw,0xb3a7ec,256);wide=read_va(raw,0xb3a804,512);end=next(i for i in range(0,512,2) if wide[i:i+2]==b'\0\0')+2;warning=wide[:end]
        data=(log,warning,read_va(raw,0xaaa4d8,4),read_va(raw,0xaa8c38,4))
        if previous is not None and (previous!=bodies or constants!=data):raise ValueError('Owner bodies/constants differ')
        previous=bodies;constants=data;refs.append({'sha256':sha(raw),'architecture':'x86','image_base':'0x400000','functions':bodies,'log_literal_rva':'0x73a7ec','warning_rva':'0x73a804','warning_bytes':len(warning)})
    log,warning,diffuse,direction=constants
    header='#pragma once\n// Literal bytes copied by920590;the256-byte copy includes adjacent constants.\nstatic const unsigned char RF455_RENDERER_LOG_PATH[256]={'+','.join(f'0x{b:02x}' for b in log)+'};\nstatic const wchar_t RF455_RENDERER_BLEND_WARNING[]={'+','.join(hex(v) for v in struct.unpack('<'+'H'*(len(warning)//2),warning))+'};\n'
    (WS/'scripts/native/client455_renderer_owner_constants.h').write_text(header,encoding='ascii')
    image=bytearray([0xa5]*0x8440);mask=bytearray(0x8440)
    def put(at,value):image[at:at+len(value)]=value;mask[at:at+len(value)]=bytes([255])*len(value)
    def zero(at,n):put(at,bytes(n))
    # Child constructor writes established by their separately recovered bodies.
    for at in [116,4264]:zero(at+4,16);zero(at+148,4000)
    zero(8424+8,12);zero(8424,4);zero(8424+20,4);put(8424+24,struct.pack('<I',1));zero(8424+28,1);zero(8424+284,4)
    zero(8712+4,12)
    for at in [8928,17128,25328]:zero(at,8200)
    zero(8,104)
    # Full91C8F0 writes,including bytes not assigned by the child constructors.
    for at in [0,4,112,8728,33840,8416]:zero(at,4)
    for at in [8732,8832,8420]:zero(at,1)
    put(8,struct.pack('<I',3))
    for at in [12,16,20]:put(at,diffuse)
    for at in [44,48,52]:put(at,struct.pack('<f',1))
    zero(72,8);put(80,direction);zero(8836,84);put(33528,struct.pack('<I',2))
    root=WS/'work/client-reference/renderer-owner455';root.mkdir(parents=True,exist_ok=True);golden=b'RO45'+struct.pack('<II',1,len(image))+image+mask;path=root/'constructor.bin';path.write_bytes(golden)
    report={'scope':'Renderer storage construction,borrowed device/sharedshader bootstrap gate andnormal destruction;not complete455engine integration','references':refs,'constructor_bytes':len(image),'written_bytes':sum(bool(v) for v in mask),'golden':path.relative_to(WS).as_posix(),'golden_sha256':sha(golden),'script_sha256':sha((WS/'scripts/audit_client455_renderer_owner.py').read_bytes()),'constants_header_sha256':sha(header.encode('ascii')),'device_contract':['GetDeviceCaps HRESULT ignored;old caps retained onfailed untouched result','MaxVertexBlendMatrices2or4 overwritesmode;other values retain previousmode','Shared shaderdevice gate prevents bootstrap/rebind whenalready nonnull','Device borrows includeowner,texturemanager,andthreepools;noAddRef'],'limits':['No original process/unwind/device-reset/errorUI/allocatorfailure equivalence','Missing shadererror callback returns init failure rather thanoriginal loggerresult;failure diagnostics pending','Opaque fields preserved;layout doesnotprovide unimplemented methods orpermitold-new casts']}
    (WS/'inventory/client455-renderer-owner-reference.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(f'PASS:11owner ranges bothpins;constructor footprint{sum(bool(v) for v in mask)}/{len(image)}bytes')
if __name__=='__main__':main()
