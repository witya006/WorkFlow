"""Pin455mesh construction/header/material control flow and matrix dependency."""
import hashlib,json,struct
from pathlib import Path
from compare_client_binaries import WS,pe
from build_client455_x87_math import read_va

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def import_slots(data):
    image=pe(data);base=image['image_base'];header=struct.unpack_from('<I',data,0x3c)[0]
    rva,size=struct.unpack_from('<II',data,header+24+104);slots={}
    def string(rva):return read_va(data,base+rva,128).split(b'\0',1)[0].decode('ascii')
    for at in range(rva,rva+size,20):
        original,_,_,name,table=struct.unpack('<5I',read_va(data,base+at,20))
        if not any((original,name,table)):break
        dll=string(name).lower();lookup=original or table;n=0
        while (item:=struct.unpack('<I',read_va(data,base+lookup+4*n,4))[0]):
            if not item&0x80000000:slots[base+table+4*n]={'dll':dll,'name':string(item+2)}
            n+=1
    return slots
def main():
    target=json.loads((WS/'config/client-target.json').read_text(encoding='utf-8'));references=[];baseline=None
    for folder,key in [('current','behavior_reference'),('reference-backup','secondary_reference')]:
        source=WS/f'work/client-reference/{folder}/RF_Online.bin';data=source.read_bytes()
        if sha(source)!=target[key]['sha256']:raise ValueError('Pinned455binary changed')
        functions=[];bodies=[]
        for name,va,size in [('mesh_constructor',0x9214e0,0x1c2),('overwritten_subobject_constructor',0x920e40,0xde),('mesh08_loader',0x922a00,0xe9b),('texture_lookup',0x934120,0x144),('texture_load',0x934a20,0x33d)]:
            body=read_va(data,va,size);bodies.append(body);functions.append({'name':name,'va':hex(va),'rva':hex(va-0x400000),'size':size,'sha256':hashlib.sha256(body).hexdigest()})
        if baseline is not None and baseline!=bodies:raise ValueError('Mesh runtime bodies differ betweenpins')
        baseline=bodies;imports=import_slots(data);matrix=[]
        for va,name in [(0x854130,'D3DXMatrixInverse'),(0x85412a,'D3DXMatrixMultiply')]:
            thunk=read_va(data,va,6)
            if thunk[:2]!=b'\xff\x25':raise ValueError('Matrix import thunk changed')
            slot=struct.unpack_from('<I',thunk,2)[0];resolved=imports[slot]
            if resolved!={'dll':'d3dx9_36.dll','name':name}:raise ValueError('Unexpected matrix dependency')
            matrix.append({'va':hex(va),'rva':hex(va-0x400000),'iat_va':hex(slot),'iat_rva':hex(slot-0x400000),'bytes':thunk.hex(),**resolved})
        if read_va(data,0xb369b0,4)!=bytes.fromhex('0000804f'):raise ValueError('Unsigned x87 bias changed')
        references.append({'sha256':sha(source),'architecture':'x86','image_base':'0x400000','functions':functions,'matrix_imports':matrix,'unsigned_bias':{'va':'0xb369b0','rva':'0x7369b0','bytes':'0000804f'}})
    paths=json.loads((WS/'config/paths.json').read_text(encoding='utf-8'));inputDll=Path(paths['client_455'])/'d3dx9_36.dll';systemDll=Path('C:/Windows/SysWOW64/d3dx9_36.dll')
    expectedDll='c12f0ab0338eb5031d3d04beaf7208ac848f7e037d21ff963d2af90221cbe935'
    if sha(inputDll)!=expectedDll or sha(systemDll)!=expectedDll:raise ValueError('D3DX9provider differs fromverified client-local/system DLL')
    pe(systemDll.read_bytes())
    report={'reference':references,'matrix_provider':{'path':str(systemDll),'input_relative':'d3dx9_36.dll','sha256':sha(systemDll),'bytes':systemDll.stat().st_size,'architecture':'x86','file_version':'9.19.949.2111','publisher_verification':'PowerShell Get-AuthenticodeSignature onbyte-identical input:Valid,Microsoft Corporation'},
        'confirmed':['Constructor final state:whole5803zero,four1.0 fields,nine-1fields,cumulative count/byte accounting;preceding subobject writes overwritten','Header copies200/264/328matrices;inverse328 times200 withrow translation forced0;separate inverse200','Unsigned598 uses x87 signedFILD plus2^32 onnegative thenFSTP;6float copies also use x87','Primary basename lowercased ininput;NOR/SEQ/REF inserted beforefirst.dds;all4load requests only onprimary cache miss;secondary retains case andleading-only backslash','Object texture directory ifnonempty,otherwise manager fallback;missing texture IDs stay0'],
        'limits':['Source metadata/material control flow,not full normal loader/texture cache/GPU provider','Matrix implementation remains pinned Microsoft D3DX9runtime dependency;no inputEXE executed','Source errors forbad names/primary path/singular inverse differ fromunchecked reference failures','Unmasked exceptions/non-ASCII CRT locale/OOM/full constructor owning methods/destructor andGPU publication remain open'],
        'raw_analysis':'artifacts/character-mesh08/runtime-instructions.json/runtime-0x934120.json/runtime-0x934a20.json/runtime-0x920e40.json;cached607line922A00 and55line9214E0;owned IDA716ae4faclosed/save'}
    (WS/'inventory/client455-mesh-runtime-reference.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('PASS:5mesh runtime bodies match bothpins;matrix thunks resolve toD3DX9_36;installed x86DLL equals signed Microsoft client-local DLL.')
if __name__=='__main__':main()
